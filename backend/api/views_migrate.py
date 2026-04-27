from django.http import JsonResponse
from django.core.management import call_command
from django.conf import settings

def run_migrations(request):
    token = request.GET.get("token")
    if token != settings.MIGRATION_SECRET:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    call_command("migrate")
    return JsonResponse({"status": "migrations applied"})