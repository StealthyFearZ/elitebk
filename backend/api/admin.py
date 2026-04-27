from django.contrib import admin, messages
from .models import ChatTelemetry, KnowledgeBase, ChatMessage
from .services.vector_store import clear_vectorstore

@admin.register(ChatTelemetry)
class ChatTelemetryAdmin(admin.ModelAdmin):
    list_display = ('endpoint', 'is_success', 'latency_display', 'created_at', 'user')
    list_filter = ('is_success', 'endpoint', 'created_at')
    search_fields = ('error_message', 'endpoint')
    readonly_fields = ('endpoint', 'latency_display', 'is_success', 'error_message', 'created_at', 'user')

    @admin.display(description='Latency')
    def latency_display(self, obj):
        if obj.latency_ms is None:
            return "N/A"
        if obj.latency_ms >= 1000:
            return f"{obj.latency_ms / 1000:.3f} s"
        return f"{obj.latency_ms:.0f} ms"

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    # Same format used from ChatTelemetryAdmin
    list_display = ('id', 'user_query', 'intent', 'response_time', 'created_at') # how all fields should be displayed
    list_filter = ('intent', 'created_at') # filters for the displaying of each of the objects
    search_fields = ('user_query', 'intent', 'ai_response') # what should be searchable from a list of recorded ChatMessage objects
    readonly_fields = ('session_id', 'user_query', 'ai_response', 'intent', 'response_time', 'created_at') # fields that should only have values that can be read, not edited

    ordering = ['-created_at'] # order the list of items by descending order of object creation, most recent to oldest

    def __str__(self): # String representation
        return f"{self.user_query[:50]} - Created At: {self.created_at} | Response Time: {self.response_time} | Intent: {self.intent} | Session ID: {self.session_id}" # string rep

# add action to clear the chatbot knowledge base
@admin.register(KnowledgeBase)
class KnowledgeBaseAdmin(admin.ModelAdmin):
    actions = ["clear_kb"]

    @admin.action(description="Clear the chatbot knowledge base")
    def clear_kb(self, request, queryset):
        try:
            clear_vectorstore()
            self.message_user(request, "Knowledge base cleared successfully!", level=messages.SUCCESS)
        except Exception as e:
            self.message_user(request, f"Error clearing knowledge base: {e}", level=messages.ERROR)

