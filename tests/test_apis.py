from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from api.models import User

class UserRegistrationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_user_registration_success(self):
        # Test user registration with valid data
        data = {'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post('/register', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user_id', response.data)

    def test_user_registration_duplicate_email(self):
        # Test user registration with duplicate email
        User.objects.create_user(email='test@example.com', password='password123')
        data = {'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post('/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Email is already registered', response.data['error'])

    # Add more test methods for different scenarios...

class LoginAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_login_success(self):
        # Test login with valid credentials
        User.objects.create_user(email='test@example.com', password='password123')
        data = {'email': 'test@example.com', 'password': 'password123'}
        response = self.client.post('/login/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class ReferralsAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_referrals_endpoint_authenticated(self):
        # Create a user with a referral code
        user = User.objects.create_user(email='user1@example.com', password='password123')
        user.referral_code = 'REFERRAL123'
        user.save()

        # Create referred users
        referred_users = []
        for i in range(25):  # Creating 25 referred users
            referred_user = User.objects.create_user(email=f'user{i + 2}@example.com', password='password123')
            referred_user.referral_code = 'REFERRAL123'
            referred_user.save()
            referred_users.append(referred_user)

        # Authenticate the user
        self.client.force_authenticate(user=user)

        # Make a GET request to the referrals endpoint
        response = self.client.get('/ref')

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert the response data structure
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)

        # Assert the number of referred users returned (should be 20 per page)
        self.assertEqual(len(response.data['results']), 20)

        # Assert the timestamp of registration for each referral
        for referral in response.data['results']:
            referred_user = User.objects.get(email=referral['email'])
            self.assertEqual(referral['timestamp'], referred_user.timestamp.isoformat())

    def test_referrals_endpoint_unauthenticated(self):
        # Make a GET request to the referrals endpoint without authentication
        response = self.client.get('/ref')

        # Assert the response status code
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)