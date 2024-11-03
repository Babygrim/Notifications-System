from django.http import JsonResponse
from rest_framework import status

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Check for a 404 response and if the request is for JSON (e.g., API endpoint)
        if response.status_code == 404:
            return JsonResponse(
                {"detail": "The requested URL does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        return response