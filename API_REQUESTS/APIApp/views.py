from rest_framework.response import Response
from .models import User, Profile
from rest_framework import status
from rest_framework.views import APIView
from APIApp.serializers import UserRegistrationSerializer, UserLoginSerializer, ProfileSerializer, ProfileRequestSerializer
from django.contrib.auth import authenticate
from APIApp.renderer import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.core.mail import EmailMessage
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import ValidationError, NotFound

class UserRegistationView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data = request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()

            refresh = RefreshToken.for_user(user)
            token = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
            }

            current_site = get_current_site(request).domain
            relative_link = reverse('verify_email', kwargs={'token': token['access'], 'user_id': token['user_id']})
            absurl = 'http://' + current_site + relative_link

            email_subject = 'Activate your account'
            email_body = f'Hi {user.email},\n\nPlease use the following link to activate your account:\n{absurl}'
            email = EmailMessage(
                email_subject, email_body, 'schandresh24@gmail.com', to=[user.email]
            )
            email.send(fail_silently=False)

            return Response({'message': 'Account created successfully. Please check your email for activation.'},
                            status=status.HTTP_201_CREATED)

            # return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from urllib.parse import unquote
class VerifyEmail(APIView):
    def get(self, request, token, user_id):
        try:
            user = User.objects.get(id=user_id)
            if not user.is_active:
                user.is_active = True
                user.save()

                return Response({'message': 'Email verification successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': 'Email already verified'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

class UserLoginView(APIView):
    renderer_classes = [UserRenderer]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data = request.data) 
        if serializer.is_valid(raise_exception=True):
            email = serializer.validated_data.get('email')
            password = serializer.validated_data.get('password')
            user = authenticate(request, email=email, password=password)

            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)

                response_data = {
                    "token": access_token,
                    "email": email,
                    "level": user.level
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response({'errors': {'non_field_errors':['Email or Password is not valid.']}}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        try:
            profile = Profile.objects.get(user=request.user)
            serializer = ProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Profile.DoesNotExist:
            raise NotFound("Profile does not exist for the user.")

    def put(self, request):
        serializer = ProfileRequestSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            try:
                # Try to get the existing profile for the user
                profile, _ = Profile.objects.get_or_create(user=request.user)
                
                # Update the profile fields
                profile.name = serializer.validated_data['name']
                profile.designation = serializer.validated_data['designation']
                profile.address = serializer.validated_data['address']
                profile.phone_no = serializer.validated_data['phone_no']
                profile.salary = serializer.validated_data['salary']
                
                # Save the updated profile
                profile.save()

                response_serializer = ProfileSerializer(profile)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except Exception as e:
                # Handle other unexpected errors
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import AccessToken

class FilteredProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    LEVEL_FILTERS = {
        'Manager': {'target_level': 'Software-developer'},
        'Project-leader': {'target_level': 'Software-developer'},
        'Software-developer': {'target_level': 'Software-developer'},
    }

    def get(self, request):
        level = request.GET.get('level', '')
        token = request.GET.get('token', '')
        email = request.GET.get('email', '')
        try:
            decoded_token = AccessToken(token)
            print("Decoded Token Payload:", decoded_token.payload)

            if token != '' and email != '':
                try:
                    if level == 'Software-developer':
                        # Software-developer can only see their own data
                        if request.user.email == email and request.user.level == level:
                            profile = Profile.objects.get(user=request.user)
                            serializer = ProfileSerializer(profile)
                        else:
                            raise ValidationError('Invalid token or insufficient permissions')
                    else:
                        # Manager and Project-leader can see data of software-developer
                        target_user = get_object_or_404(User, email=email, level=level)
                        if request.user.level == level and decoded_token.payload['user_id'] == target_user.id:
                            filter_conditions = self.LEVEL_FILTERS[level]
                            target_level = filter_conditions['target_level']
                            profiles = Profile.objects.filter(user__level=target_level)
                            serializer = ProfileSerializer(profiles, many=True)
                        else:
                            raise ValidationError('Invalid token or insufficient permissions')

                    return Response(serializer.data, status=status.HTTP_200_OK)

                except User.DoesNotExist:
                    raise NotFound("User not found")

                except Profile.DoesNotExist:
                    raise NotFound("Profile does not exist for the user.")

            else:
                raise ValidationError('Token and email are required')
        except Exception as e:
            print("Token Decoding Error:", str(e))
            raise ValidationError('Invalid token or insufficient permissions')


