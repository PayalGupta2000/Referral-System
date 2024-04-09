from django.urls import path
from .views import *
urlpatterns = [
    path('register',UserRegistrationAPIView.as_view()),
    path('login',LoginAPIView.as_view()),
    path('detail',UserDetailsAPIView.as_view()),
    path('logout',LogoutAPIView.as_view()),
    path('ref',ReferralsAPIView.as_view()),

   
]
