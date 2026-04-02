from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .services.rag_service import generate_answer

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