from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import Client

User = get_user_model()

class DashboardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.username = "dashboarduser"
        self.password = "dashboardpass123"
        self.email = "dashboarduser@example.com"
        self.user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password
        )
        self.dashboard_url = "/dashboard/"

    def test_dashboard_access_authenticated(self):
        # Login the user
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome to your Dashboard")
        self.assertContains(response, self.username)
        self.assertContains(response, self.email)

    def test_dashboard_access_unauthenticated(self):
        response = self.client.get(self.dashboard_url)
        # Should redirect to login page
        self.assertIn(response.status_code, [302, 301])
        self.assertTrue(response.url.startswith('/login') or '/accounts/login' in response.url)

    def test_dashboard_template_used(self):
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.dashboard_url)
        self.assertTemplateUsed(response, "dashboard.html")
        self.assertTemplateUsed(response, "base.html")