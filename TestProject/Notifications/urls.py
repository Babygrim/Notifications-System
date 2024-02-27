from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('get_notifications', getUserNotifications, name='getNotifications'),
    path('mark_as_read/', MarkAsRead, name='markAsRead'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
