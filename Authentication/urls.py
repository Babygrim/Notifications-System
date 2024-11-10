from django.urls import path
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    
    path('login', MyTokenObtainPairView.as_view(), name='login'),
    path('signup', RegisterView.as_view(), name='signup'),
    path('refresh', TokenRefreshView.as_view(), name='refresh'),
    #path('logout', LogoutView.as_view(), name='logout'),
    path('profile', ViewProfile.as_view(), name='profile'),
    path('writer', BecomeWriter.as_view(), name='writer'),
    path('subscribe', Subscribe.as_view(), name="subscribe"),
    path('subscriptions', Subscriptions.as_view(), name="get_subs"),
    path('notify', NotificationsSetup.as_view(), name="get_notifications"),
    
]