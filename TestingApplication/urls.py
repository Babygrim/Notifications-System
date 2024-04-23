from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('create_users', CreateUsers),
    path('db_info', DBinfo, name="db_info"),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
