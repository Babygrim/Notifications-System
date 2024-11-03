from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('login', MyTokenObtainPairView.as_view(), name='login'),
    path('signup', RegisterView.as_view(), name='signup'),
    #path('logout', LogoutView.as_view(), name='logout'),
    path('view_profile', ViewProfile.as_view(), name='profile'),
    path('writer', BecomeWriter.as_view(), name='writer'),
    # path('subscribe_to', subscribeToAuthor, name="subscribe"),
    # path('subscriptions', getUserSubscriptionWriters, name="get_subs"),
    # path('note_unnote', setOrRemoveNotifications, name="get_notifications"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)