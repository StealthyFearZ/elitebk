from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.rag_service import generate_answer
from .services.dataset_manager import update_dataset

class ChatAnswerView(APIView):
    def post(self, request): # DRF version of Django's `if request.method == "POST"`
        query = request.data.get("question")
        if not query: # no query
            return Response({"error":"Question is required"}, status=400)
        result = generate_answer(query)

        # save to database if necessary via ChatMessage model

        return Response({
            "answer": result["answer"],
            "sources": result["sources"]
        })

def update_dataset_view(request):
    league_id = '4328'  # English Premier League ID
    season = '2022-2023'
    update_dataset(league_id, season)
    return HttpResponse("Dataset updated successfully.")