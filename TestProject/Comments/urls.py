from django.urls import path
from .views import printAllComments, ReplyToComment, printNoteComment
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('all_comments', printAllComments, name='comments'),
    path('replies/<int:comment_id>', ReplyToComment, name='make_comments'),
    path('view_reply/<int:id>', printNoteComment, name = "note"),
    
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
