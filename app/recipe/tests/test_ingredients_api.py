from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTests(TestCase):
    """ Test the publicly available ingredients API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required to access the endpoint """
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code,
                         status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """ Test the private ingredients API """

    def setUp(self):
        self.client = APIClient()
        self.auth_user = get_user_model().objects.create_user(
            'bob@mail.com', 'secret'
        )
        self.guest_user = get_user_model().objects.create_user(
            'alice@mail.com', 'secret'
        )
        self.client.force_authenticate(self.auth_user)

    def test_retrieve_ingredient_list(self):
        """ Test retrieving a list of ingredients """
        Ingredient.objects.create(user=self.auth_user, name='Kale')
        Ingredient.objects.create(user=self.auth_user, name='Salt')

        response = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """
            Test that ingredients for the authenticated user are
            returned
        """
        Ingredient.objects.create(user=self.guest_user, name='Vinegar')
        ingredient = Ingredient.objects.create(
            user=self.auth_user,
            name='Tumeric'
        )

        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """ Test create new ingredient """
        payload = {'name': 'Cabbage'}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Ingredient.objects.filter(
                user=self.auth_user, name=payload['name']
            ).exists()
        )

    def test_create_ingredient_invalid(self):
        """ Test create invalid ingredient fails """
        payload = {'name': ''}

        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
