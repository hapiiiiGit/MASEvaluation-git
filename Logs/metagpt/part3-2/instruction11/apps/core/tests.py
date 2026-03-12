from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import CoreData

User = get_user_model()

class CoreDataAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="coreuser",
            email="coreuser@example.com",
            password="corepassword123"
        )
        self.user2 = User.objects.create_user(
            username="otheruser",
            email="otheruser@example.com",
            password="otherpassword123"
        )
        self.coredata_url = '/api/data/'
        self.coredata = CoreData.objects.create(
            owner=self.user,
            data_field="Initial Data"
        )
        self.coredata2 = CoreData.objects.create(
            owner=self.user2,
            data_field="Other User Data"
        )

    def authenticate(self, user):
        login_url = '/api/auth/login/'
        response = self.client.post(login_url, {
            "username": user.username,
            "password": "corepassword123" if user == self.user else "otherpassword123"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + access_token)

    def test_list_coredata_authenticated(self):
        self.authenticate(self.user)
        response = self.client.get(self.coredata_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Only user's own CoreData should be listed
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['data_field'], "Initial Data")

    def test_list_coredata_unauthenticated(self):
        response = self.client.get(self.coredata_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_coredata(self):
        self.authenticate(self.user)
        payload = {"data_field": "New Data"}
        response = self.client.post(self.coredata_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['data_field'], "New Data")
        self.assertEqual(response.data['owner'], self.user.username)
        self.assertTrue(CoreData.objects.filter(owner=self.user, data_field="New Data").exists())

    def test_retrieve_coredata(self):
        self.authenticate(self.user)
        url = f"{self.coredata_url}{self.coredata.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data_field'], self.coredata.data_field)

    def test_retrieve_coredata_not_owner(self):
        self.authenticate(self.user)
        url = f"{self.coredata_url}{self.coredata2.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_coredata(self):
        self.authenticate(self.user)
        url = f"{self.coredata_url}{self.coredata.id}/"
        payload = {"data_field": "Updated Data"}
        response = self.client.put(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.coredata.refresh_from_db()
        self.assertEqual(self.coredata.data_field, "Updated Data")

    def test_partial_update_coredata(self):
        self.authenticate(self.user)
        url = f"{self.coredata_url}{self.coredata.id}/"
        payload = {"data_field": "Partially Updated"}
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.coredata.refresh_from_db()
        self.assertEqual(self.coredata.data_field, "Partially Updated")

    def test_delete_coredata(self):
        self.authenticate(self.user)
        url = f"{self.coredata_url}{self.coredata.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(CoreData.objects.filter(id=self.coredata.id).exists())

    def test_delete_coredata_not_owner(self):
        self.authenticate(self.user)
        url = f"{self.coredata_url}{self.coredata2.id}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_permissions_enforced(self):
        # Unauthenticated user cannot create
        payload = {"data_field": "Should Fail"}
        response = self.client.post(self.coredata_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Unauthenticated user cannot update
        url = f"{self.coredata_url}{self.coredata.id}/"
        response = self.client.put(url, {"data_field": "Should Fail"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        # Unauthenticated user cannot delete
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)