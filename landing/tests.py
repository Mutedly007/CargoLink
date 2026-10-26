from django.test import TestCase
from django.urls import reverse


class LandingPageTests(TestCase):
    def test_landing_page_renders(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "CargoLink")
        self.assertContains(response, "Connecter, Planifier")
        self.assertContains(response, "Optimiser la Logistique")
        self.assertContains(response, "Aucun quai actif pour le moment")

    def test_preview_404_view(self):
        response = self.client.get(reverse('preview_404'))
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Destination Hors Réseau", status_code=404)

    def test_preview_500_view(self):
        response = self.client.get(reverse('preview_500'))
        self.assertEqual(response.status_code, 500)
        self.assertContains(response, "Arrêt d'Urgence du Serveur", status_code=500)

    def test_preview_403_view(self):
        response = self.client.get(reverse('preview_403'))
        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "Privilèges Insuffisants", status_code=403)

