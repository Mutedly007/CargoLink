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
