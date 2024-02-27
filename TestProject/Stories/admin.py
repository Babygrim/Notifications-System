from django.contrib import admin
from Authentication.models import *
from Stories.models import *
from Notifications.models import *
from Comments.models import *
# Register your models here.

admin.site.register(PostGenre)
admin.site.register(PostTags)
admin.site.register(BaseUserProfile)
admin.site.register(UserProfileReader)
admin.site.register(UserProfileWriter)
admin.site.register(Comment)
admin.site.register(AdministrativeOverallNotifications)
admin.site.register(UserCommentRepliedNotification)
admin.site.register(UserStoryCommentedNotification)
admin.site.register(UserStoryCreatedNotification)
admin.site.register(Post)
admin.site.register(UserLikedPosts)
admin.site.register(UserViewedPosts)
admin.site.register(MarkedAsRead)