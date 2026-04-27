from django.http import JsonResponse
from django.core.management import call_command
from django.conf import settings

def run_migrations(request):
    token = request.GET.get("token")
    if settings.MIGRATION_SECRET and token != settings.MIGRATION_SECRET:    # skip check if missing
        return JsonResponse({"error": "Unauthorized"}, status=401)

    call_command("migrate")
    return JsonResponse({"status": "migrations applied"})