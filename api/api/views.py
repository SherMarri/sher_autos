from django.http import HttpRequest, JsonResponse


def get_status(request: HttpRequest):
    return JsonResponse({"status": "ok"})
