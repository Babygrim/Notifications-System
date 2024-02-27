from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
    path('view_profile', viewProfile, name='profile'),
    path('become_writer', becomeWriter, name='writer'),
    path('subscribe_to', subscribeToAuthor, name="subscribe"),
    path('subscriptions', getUserSubscriptionWriters, name="get_subs"),
    path('note_unnote', setOrRemoveNotifications, name="get_notifications"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)