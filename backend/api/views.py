import os
from django.http import JsonResponse, StreamingHttpResponse
import time
from .models import ChatMessage
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.authtoken.models import Token
from .services.rag_service import generate_answer
from .services.report_service import generate_report_content, build_pdf, encode_pdf
from .services.prediction_service import (
    build_xlsx_bytes,
    detect_teams_in_text,
    encode_xlsx,
    generate_predicted_rows,
)
from .services.dataset_manager import update_dataset, update_dataset_from_json
from django.contrib.auth.models import User
from .models import UserProfile
from .services.telemetry import track_chat_performance
import json

DATASET_FOLDER = os.path.join(os.path.dirname(__file__), "../dataset")


class IsDeveloper(BasePermission):
    # Will check if the user is authenticated --> then check if the user is a developer
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and hasattr(request.user, 'profile')
            and request.user.profile.role == 'developer'
        )


class ChatAnswerView(APIView):
    @track_chat_performance(endpoint_name="Generate Chatbot Response")
    def post(self, request):
        query = request.data.get("question")
        # ADded error detection for submitting empty question
        if not query:
            return Response({"error": "Question is required"}, status=400)
        start_time = time.time() # stores time before generating answer
        result = generate_answer(query)
        result_response_time = int((time.time() - start_time)) # uses time before generation to calculate change in time as the response time
        detected_team, detected_opponent = detect_teams_in_text(query)

        ChatMessage.objects.create( # adds another value to the ChatMessage model for each 
            session_id = request.data.get("session_id", "default_session"), # gets the id of the session it was called in
            user_query = query,
            ai_response = result['answer'],
            intent = result.get('intent'),
            response_time = result_response_time
        )

        return Response({
            "answer": result["answer"],
            "sources": result["sources"],
            "detected_team": detected_team,
            "detected_opponent": detected_opponent,
        })


class GenerateReportView(APIView):
    def post(self, request):
        # Find question
        question = request.data.get("question")
        #get answer
        answer = request.data.get("answer")
        #get sources
        sources = request.data.get("sources", [])

        if not question or not answer:
            return Response({"error": "question and answer are required"}, status=400)

        try:
            # Call the generate report function
            report_data = generate_report_content(question, answer, sources)
        except ValueError as e:
            return Response({"error": str(e)}, status=500)

        # Now build the pdf report
        pdf_bytes = build_pdf(report_data, question)
        return Response({
            "preview": {
                "overview": report_data["overview"],
                "key_statistics": report_data["key_statistics"],
            },
            "pdf_base64": encode_pdf(pdf_bytes),
        })


class PredictLineupView(APIView):
    def post(self, request):
        team = request.data.get("team")
        opponent = request.data.get("opponent")
        question = request.data.get("question", "")

        if not team:
            return Response({"error": "team is required"}, status=400)

        try:
            prediction = generate_predicted_rows(team=str(team), opponent=str(opponent) if opponent else None, question=str(question))
            rows = prediction["rows"]
            xlsx_bytes = build_xlsx_bytes(rows)
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({
            "team": team,
            "opponent": opponent,
            "notes": prediction.get("notes", ""),
            "table": rows,
            "xlsx_base64": encode_xlsx(xlsx_bytes),
        })


class LoginView(APIView):
    # Added a login view for either an enduser or developer to log in
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        # Error detection for username / password empty
        if not username or not password:
            return Response({"error": "Username and password required"}, status=400)

        # Authenticates the user
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        token, _ = Token.objects.get_or_create(user=user)
        role = user.profile.role if hasattr(user, 'profile') else 'end_user'
        return Response({
            "token": token.key,
            "username": user.username,
            "role": role,
        })

# Register View
class RegisterView(APIView):
    permission_classes = [AllowAny]
    # use to get username / password / role
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role")
        
        #error message
        if not username or not password or not role:
            return Response({"error": "Username, password, and role are required"}, status=400)

        #incorrect rule
        if role not in (UserProfile.DEVELOPER, UserProfile.END_USER):
            return Response({"error": "Invalid role"}, status=400)
        #Existing username error
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already taken"}, status=400)

        user = User.objects.create_user(username=username, password=password) # make user
        UserProfile.objects.create(user=user, role=role)
        token = Token.objects.create(user=user) #give token here

        return Response({"token": token.key, "username": user.username, "role": role}) # return the token


class UploadContextView(APIView):
    # Gives the developer the option to upload a JSON as new context --> my user story...
    permission_classes = [IsDeveloper]

    def post(self, request):
        uploaded_file = request.FILES.get('file')
        # Empty file
        if not uploaded_file:
            return Response({"error": "No file provided"}, status=400)

        # Checks that it is a JSON file
        if not uploaded_file.name.endswith('.json'):
            return Response({"error": "Only JSON files are supported"}, status=400)

        os.makedirs(DATASET_FOLDER, exist_ok=True)

        from datetime import datetime
        # Need this for saving the JSON in our datatbase
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"upload_{timestamp}.json"
        save_path = os.path.join(DATASET_FOLDER, filename)

        with open(save_path, 'wb') as f:
            for chunk in uploaded_file.chunks():
                f.write(chunk)

        try:
            list(update_dataset_from_json())
            return Response({"message": "Dataset uploaded and updated successfully."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


def update_dataset_view(request):
    source = request.GET.get("source", "json")
    season = request.GET.get("season", "2024")
    max_players = int(request.GET.get("max_players", "50"))

    def progress_generator():
        try:
            # Send initial message
            yield f"data: {json.dumps({'message': 'Starting dataset update...', 'status': 'processing'})}\n\n"

            record_count = None
            progress_messages = []

            # Iterate through the generator to get progress messages
            dataset_generator = update_dataset(season, source=source, max_players=max_players)
            for message in dataset_generator:
                if isinstance(message, str):
                    progress_messages.append(message)
                    yield f"data: {json.dumps({'message': message, 'status': 'processing', 'progress': progress_messages})}\n\n"
                else:
                    record_count = message

            # Send completion message
            response_data = {
                "message": f"Dataset updated successfully from {source} for season {season}.",
                "status": "completed",
                "progress": progress_messages
            }
            if record_count is not None:
                response_data["records_ingested"] = record_count

            yield f"data: {json.dumps(response_data)}\n\n"

        except Exception as e:
            yield f"data: {json.dumps({'error': str(e), 'status': 'error'})}\n\n"

    response = StreamingHttpResponse(
        progress_generator(),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    return response