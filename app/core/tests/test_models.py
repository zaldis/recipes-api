from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_user(email='user@mail.com', password='secret'):
    """ Create base user """
    return get_user_model().objects.create_user(email, password)


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

    def test_email_validation(self):
        """
            All users must have email address
        """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email=None, password='secret')

    def test_superuser_creation(self):
        """
            Custom user model must provide api to create superuser
        """
        user = get_user_model().objects.create_superuser(
                    email='super.user@gmail.com', password='secret')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_representation(self):
        """ Tag should be convertable to string as tag's name """
        tag = models.Tag.objects.create(user=create_user(), name='Vegan')
        self.assertEqual(str(tag), tag.name)

    def test_ingredient_representation(self):
        """ Ingredient should be convertable to string as ingredient's name """
        ingredient = models.Ingredient.objects.create(user=create_user(),
                                                      name='Cucumber')
        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_representation(self):
        """ Recipe should be convertable to string as recipe's title """
        recipe = models.Recipe.objects.create(user=create_user(),
                                              title='Mushroom souce',
                                              time_minutes=5,
                                              price=5.00)
        self.assertEqual(str(recipe), recipe.title)
