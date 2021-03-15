from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient, Tag
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


RECIPES_URL = reverse('recipe:recipe-list')


def get_detail_recipe_url(recipe_id: int) -> str:
    """ Return recipe detail url """
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_ingredient(user, name='Sample ingredient'):
    """ Create and return sample ingredient """
    return Ingredient.objects.create(user=user, name=name)


def create_tag(user, name='Sample tag'):
    """ Create and return sample tag """
    return Tag.objects.create(user=user, name=name)


def create_recipe(user, **params):
    """ Create and return sample recipe """
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeAPITests(TestCase):
    """ Test unauthenticated recipe API access """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test that authentication is required """
        response = self.client.get(RECIPES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """ Test authenticated recipe API access """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@mail.com',
            'password'
        )
        self.guest_user = get_user_model().objects.create_user(
            'guest@mail.com',
            'password'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """ Test retrieving a list of recipes """
        [create_recipe(user=self.user) for _ in range(3)]

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """ Test retrieving recipes for authenticated user """
        create_recipe(user=self.user)
        create_recipe(user=self.guest_user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        """ Test viewing a recipe detail """
        recipe = create_recipe(user=self.user)
        recipe.tags.add(
            create_tag(user=self.user)
        )
        recipe.ingredients.add(
            create_ingredient(user=self.user)
        )

        url = get_detail_recipe_url(recipe.id)
        response = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.data, serializer.data)
