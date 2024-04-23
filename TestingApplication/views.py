from Authentication.models import BaseUserProfile, UserProfileWriter
from django.contrib.auth.models import User
from Stories.models import Post, PostGenre, PostTags
from Notifications.models import UserCommentRepliedNotification
from Comments.models import Comment
from Notifications.models import *
from time import time
from django.http import JsonResponse
import random
from openpyxl import load_workbook, Workbook

def CreateUsers(request):
    start = time()
    
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    
    wb = Workbook()

    # Select the active worksheet (default first sheet)
    ws = wb.active
    #!!! CREATE 10000 Users and create from 1 to 8 Stories with each User               ~15 min approx
    for _ in range(10000):
        username = ('').join(random.choices(alphabet, k=8))
        password = ('').join(random.choices(alphabet, k=8))
        user = User.objects.create_user(username=username, password=password)
        ws.append((username, password))
        user.save()

    wb.save('users.xlsx')
    all_users = BaseUserProfile.objects.all()
    all_genres = PostGenre.objects.all()
    all_tags = PostTags.objects.all()
    
    for user in all_users:
        if user.writer == None:
            user.writer = UserProfileWriter()
            user.writer.save()
            user.save()
            
        random_counter = random.choice([1,2,3,4,5,6,7,8])
        for _ in range(random_counter):
            tags = random.choices(all_tags, k=random.choice([2,3]))
            post = Post(creator_id = user.writer, post_text = f'Story {('').join(random.choices('0123456789', k=8))}', post_title = f'Story {('').join(random.choices('0123456789', k=8))} by {user.writer.writer_pseudo}', genre = random.choice(all_genres))
            post.save()
            for tag in tags:
                post.tags.add(tag)
            
            post.save()
    
    
    
    #!!! All Users create from 1 to 8 Comments and/or Replies Under random posts
    
    all_users = BaseUserProfile.objects.all()
    all_posts = Post.objects.all()
    all_comments = Comment.objects.all() 
    
    for user in all_users:
        count = random.choice([1,2,3,4,5,6,7,8])
        
        for _ in range(count):
            destiny = random.choice([0,1,2,3,4,5,6,7,8,9])
            
            if destiny % 2 == 0:
                parent = random.choice(all_comments)
                
                create_new = Comment(creator = user, parent_comment = parent, post=parent.post, comment_body = f'Reply by {user.displayable_name}, commenting just to comment cuz I need to test comments')    
                create_new.save()
                
                create_notification = UserCommentRepliedNotification(receiver = parent.creator, source = create_new, parent_source=parent.post)
                create_notification.save()

            else:
                parent_post = random.choice(all_posts)
                
                create_new = Comment(creator = user, post=parent_post, comment_body = f'Comment by {user.displayable_name}, commenting just to comment cuz I need to test comments')    
                create_new.save()
    
    
    
    
    # #!!! Insert 200 randomly generated book titles
    # workbook = load_workbook('books.xlsx')

    # # Select the worksheet (replace 'Sheet1' with the name of your worksheet)
    # worksheet = workbook['Sheet1']

    # # Iterate over rows and access specific cells (columns)
    # all_profiles = BaseUserProfile.objects.filter(writer__isnull = False)
    # all_genres = PostGenre.objects.all()
    # all_tags = PostTags.objects.all()
    
    # for cell in worksheet['A1':'A200']:
    #     user = random.choice(all_profiles)
    #     post = Post(creator_id = user.writer, post_text = f'Story {('').join(random.choices('0123456789', k=8))}', post_title = str(cell[0].value), genre = random.choice(all_genres))
    #     post.save()
    #     for tag in random.choices(all_tags, k=random.choice([2, 3])):
    #         post.tags.add(tag)
        
    #     post.save()
    
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
        