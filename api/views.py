from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import make_password
from .models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from .serializers import *
from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger
from rest_framework.permissions import IsAuthenticated


class UserRegistrationAPIView(APIView):
    def post(self, request):
        email = request.data.get("email")
        referral_code = request.data.get('referral_code')
        points = 0  # Default points for a new user
        
        if User.objects.filter(email=email).exists():
            return Response({'error': 'Email is already registered'}, status=status.HTTP_400_BAD_REQUEST)

        # Use email as the username
        username = email

        user = User(email=email, username=username, referral_code=referral_code, points=points)
        user.set_password(request.data.get("password"))

        if referral_code:
            referred_by_user = User.objects.filter(referral_code=referral_code).first()
            if referred_by_user:
                referred_by_user.points += 1
                referred_by_user.save()

        user.save()

        return Response({'message': 'User registered successfully', 'user_id': user.id}, status=status.HTTP_201_CREATED)

from django.contrib.auth import authenticate

class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Authenticate user
        user = authenticate(username=username, password=password)

        if user is not None:
            # User authenticated, generate token
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            # Authentication failed
            print("Authentication failed for email:", username)
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
class UserDetailsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # The authenticated user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.authentication import TokenAuthentication

class LogoutAPIView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        # Get the token associated with the current user's session
        token = Token.objects.get(user=request.user)

        # Delete the token
        token.delete()

        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    

class ReferralsAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Retrieve users who registered using the current user's referral_code
        referred_users = User.objects.filter(referral_code=user.referral_code)

        # Paginate the results
        paginator = Paginator(referred_users, 20)  # 20 users per page
        page = request.query_params.get('page', 1)

        try:
            referred_users_page = paginator.page(page)
        except PageNotAnInteger:
            referred_users_page = paginator.page(1)
        except EmptyPage:
            referred_users_page = paginator.page(paginator.num_pages)

        # Serialize the data
        serializer = UserSerializer(referred_users_page, many=True)

        # Prepare the response
        response_data = {
            'count': paginator.count,
            'next': referred_users_page.next_page_number() if referred_users_page.has_next() else None,
            'previous': referred_users_page.previous_page_number() if referred_users_page.has_previous() else None,
            'results': serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)
