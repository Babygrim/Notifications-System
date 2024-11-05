from rest_framework import permissions
from Authentication.models import BaseUserProfile

class IsAuthenticatedWriter(permissions.BasePermission):
    """
    Custom permission that only allows authenticated users with a writer profile
    to access the endpoint with the POST method.
    """
    message = "Only users with writer profiles are allowed to create or update (their own) posts."

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user or not request.user.is_authenticated:
            return False

        # Check if the user has a writer profile
        # Assuming 'UserProfileWriter' is the model linked to a writer profile
        user = BaseUserProfile.objects.get(user = request.user)
        if user.writer != None:
            return True
        
        #return hasattr(request.user, 'writer')  # Adjust to your model setup
        