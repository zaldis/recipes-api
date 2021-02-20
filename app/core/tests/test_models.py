from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):

    def test_user_creation(self):
        """
            User model expects email and password
        """

        email = 'test.user@gmail.com'
        password = 'secret'
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_email_normalization(self):
        """
            User email should be normalized when user is created
        """
        email = 'test.user@GMAIL.COM'
        user = get_user_model().objects.create_user(email=email)
        self.assertEqual(user.email, email.lower())
