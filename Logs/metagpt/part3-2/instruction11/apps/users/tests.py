from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Profile

User = get_user_model()

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.logout_url = '/api/auth/logout/'
        self.user_data = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "strongpassword123",
            "profile": {
                "bio": "Hello, I am a test user."
            }
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        user = User.objects.get(username="testuser")
        self.assertTrue(user.check_password(self.user_data["password"]))
        self.assertEqual(user.email, self.user_data["email"])
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.bio, self.user_data["profile"]["bio"])

    def test_user_login(self):
        # Register first
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_user_login_invalid_credentials(self):
        # Register first
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            "username": self.user_data["username"],
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_user_logout(self):
        # Register and login first
        self.client.post(self.register_url, self.user_data, format='json')
        login_data = {
            "username": self.user_data["username"],
            "password": self.user_data["password"]
        }
        login_response = self.client.post(self.login_url, login_data, format='json')
        access_token = login_response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)
        response = self.client.post(self.logout_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)

    def test_profile_created_on_registration(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username="testuser")
        self.assertTrue(Profile.objects.filter(user=user).exists())