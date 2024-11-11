from .models import *
from django.http import JsonResponse
from Authentication.models import BaseUserProfile, SubscriptionTimeStampThrough
from django.core.paginator import Paginator
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response

#Fetch profile notifications
class GetNotifications(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
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
                    subscr = UserStoryCreatedNotification.objects.filter(creator = subscription).exclude(created__lt = subscr_information.when_subscribed).exclude(id__in = sc_ids)
                    story_created_note += list(subscr)
                
        comment_replied_note = UserCommentRepliedNotification.objects.filter(receiver = base_user).exclude(id__in=cr_ids)    
        
        model_combination += list(story_created_note)
        model_combination += list(comment_replied_note)
        
        sorted_model_combination = sorted(model_combination, key=lambda obj: obj.created, reverse=True)
        
        paginated_stories = Paginator(sorted_model_combination, per_page=10)
        get_page = paginated_stories.get_page(req_page)
        
        payload = [elem.serialize() for elem in get_page.object_list]

        response = {
                "page": {
                    "current": get_page.number,
                    "total": paginated_stories.num_pages,
                    "has_next": get_page.has_next(),
                    "has_previous": get_page.has_previous(),
                },
                "data": payload
        }
        
        return Response({"success": True, "data": response, "message": ""})

#Mark profile notifications as Read
class MarkAsRead(APIView):
    authentication_classes = (JWTAuthentication, )
    permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        base_user = BaseUserProfile.objects.get(user = request.user)
        mark = MarkedAsRead.objects.get(user = base_user)
        
        data = request.data 
        note_type = data.get('type', None)
        note_id = data.get('note_id', None)
        
        if note_type == None or note_id == None:
            return Response({"success": False, "data": {}, "message": "request body missing type (type can should be 'sc', 'scom', 'cr', 'ao') or note_id"})
        
        if note_type == "sc":
            notification_obj = UserStoryCreatedNotification.objects.get(pk = int(note_id))
            if notification_obj not in mark.notifications_sc.all():
                mark.notifications_sc.add(notification_obj)
            else:
                return Response({"success": False, "data": {}, "message": "Notification is already marked as read."})
        elif note_type == "scom":
            notification_obj = UserStoryCommentedNotification.objects.get(pk = int(note_id))
            if notification_obj not in mark.notifications_scom.all():
                mark.notifications_scom.add(notification_obj)
            else:
                return Response({"success": False, "data": {}, "message": "Notification is already marked as read."})
        elif note_type == "cr":
            notification_obj = UserCommentRepliedNotification.objects.get(pk = int(note_id))
            if notification_obj not in mark.notifications_cr.all():
                mark.notifications_cr.add(notification_obj)
            else:
                return Response({"success": False, "data": {}, "message": "Notification is already marked as read."})
        elif note_type == "ao":
            notification_obj = AdministrativeOverallNotifications.objects.get(pk = int(note_id))
            if notification_obj not in mark.notifications_ao.all():
                mark.notifications_ao.add(notification_obj)
            else:
                return Response({"success": False, "data": {}, "message": "Notification is already marked as read."})
        else:
            return Response({"success": False, "data": {}, "message": "Invalid type (type can should be 'sc', 'scom', 'cr', 'ao')"})
        
        mark.save()
        return Response({"success": True, "data": {}, "message": "Notification marked as read. (If user didn't have notification with that ID in a first place - this does no good no harm)"})
    
            
        