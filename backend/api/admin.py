from django.contrib import admin, messages
from .models import ChatTelemetry, KnowledgeBase
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