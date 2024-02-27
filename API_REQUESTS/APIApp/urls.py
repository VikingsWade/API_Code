
from django.urls import path
from APIApp.views import UserRegistationView, UserLoginView, VerifyEmail, ProfileView, FilteredProfileView

urlpatterns = [
    path('register/', UserRegistationView.as_view(), name='register'),
    path('verify-email/<str:token>/<int:user_id>/', VerifyEmail.as_view(), name='verify_email'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', ProfileView.as_view(), name='profile'),  
    path('filtered-profile/', FilteredProfileView.as_view(), name='filtered_profile'),

]
