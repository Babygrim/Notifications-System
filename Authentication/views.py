from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer, RegisterSerializer, ProfileSerializer, ProfileSerializerForOthers, WriterSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.views import APIView
from .models import *
from rest_framework_simplejwt.tokens import RefreshToken

#Login User
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_data = serializer.validated_data
        user = serializer.user
        
        profile = BaseUserProfile.objects.get(user = user)


        return Response({
            'success': True,
            'data': ProfileSerializer(profile).data,
            'message': '',
            'access': token_data['access'],
            'refresh': token_data['refresh']
        })

#Register User
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            # Save the new user and get instance
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            
            # Customize response
            response_data = {
                "success": True,
                "message": "User registered successfully",
                "data": ProfileSerializer(BaseUserProfile.objects.get(user = user)).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh)
            }
            
            return Response(response_data)
        
        else:
            return Response({"success": False,  "data": {}, "message": serializer.errors})

# #Log Out
# class LogoutView(APIView):
#     authentication_classes = (JWTAuthentication,)
#     permission_classes = (IsAuthenticated,)

#     def post(self, request):
#         try:
#             # Extract the refresh token from the request data
#             refresh_token = request.data.get("refresh")
#             token = RefreshToken(refresh_token)
#             # Blacklist the token
#             token.blacklist()

#             return JsonResponse({"success": True, "data": {}, "message": ""})
#         except Exception as e:
#             return JsonResponse({"success": False, "data": {}, "message": "Invalid token or token not provided."})

class ViewProfile(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
    
    def get(self, request):
        user = request.GET.get('user', -1)
        
        if request.user.is_authenticated and user == -1:
            profile = BaseUserProfile.objects.get(user__id = request.user.id)
            
            return Response({'success': True, 'data': {"profile": ProfileSerializer(profile).data}, 'message': ''})
        else:
            profile = BaseUserProfile.objects.get(user__id = int(user))
            
            return Response({'success': True, 'data': {"profile": ProfileSerializerForOthers(profile).data}, 'message': ''})
                     
    def patch(self, request):
        profile = BaseUserProfile.objects.get(user = request.user)
        
        data = request.data
        
        if profile.writer:
            new_pseudo = data.get('author_pseudo', None)
            
            if new_pseudo:
                profile.writer.writer_pseudo = new_pseudo
                profile.writer.save()
                profile.save()
        
        new_avatar = data.get('avatar', None)

        if new_avatar:
            profile.avatar = new_avatar
            profile.save()
              
        if new_avatar == None and new_pseudo == None:
            return Response({"success": False, "data": {}, "message": 'Nothing was updated. Patchable parameters are "author_pseudo" and "avatar"'})
            
        return Response({"success": True, "data": {}, "message": 'Profile updated successfully'})
             
class BecomeWriter(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, )
        
    def post(self, request):
        data = request.data
        profile = BaseUserProfile.objects.get(user = request.user)
        
        if profile.writer:
            return Response({'success': False, 'data': "", 'message': "User already has writer profile"})
        else:
            author_pseudo = data.get('author_pseudo')
            
            if author_pseudo:
                try:
                    get_existing = UserProfileWriter.objects.get(writer_pseudo = author_pseudo)
                    
                    if get_existing:
                        return Response({'success': False, 'data': {}, 'message': {"author_pseudo": "Author with that pseudo already exists"}})
                except UserProfileWriter.DoesNotExist:
                    writer_profile = UserProfileWriter(writer_pseudo = author_pseudo)
                            
                    writer_profile.save()
                    profile.writer = writer_profile
                    profile.save()
                    
                    return Response({'success': True, 'data': {"profile": ProfileSerializer(profile).data}, 'message': ''})
            else:
                return Response({'success': False, 'data': {}, 'message': {"author_pseudo": "This field is required"}})
        
class Subscribe(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        data = request.data
        author = data.get('author_id')
        
        if author:
            try:
                subscribeto = UserProfileWriter.objects.get(pk=int(author))
            except UserProfileWriter.DoesNotExist:
                return Response({"success": False, "data": {}, "message": f"Author with id={author} does not exist."})
            except ValueError:
                return Response({"success": False, "data": {}, "message": f"'author_id' should be integer value"})
            
            base = BaseUserProfile.objects.get(user = request.user)
            subscription_objects_base = base.reader.subscribed_to
            
            if base.writer == subscribeto:
                return Response({"success": False, "data": {}, "message": f"You cannot subscribe to yourself"})
            
            try:
                get_subscription = SubscriptionTimeStampThrough.objects.get(writer = subscribeto, reader = base.reader)
            except SubscriptionTimeStampThrough.DoesNotExist:
                get_subscription = None
                
            if get_subscription:
                subscription_objects_base.remove(subscribeto)
                base.save()
                return Response({"success": True, "data": {}, "message": f"Unsubscribed from author={author}"})
            
            else:
                subscription_objects_base.add(subscribeto)
                base.save()
                return Response({"success": True, "data": {}, "message": f"Subscribed to author={author}"})
        
        else:
            return Response({"success": False, "data": {}, "message": f"'author_id' is required request body field"})
        
class Subscriptions(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def get(self, request):
        profile = BaseUserProfile.objects.get(user = request.user)
        
        return Response({"success": True, "data": WriterSerializer(profile.reader.subscribed_to.all(), many = True).data, "message": ""})
        
class NotificationsSetup(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        data = request.data
        author_id = data.get('author_id', None)

        if author_id:
            base_user = BaseUserProfile.objects.get(user=request.user)
            try:
                author = UserProfileWriter.objects.get(pk = author_id)
            except UserProfileWriter.DoesNotExist:
                return Response({'success':False, "data": {}, "message": f"author with author_id={author_id} does not exist."})
            
            try:
                subscription = SubscriptionTimeStampThrough.objects.get(writer = author, reader = base_user.reader)
            except SubscriptionTimeStampThrough.DoesNotExist:
                return Response({'success':False, "data": {}, "message": f"You are not subscribed to author with author_id={author_id}."})
            
            if subscription.receive_notifications == True:
                subscription.receive_notifications = False
                subscription.save()
                return Response({'success':True, "data": {}, "message": f"No longer receiving notifications from author_id={author_id}."})
                
            else:
                
                subscription.receive_notifications = True
                subscription.save()
                return Response({'success':True, "data": {}, "message": f"Receiving notifications from author_id={author_id}."})
                
            
            
        return Response({'success':False, "data": {}, "message": "author_id field is required"})

        
        
        