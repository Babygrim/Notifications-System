from .models import UserStoryCreatedNotification, UserStoryCommentedNotification, UserCommentRepliedNotification, AdministrativeOverallNotifications
from time import time
from django.utils import timezone


def clean_up_cron_job():
    start = time()
    notifications_sc = UserStoryCreatedNotification.objects.all().order_by('created_at')
    notifications_scom = UserStoryCommentedNotification.objects.all().order_by('created_at')
    notifications_cr = UserCommentRepliedNotification.objects.all().order_by('created_at')
    notifications_ao = AdministrativeOverallNotifications.objects.all().order_by('created_at')

    for notif in notifications_sc:
        if (timezone.now() - notif.created_at).total_seconds() // 60 >= 30:
            notif.delete()
        else:
            break
        
    for notif in notifications_scom:
        if (timezone.now() - notif.created_at).total_seconds() // 60 >= 30:
            notif.delete()
        else:
            break
        
    for notif in notifications_cr:
        if (timezone.now() - notif.created_at).total_seconds() // 60 >= 30:
            notif.delete()
        else:
            break
        
    for notif in notifications_ao:
        if (timezone.now() - notif.created_at).total_seconds() // 60 >= 30:
            notif.delete()
        else:
            break
    
    notifications_sc.save()
    notifications_scom.save()
    notifications_cr.save()
    notifications_ao.save()
    
    print(f"Cron Job fired and finished, started = {start}, finished in {time() - start} second(s)")