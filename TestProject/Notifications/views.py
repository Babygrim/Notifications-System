from .models import *
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from itertools import chain

# Create your views here.
def getUserNotifications(request, id):
    req_page = int(request.GET.get('page', 1))
    story_commented_note = UserStoryCommentedNotification.objects.filter(receiver=id)
    comment_replied_note = UserCommentRepliedNotification.objects.filter(receiver=id)
    administrative_note = AdministrativeOverallNotifications.objects.all()
    
    for elem in administrative_note:
        if elem.is_created_today():
            elem.delete()

    model_combination = list(chain(administrative_note, story_commented_note, comment_replied_note))
    
    paginated_stories = Paginator(model_combination, per_page=6)
    get_page = paginated_stories.get_page(req_page)
    
    payload = [elem.serialize() for elem in get_page.object_list]

    response = {
            "page": {
                "current": get_page.number,
                "has_next": get_page.has_next(),
                "has_previous": get_page.has_previous(),
                "overall": paginated_stories.count,
            },
            "notifications": payload
    }
    
    return JsonResponse({"data":response}, safe=False)


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
        