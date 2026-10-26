from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
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

    def test_profile_view_requires_login(self):
        """Un visiteur non connecté est redirigé vers la page de connexion."""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)

    def test_profile_view_get_authenticated(self):
        """Un utilisateur connecté visualise ses informations sur la page profil."""
        user = User.objects.create_user(
            username='kacem_profil',
            email='kacem@cargolink.tn',
            first_name='Kacem',
            last_name='Trabelsi',
            password='TestPassword123!'
        )
        user.profile.role = 'ENTREPOT'
        user.profile.entreprise = 'Logistique Sahel'
        user.profile.telephone = '+216 99 888 777'
        user.profile.save()

        self.client.force_login(user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kacem Trabelsi")
        self.assertContains(response, "@kacem_profil")
        self.assertContains(response, "kacem@cargolink.tn")
        self.assertContains(response, "Logistique Sahel")
        self.assertContains(response, "+216 99 888 777")
        self.assertContains(response, "Gestionnaire d&#x27;Entrepôt")

    def test_profile_update_personal_info_and_role(self):
        """Un utilisateur met à jour ses coordonnées et son rôle."""
        user = User.objects.create_user(
            username='user_to_edit',
            email='old_email@cargolink.tn',
            first_name='Ancien',
            last_name='Nom',
            password='TestPassword123!'
        )
        user.profile.role = 'ENTREPOT'
        user.profile.save()

        self.client.force_login(user)
        post_data = {
            'first_name': 'Nouveau',
            'last_name': 'Prenom',
            'username': 'user_edited',
            'email': 'nouveau_email@cargolink.tn',
            'role': 'PLANIFICATEUR',
            'entreprise': 'Super Transports',
            'telephone': '+216 55 444 333',
        }
        response = self.client.post(reverse('profile'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Nouveau')
        self.assertEqual(user.last_name, 'Prenom')
        self.assertEqual(user.username, 'user_edited')
        self.assertEqual(user.email, 'nouveau_email@cargolink.tn')
        self.assertEqual(user.profile.role, 'PLANIFICATEUR')
        self.assertEqual(user.profile.entreprise, 'Super Transports')
        self.assertEqual(user.profile.telephone, '+216 55 444 333')

    def test_profile_update_password_success(self):
        """Un utilisateur change son mot de passe avec succès."""
        user = User.objects.create_user(
            username='pwd_user',
            email='pwd@cargolink.tn',
            password='CurrentPassword123!'
        )
        self.client.force_login(user)

        post_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'pwd_user',
            'email': 'pwd@cargolink.tn',
            'role': 'ENTREPOT',
            'entreprise': '',
            'telephone': '',
            'old_password': 'CurrentPassword123!',
            'new_password': 'BrandNewPassword456!',
            'confirm_new_password': 'BrandNewPassword456!',
        }
        response = self.client.post(reverse('profile'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.check_password('BrandNewPassword456!'))

    def test_profile_update_password_wrong_old_password(self):
        """Une erreur est renvoyée si l'ancien mot de passe est erroné."""
        user = User.objects.create_user(
            username='pwd_user_fail',
            email='pwdfail@cargolink.tn',
            password='CurrentPassword123!'
        )
        self.client.force_login(user)

        post_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'pwd_user_fail',
            'email': 'pwdfail@cargolink.tn',
            'role': 'ENTREPOT',
            'entreprise': '',
            'telephone': '',
            'old_password': 'WrongPassword999!',
            'new_password': 'BrandNewPassword456!',
            'confirm_new_password': 'BrandNewPassword456!',
        }
        response = self.client.post(reverse('profile'), data=post_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Le mot de passe actuel saisi est incorrect.", response.context['form'].errors.get('old_password', []))

        user.refresh_from_db()
        self.assertTrue(user.check_password('CurrentPassword123!'))

    def test_profile_update_avatar_upload(self):
        """Un utilisateur peut téléverser une photo de profil valide."""
        user = User.objects.create_user(
            username='avatar_user',
            email='avatar@cargolink.tn',
            password='TestPassword123!'
        )
        self.client.force_login(user)

        # 1x1 valid GIF image
        gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        uploaded_avatar = SimpleUploadedFile('my_avatar.gif', gif_bytes, content_type='image/gif')

        post_data = {
            'first_name': 'Avatar',
            'last_name': 'Tester',
            'username': 'avatar_user',
            'email': 'avatar@cargolink.tn',
            'role': 'ENTREPOT',
            'entreprise': '',
            'telephone': '',
            'avatar': uploaded_avatar,
        }
        response = self.client.post(reverse('profile'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(bool(user.profile.avatar))
        self.assertIn('my_avatar', user.profile.avatar.name)
        # Nettoyage
        if user.profile.avatar:
            user.profile.avatar.delete(save=False)

    def test_profile_update_avatar_delete(self):
        """Un utilisateur peut supprimer sa photo de profil existante."""
        user = User.objects.create_user(
            username='avatar_del_user',
            email='avatardel@cargolink.tn',
            password='TestPassword123!'
        )
        gif_bytes = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff\x00\x00\x00!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
        user.profile.avatar = SimpleUploadedFile('to_delete.gif', gif_bytes, content_type='image/gif')
        user.profile.save()
        self.assertTrue(bool(user.profile.avatar))

        self.client.force_login(user)
        post_data = {
            'first_name': 'Avatar',
            'last_name': 'Tester',
            'username': 'avatar_del_user',
            'email': 'avatardel@cargolink.tn',
            'role': 'ENTREPOT',
            'entreprise': '',
            'telephone': '',
            'delete_avatar': '1',
        }
        response = self.client.post(reverse('profile'), data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertFalse(bool(user.profile.avatar))





