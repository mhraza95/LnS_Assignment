from django.urls import include, path, reverse
from rest_framework.test import APITestCase, URLPatternsTestCase


class AccountTests(APITestCase, URLPatternsTestCase):
    urlpatterns = [
        path('', include('app.urls')),
    ]

    def test_create_contact(self):
        """
        Ensure we can create a new contact object.
        """
        response = self.client.get('contact')
        #response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)