from .models import *
from django.http import JsonResponse
from Authentication.models import BaseUserProfile, SubscriptionTimeStampThrough
from django.core.paginator import Paginator
from itertools import chain
import json
from operator import attrgetter

# Create your views here.
def getUserNotifications(request):
    if request.method == "GET":
        if request.user:
            req_page = int(request.GET.get('page', 1))
            
            administrative_note = list()
            story_commented_note = list()
            story_created_note = list()
            comment_replied_note = list()
            
            model_combination = None
            base_user = BaseUserProfile.objects.get(user = request.user)
            try:
                mark = MarkedAsRead.objects.get(user = base_user)
            except MarkedAsRead.DoesNotExist:
                mark = MarkedAsRead(user = base_user)
                mark.save()
            
            ao_ids = mark.notifications_ao.values_list('id', flat=True)
            cr_ids = mark.notifications_cr.values_list('id', flat=True)
            sc_ids = mark.notifications_sc.values_list('id', flat=True)
            scom_ids = mark.notifications_scom.values_list('id', flat=True)
            
            
            
            administrative_note = AdministrativeOverallNotifications.objects.all().exclude(id__in = ao_ids)
            model_combination = list(administrative_note)
            
            # writers notes
            if base_user.writer:
                story_commented_note = UserStoryCommentedNotification.objects.filter(receiver = base_user.writer).exclude(id__in=scom_ids)
                model_combination += list(story_commented_note)
            
            # readers notes
            subscribed_to = base_user.reader.subscribed_to.all()
            if subscribed_to.count() > 0:
                story_created_note = list()
                for subscription in subscribed_to:
                    subscr_information = SubscriptionTimeStampThrough.objects.get(reader = base_user.reader, writer = subscription)
                    if subscr_information.receive_notifications:
                        subscr = UserStoryCreatedNotification.objects.filter(creator = subscription).exclude(created_at__lt = subscr_information.when_subscribed).exclude(id__in = sc_ids)
                        story_created_note += list(subscr)
                    
            comment_replied_note = UserCommentRepliedNotification.objects.filter(receiver = base_user).exclude(id__in=cr_ids)    
            
            model_combination += list(story_created_note)
            model_combination += list(comment_replied_note)
            
            sorted_model_combination = sorted(model_combination, key=lambda obj: obj.created_at, reverse=True)
            
            paginated_stories = Paginator(sorted_model_combination, per_page=5)
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
        else:
            return JsonResponse({"data":"not logged"}, safe=False)

def MarkAsRead(request):
    if request.method == "POST":
        base_user = BaseUserProfile.objects.get(user = request.user)
        mark = MarkedAsRead.objects.get(user = base_user)
        
        data = json.loads(request.body)
        
        note_type = data.get('type')
        note_id = int(data.get('note_id'))
        
        if note_type == "sc":
            notification_obj = UserStoryCreatedNotification.objects.get(pk = note_id)
            mark.notifications_sc.add(notification_obj)
        if note_type == "scom":
            notification_obj = UserStoryCommentedNotification.objects.get(pk = note_id)
            mark.notifications_scom.add(notification_obj)
        if note_type == "cr":
            notification_obj = UserCommentRepliedNotification.objects.get(pk = note_id)
            mark.notifications_cr.add(notification_obj)
        if note_type == "ao":
            notification_obj = AdministrativeOverallNotifications.objects.get(pk = note_id)
            mark.notifications_ao.add(notification_obj)
        
        mark.save()
        
        return JsonResponse({"message":"success"})
            
        