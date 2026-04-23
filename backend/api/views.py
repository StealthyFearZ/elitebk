import os
from django.http import JsonResponse
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework.authtoken.models import Token
from .services.rag_service import generate_answer
from .services.report_service import generate_report_content, build_pdf, encode_pdf
from .services.dataset_manager import update_dataset, update_dataset_from_json
from django.contrib.auth.models import User
from .models import UserProfile

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
    def post(self, request):
        query = request.data.get("question")
        # ADded error detection for submitting empty question
        if not query:
            return Response({"error": "Question is required"}, status=400)
        result = generate_answer(query)
        return Response({
            "answer": result["answer"],
            "sources": result["sources"]
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
            update_dataset_from_json()
            return Response({"message": "Dataset uploaded and updated successfully."})
        except Exception as e:
            return Response({"error": str(e)}, status=500)


def update_dataset_view(request):
    season = 2024
    # More debugging / error detection statements to help figure out wahts wrong rn...
    try:
        update_dataset(season)
        return JsonResponse({"message": "Dataset updated successfully."})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)