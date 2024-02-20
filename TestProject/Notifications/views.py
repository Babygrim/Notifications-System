from .models import *
from django.http import JsonResponse
import json

# Create your views here.
def getUserNotifications(request, id):
    story_commented_note = UserStoryCommentedNotification.objects.filter(receiver=id)
    comment_replied_note = UserCommentRepliedNotification.objects.filter(receiver=id)
    
    return JsonResponse({"story": [elem.serialize() for elem in story_commented_note], "comment": [elem.serialize() for elem in comment_replied_note]})


def MarkAsRead(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        if data['type'] == "story":
            to_delete = UserStoryCommentedNotification.objects.get(pk=data['note_id'])
            to_delete.delete()
            
        else:
            to_delete = UserCommentRepliedNotification.objects.get(pk=data['note_id'])
            to_delete.delete()
        
        return JsonResponse({"message": "Success"})
        