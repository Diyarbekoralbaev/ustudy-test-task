from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import UserModel


class UserTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.me_url = reverse('me')

        # Create a user for login
        self.user_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        self.client.post(self.register_url, self.user_data, format='json')

        # Log in to get token
        login_response = self.client.post(self.login_url, self.user_data, format='json')
        self.access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)

    def test_user_registration(self):
        data = {
            'username': 'newuser',
            'password': 'newpassword123'
        }
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(UserModel.objects.count(), 2)  # 1 from setUp + 1 new user
        self.assertEqual(UserModel.objects.get(username='newuser').username, 'newuser')

    def test_user_login(self):
        response = self.client.post(self.login_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_user_login_invalid(self):
        invalid_data = {
            'username': 'invaliduser',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_get_all_users(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # Only the user created in setUp
        self.assertEqual(response.data[0]['username'], self.user_data['username'])

    def test_get_current_user(self):
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])
