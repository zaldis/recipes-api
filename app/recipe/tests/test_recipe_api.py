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

    def test_create_basic_recipe(self):
        """ Test creating recipe """
        payload = {
            'title': 'Cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """ Test creating recipe with tags """
        tag1 = create_tag(user=self.user, name='Vegan')
        tag2 = create_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """ Test creating recipe with ingredients """
        ingredient1 = create_ingredient(user=self.user, name='Carrot')
        ingredient2 = create_ingredient(user=self.user, name='Apple')
        payload = {
            'title': 'Fruit salad',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }

        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

    def test_partial_update_recipe(self):
        """ Test updating a recipe with patch """
        recipe = create_recipe(user=self.user)
        recipe.tags.add(create_tag(user=self.user))
        new_tag = create_tag(user=self.user, name='Vegan')

        payload = {'title': 'Updated title', 'tags': [new_tag.id]}
        url = get_detail_recipe_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """ Test updating a recipe with put """
        recipe = create_recipe(user=self.user)
        recipe.tags.add(create_tag(user=self.user))
        payload = {
            'title': 'Spaghetti carbonara',
            'time_minutes': 25,
            'price': 5.00
        }
        url = get_detail_recipe_url(recipe.id)
        self.client.put(url, payload)

        recipe.refresh_from_db()
        for key in payload.keys():
            self.assertEqual(getattr(recipe, key), payload[key])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 0)
