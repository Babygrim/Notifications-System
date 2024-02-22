from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('login/', user_login, name='login'),
    path('signup/', user_signup, name='signup'),
    path('logout/', user_logout, name='logout'),
    path('view_profile/<int:id>', viewProfile, name='profile'),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)