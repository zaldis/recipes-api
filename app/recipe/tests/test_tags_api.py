from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


class PublicTagsApiTests(TestCase):
    """ Test the publicly available tags API """

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """ Test that login is required for retrieving tags """
        response = self.client.get(TAGS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsApiTests(TestCase):
    """ Test the authorized user tags API """

    def setUp(self):
        self.auth_user = get_user_model().objects.create_user(
            'bob@mail.com',
            'secret'
        )
        self.guest_user = get_user_model().objects.create_user(
            'guest@mail.com',
            'secret'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.auth_user)

    def test_retrieve_tags(self):
        """ Test retrieving tags """
        Tag.objects.create(user=self.auth_user, name='Vegan')
        Tag.objects.create(user=self.auth_user, name='Dessert')

        response = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_tags_limited_to_user(self):
        """ Test that tags returned are for the authenticated user """
        Tag.objects.create(user=self.guest_user, name='Fruits')
        tag = Tag.objects.create(user=self.auth_user, name='Comfort food')

        response = self.client.get(TAGS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """ Test creating a new tag """
        payload = {'name': 'New tag'}
        self.client.post(TAGS_URL, payload)

        auth_user_tags = Tag.objects.filter(user=self.auth_user,
                                            name=payload['name'])
        self.assertTrue(auth_user_tags.exists())

    def test_create_tag_invalid(self):
        """ Test creating a new tag with invalid payload """
        payload = {'name': ''}
        response = self.client.post(TAGS_URL, payload)

        self.assertEqual(response.status_code,
                         status.HTTP_400_BAD_REQUEST)
