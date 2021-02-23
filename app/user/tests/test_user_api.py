from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
USER_URL = reverse('user:profile')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """
        Test not authorized user's api
    """

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """
            To success user creation should be passed:
                email,
                name,
                password (more than 5 symbols)
        """
        payload = {
            'email': 'user@gmail.com',
            'password': 'secret',
            'name': 'Bob'
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**response.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_user_creation_if_already_exists(self):
        """
            It's not possible to create two identical users
        """
        payload = {
            'email': 'user@gmail.com',
            'password': 'secret',
            'name': 'Bob'
        }
        create_user(**payload)

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """
            User's password should be more than 5 symbols
        """
        payload = {
            'email': 'user@gmail.com',
            'password': 'pwd',
            'name': 'Bob',
        }

        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST),
        user_exists = get_user_model().objects.filter(
                email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
            Test that token is created for user
        """
        payload = {'email': 'user@gmail.com', 'password': 'secret'}
        create_user(**payload)
        response = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_token_invalid_credentials(self):
        """
            Test that token is not created if invalid credentials are given
        """
        payload = {'email': 'user@gmail.com', 'password': 'secret'}
        create_user(**payload)

        payload['password'] = '123'
        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """
            Test that token is not created if user does not exist
        """
        payload = {'email': 'user@gmail.com', 'password': 'secret'}

        response = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', response.data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """
            Test that authentication is required for users
        """
        response = self.client.get(USER_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
        Test API requests that require authentication
    """

    def setUp(self):
        self.user = create_user(
            email='user@mail.com',
            password='secret',
            name='Bob'
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """
            Test retrieving profile for logged in user
        """
        response = self.client.get(USER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name
        })

    def test_post_profile_not_allowed(self):
        """
            Post request is not allowed for profile endpoint
        """
        response = self.client.post(USER_URL, {})
        self.assertEqual(response.status_code,
                         status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """
            Test updating the user profile for authenticated user
        """
        payload = {'name': 'NewName', 'password': 'new password'}

        response = self.client.patch(USER_URL, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
