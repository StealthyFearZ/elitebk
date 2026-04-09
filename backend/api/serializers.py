from rest_framework import serializers

class ChatQuerySerializer(serializers.Serializer): #serializers convert complex data such as model instances into a format that is more comprehensible by Python
    question = serializers.CharField() # actual question
    conversation_id = serializers.CharField(required=False, allow_blank=True)
    top_k = serializers.IntegerField(required=False, default=4, min_value=1, max_value=10) # Sampling parameter value that controls randomness of text/restricts tokens selection