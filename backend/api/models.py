from django.db import models

# defined normally using Django models
class ChatMessage(models.Model): # chat storage model via Postgres
    session_id = models.CharField(max_length=100)
    user_query = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

# model for tracking what's in the db
class Document(models.Model):
    title = models.CharField(max_length=255)
    source_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


