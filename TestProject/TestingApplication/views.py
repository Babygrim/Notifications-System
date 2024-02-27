from Authentication.models import BaseUserProfile, UserProfileWriter
from django.contrib.auth.models import User
from Stories.models import Post, PostGenre
from Notifications.models import UserCommentRepliedNotification
from Comments.models import Comment
from Notifications.models import *
from time import time
from django.http import JsonResponse
import random

def CreateUsers(request):
    start = time()
    
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    
    #!!! CREATE 10000 Users and create from 1 to 8 Stories with each User               ~15 min approx
    # for _ in range(10000):
    #     user = User.objects.create_user(username=('').join(random.choices(alphabet, k=8)), password=('').join(random.choices(alphabet, k=8)))
    #     user.save()

    # all_users = BaseUserProfile.objects.all()
    # all_genres = PostGenre.objects.all()
    
    # for user in all_users:
    #     if user.writer == None:
    #         user.writer = UserProfileWriter()
    #         user.save()
            
    #     random_counter = random.choice([1,2,3,4,5,6,7,8])
    #     for _ in range(random_counter):
    #         post = Post(creator_id = user.writer, post_text = f'Story {('').join(random.choices('0123456789', k=8))}', post_title = f'Story {('').join(random.choices('0123456789', k=8))} by {user.writer.writer_pseudo}', genre = random.choice(all_genres))
    #         post.save()
    
    #
    
    #!!! All Users create from 1 to 8 Comments and/or Replies Under random posts
    
    all_users = BaseUserProfile.objects.all()
    all_posts = Post.objects.all()
    all_comments = Comment.objects.all() 
    
    for user in all_users:
        count = random.choice([1,2,3,4,5,6,7,8])
        
        for _ in range(count):
            destiny = random.choice([0,1,2,3,4,5,6,7,8,9])
            
            # if destiny % 2 == 0:
            parent = random.choice(all_comments)
            
            create_new = Comment(creator = user, parent_comment = parent, post=parent.post, comment_body = f'Reply by {user.displayable_name}, commenting just to comment cuz I need to test comments')    
            create_new.save()
            
            create_notification = UserCommentRepliedNotification(receiver = parent.creator, source = create_new, parent_source=parent.post)
            create_notification.save()

            # else:
            #     parent_post = random.choice(all_posts)
                
            #     create_new = Comment(creator = user, post=parent_post, comment_body = f'Comment by {user.displayable_name}, commenting just to comment cuz I need to test comments')    
            #     create_new.save()
              
    return JsonResponse({"message":"SUCCESS!", "time": time() - start})
        
        
def DBinfo(request):
    if request.method == "GET":
        numb_of_users = BaseUserProfile.objects.count()
        numb_of_posts = Post.objects.count()
        numb_of_comments = Comment.objects.count()
        numb_of_story_created_notifications = UserStoryCreatedNotification.objects.count()
        numb_of_comment_replied_notifications = UserCommentRepliedNotification.objects.count()
        numb_of_story_commented_notifications = UserStoryCommentedNotification.objects.count()
        numb_of_admin_notifications = AdministrativeOverallNotifications.objects.count()
        
        return JsonResponse({
            "users": numb_of_users,
            "posts": numb_of_posts,
            "comments": numb_of_comments,
            "sc_notifications": numb_of_story_created_notifications,
            "scom_notifications": numb_of_story_commented_notifications,
            "ao_notifications": numb_of_admin_notifications,
            "cr_notifications": numb_of_comment_replied_notifications,
        })
        