from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class PortalLoginTests(TestCase):
    def setUp(self):
        self.claim = Group.objects.create(name="claim")
        self.operation = Group.objects.create(name="operation")
        Group.objects.create(name="migration")
        self.user = User.objects.create_user("ada", password="secret-pass")

    def test_home_asks_for_login(self):
        response = self.client.get(reverse("home"))
        self.assertRedirects(response, "/login/?next=/")

    def test_wrong_password_keeps_the_form(self):
        response = self.client.post(
            reverse("login"),
            {"username": "ada", "password": "wrong"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Sign in")
        self.assertContains(response, "Please enter a correct username and password.")

    def test_home_shows_only_assigned_projects(self):
        self.user.groups.add(self.claim, self.operation)
        self.client.login(username="ada", password="secret-pass")

        response = self.client.get(reverse("home"))

        self.assertContains(response, "Claim")
        self.assertContains(response, "https://claim.example.com/")
        self.assertContains(response, "Operation")
        self.assertContains(response, "https://operation.example.com/")
        self.assertNotContains(response, "Migration")
        self.assertNotContains(response, "https://migration.example.com/")

    def test_home_without_groups_explains_the_empty_list(self):
        self.client.login(username="ada", password="secret-pass")
        response = self.client.get(reverse("home"))
        self.assertContains(response, "No projects are assigned to this account.")

    def test_logout_returns_to_login(self):
        self.client.login(username="ada", password="secret-pass")
        response = self.client.post(reverse("logout"))
        self.assertRedirects(response, reverse("login"))
