from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import UserProfile


class AccountsAuthTests(TestCase):

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

    def test_admin_login_shows_admin_badge(self):
        admin_user = User.objects.create_user(
            username='admin_boss',
            email='admin@boss.com',
            password='AdminPassword123!',
            first_name='Admin',
            last_name='User'
        )
        admin_user.profile.role = 'ADMIN'
        admin_user.profile.save()

        response = self.client.post(reverse('login'), data={
            'username': 'admin_boss',
            'password': 'AdminPassword123!'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin User")
        self.assertContains(response, "badge-admin")
        self.assertContains(response, "@admin_boss")
        self.assertContains(response, "Administrateur Système")
        self.assertContains(response, "Dashboard Admin")

    def test_removing_admin_role_revokes_admin_badge(self):
        user = User.objects.create_user(
            username='demoted_user',
            email='demoted@test.com',
            password='TestPassword123!',
            first_name='Demoted',
            last_name='User'
        )
        user.profile.role = 'ADMIN'
        user.profile.save()
        self.assertTrue(user.profile.is_admin)
        self.assertTrue(user.is_staff)

        # Demote user to ENTREPOT
        user.profile.role = 'ENTREPOT'
        user.profile.save()
        user.refresh_from_db()
        self.assertFalse(user.profile.is_admin)
        self.assertFalse(user.is_staff)

        # Verify page does not contain admin badge or dashboard admin
        self.client.force_login(user)
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "badge-admin")
        self.assertNotContains(response, "Dashboard Admin")
        self.assertContains(response, "Gestionnaire d'Entrepôt")

    def test_unauthenticated_user_accessing_admin_shows_page_not_accessible(self):
        """Un utilisateur non connecté accédant à /admin/ reçoit un 403 Page Non Accessible."""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Page non accessible", status_code=403)
        self.assertContains(response, "Accès Restreint", status_code=403)
        self.assertNotContains(response, "Django administration", status_code=403)

    def test_non_admin_user_accessing_admin_shows_page_not_accessible(self):
        """Un utilisateur avec rôle non-admin (ex: ENTREPOT) accédant à /admin/ reçoit un 403."""
        user = User.objects.create_user(
            username='simple_entrepot',
            email='simple@test.com',
            password='TestPassword123!'
        )
        user.profile.role = 'ENTREPOT'
        user.profile.save()
        self.client.force_login(user)

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Page non accessible", status_code=403)
        self.assertContains(response, "simple_entrepot", status_code=403)
        self.assertNotContains(response, "Django administration", status_code=403)

    def test_admin_user_accessing_admin_is_authorized(self):
        """Un administrateur CargoLink peut accéder normalement à /admin/."""
        admin_user = User.objects.create_user(
            username='super_admin',
            email='admin@cargolink.tn',
            password='AdminPassword123!'
        )
        admin_user.profile.role = 'ADMIN'
        admin_user.profile.save()
        self.client.force_login(admin_user)

        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Site administration")



