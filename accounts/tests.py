from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile


class AccountsAuthTests(TestCase):
    def test_landing_page_renders(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CargoLink")
        self.assertContains(response, "CONNECTER")
        self.assertContains(response, "OPTIMISER")

    def test_signup_creates_user_with_role(self):
        signup_data = {
            'first_name': 'Aziz',
            'last_name': 'Hammami',
            'username': 'aziz_test',
            'email': 'aziz@test.com',
            'role': 'ENTREPOT',
            'entreprise': 'CargoLink Hub',
            'telephone': '+216 12 345 678',
            'password': 'StrongPassword123!',
            'password_confirm': 'StrongPassword123!',
        }
        response = self.client.post(reverse('signup'), data=signup_data, follow=True)
        self.assertEqual(response.status_code, 200)

        # Check user created in database
        user = User.objects.get(username='aziz_test')
        self.assertEqual(user.email, 'aziz@test.com')
        self.assertTrue(user.is_authenticated)

        # Check profile and role
        self.assertEqual(user.profile.role, 'ENTREPOT')
        self.assertEqual(user.profile.entreprise, 'CargoLink Hub')

    def test_login_and_logout(self):
        user = User.objects.create_user(
            username='chauffeur_test',
            email='chauffeur@test.com',
            password='TestPassword123!'
        )
        user.profile.role = 'TRANSPORTEUR'
        user.profile.save()

        # Test login
        response = self.client.post(reverse('login'), data={
            'username': 'chauffeur_test',
            'password': 'TestPassword123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)

        # Test logout
        logout_response = self.client.get(reverse('logout'), follow=True)
        self.assertEqual(logout_response.status_code, 200)
        self.assertFalse(logout_response.context['user'].is_authenticated)
