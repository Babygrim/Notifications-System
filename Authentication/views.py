from django.shortcuts import render, redirect, HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignupForm, LoginForm
from .models import *
from django.http import JsonResponse
import json

# Create your views here.
# signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
        
    return render(request, 'signup.html', {'form': form})

# login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            if user:
                login(request, user)
                return redirect('stories')
        
        return render(request, 'login.html', {'form': form}) 
    
    elif request.user.is_authenticated:
        return redirect('stories')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})

# logout page
def user_logout(request):
    referer = request.META.get('HTTP_REFERER')
    logout(request)
    if referer:
        return redirect(referer)
    else:
        return redirect('stories')


def viewProfile(request):
    if request.method == "GET":
        user = request.GET.get('user', -1)
        
        if request.user.is_authenticated and user == -1:
            profile = BaseUserProfile.objects.get(user__id = request.user.id)
            
            return JsonResponse({'success': True, 'profile': profile.serialize()})
        else:
            profile = BaseUserProfile.objects.get(user__id = int(user))
            
            return JsonResponse({'success': True, 'profile': profile.serialize_for_others()})
            
        
       
def becomeWriter(request):
    if request.method == "GET":
        user = User.objects.get(pk=int(request.user.id))
        profile = BaseUserProfile.objects.get(user = user)
        
        if profile.writer:
            return redirect('/')
        return render(request, 'become-writer.html')
    
    elif request.method == "POST":
        data = request.POST
        types = data.get('pseudo_type', None)
        profile = BaseUserProfile.objects.get(user = request.user)
        
        if profile.writer:
            return redirect('/')
        else:
            if types:
                writer_profile = UserProfileWriter()
            else:
                author_pseudo = data.get('pseudo')
                writer_profile = UserProfileWriter(writer_pseudo = author_pseudo)
                    
            writer_profile.save()
            profile.writer = writer_profile
            profile.save()
            
            return redirect('/')
        
def subscribeToAuthor(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        author = data.get('author_id')
        subscribeto = UserProfileWriter.objects.get(pk=int(author))
        
        base = BaseUserProfile.objects.get(user = request.user)
        subscription_objects_base = base.reader.subscribed_to
        
        try:
            get_subscription = SubscriptionTimeStampThrough.objects.get(writer = subscribeto, reader = base.reader)
        except SubscriptionTimeStampThrough.DoesNotExist:
            get_subscription = None
            
        if get_subscription:
            subscription_objects_base.remove(subscribeto)
            base.save()
            return JsonResponse({"success": True, "action": False })
        
        else:
            subscription_objects_base.add(subscribeto)
            base.save()
            return JsonResponse({"success": True, "action": True })
        
def getUserSubscriptionWriters(request):
    if request.method == "GET":
        user = request.GET.get('reader')
        
        reader = UserProfileReader.objects.get(pk=int(user))
        
        return JsonResponse({"context": [elem.serialize_load() for elem in reader.subscribed_to.all()]})
        
def setOrRemoveNotifications(request):
    if request.method == "POST":
        data = json.loads(request.body)
        author_id = data.get('author_id', None)

        if author_id:
            base_user = BaseUserProfile.objects.get(user=request.user)
            author = UserProfileWriter.objects.get(pk = author_id)
            
            subscription = SubscriptionTimeStampThrough.objects.get(writer = author, reader = base_user.reader)
            
            if subscription.receive_notifications == True:
                
                subscription.receive_notifications = False
                subscription.save()
                return JsonResponse({'success':True, 'action':False})
                
            else:
                
                subscription.receive_notifications = True
                subscription.save()
                return JsonResponse({'success':True, 'action':True})
                
            
            
        return JsonResponse({'success':False, 'action':False})

        
        
        