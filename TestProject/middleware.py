from django.http import JsonResponse
from rest_framework import status
from django.conf import settings

class Custom404Middleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request URL is for media files
        if request.path.startswith(settings.MEDIA_URL):
            return self.get_response(request)

        response = self.get_response(request)

        # Check for a 404 response for non-media URLs
        if response.status_code == 404:
            return JsonResponse(
                {"detail": "The requested URL does not exist"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return response