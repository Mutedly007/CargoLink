from datetime import date, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from accounts.models import UserProfile
from camions.models import Camion, HistoriquePassage
from camions.ai_service import GeminiTruckDiagnostic


class CamionModelTests(TestCase):
    """
    Tests unitaires sur le modèle Camion (Validations, contraintes et logique métier).
    """

    def setUp(self):
        self.user = User.objects.create_user(username='transporteur_test', password='password123')
        UserProfile.objects.filter(user=self.user).update(role='TRANSPORTEUR', entreprise='Test Transports')

    def test_camion_creation_and_normalization(self):
        """Vérifie la normalisation automatique en majuscules de l'immatriculation."""
        camion = Camion.objects.create(
            immatriculation="  234 tun 5678  ",
            marque="Volvo",
            modele="FH16",
            annee_fabrication=2022,
            type_camion="SEMI_REMORQUE",
            capacite_tonnage=24.5,
            volume_m3=85,
            capacite_palettes=33,
            kilometrage=100000,
            transporteur=self.user
        )
        self.assertEqual(camion.immatriculation, "234 TUN 5678")
        self.assertEqual(camion.societe_transport, "Test Transports")
        self.assertEqual(camion.badge_status_class, "status-disponible")
        self.assertEqual(str(camion), "234 TUN 5678 - Volvo FH16 (Semi-remorque (38-44t))")

    def test_capacite_tonnage_strictement_positive(self):
        """Vérifie qu'un tonnage négatif ou nul lève une ValidationError."""
        camion = Camion(
            immatriculation="123 TUN 4567",
            marque="Scania",
            modele="R450",
            capacite_tonnage=0.0
        )
        with self.assertRaises(ValidationError):
            camion.full_clean()

    def test_immatriculation_trop_courte(self):
        """Vérifie qu'une immatriculation de moins de 4 caractères est rejetée."""
        camion = Camion(
            immatriculation="AB",
            marque="DAF",
            modele="XF",
            capacite_tonnage=18.0
        )
        with self.assertRaises(ValidationError):
            camion.full_clean()

    def test_controle_technique_urgent_property(self):
        """Vérifie l'indicateur d'alerte lorsque le contrôle technique est prévu dans moins de 15 jours."""
        today = date.today()
        camion = Camion.objects.create(
            immatriculation="999 TUN 8888",
            marque="Mercedes-Benz",
            modele="Actros",
            capacite_tonnage=20.0,
            date_prochain_controle=today + timedelta(days=5)
        )
        self.assertTrue(camion.controle_technique_urgent)

        # Contrôle lointain (dans 60 jours) -> non urgent
        camion.date_prochain_controle = today + timedelta(days=60)
        camion.save()
        self.assertFalse(camion.controle_technique_urgent)


class CamionViewsIntegrationTests(TestCase):
    """
    Tests d'intégration sur les vues, les formulaires, le contrôle d'accès RBAC et l'IA.
    """

    def setUp(self):
        self.client = Client()

        # Utilisateur 1: Transporteur autorisé
        self.transporteur_user = User.objects.create_user(username='transporteur1', password='pass_transporteur')
        UserProfile.objects.filter(user=self.transporteur_user).update(role='TRANSPORTEUR', entreprise='Fret Rapide')

        # Utilisateur 2: Gestionnaire Entrepôt (droit de consultation seulement)
        self.entrepot_user = User.objects.create_user(username='entrepot1', password='pass_entrepot')
        UserProfile.objects.filter(user=self.entrepot_user).update(role='ENTREPOT')

        # Camion de test
        self.camion = Camion.objects.create(
            immatriculation="111 TUN 2222",
            marque="Renault",
            modele="T-High",
            annee_fabrication=2023,
            type_camion="SEMI_REMORQUE",
            capacite_tonnage=25.0,
            volume_m3=90,
            capacite_palettes=33,
            etat="DISPONIBLE",
            kilometrage=50000,
            transporteur=self.transporteur_user
        )

    def test_camion_list_view_accessible_public(self):
        """Vérifie que le catalogue de la flotte est accessible en consultation."""
        response = self.client.get(reverse('camions:camion_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'camions/camion_list.html')
        self.assertContains(response, "111 TUN 2222")

    def test_camion_detail_view(self):
        """Vérifie l'affichage de la fiche détaillée du camion."""
        response = self.client.get(reverse('camions:camion_detail', kwargs={'pk': self.camion.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'camions/camion_detail.html')
        self.assertContains(response, "Score de Santé & Maintenance Prédictive")

    def test_camion_create_by_transporteur_success(self):
        """Vérifie qu'un utilisateur avec le rôle TRANSPORTEUR peut créer un camion."""
        self.client.login(username='transporteur1', password='pass_transporteur')
        post_data = {
            'immatriculation': '333 TUN 4444',
            'marque': 'Scania',
            'modele': 'V8 650',
            'annee_fabrication': 2023,
            'type_camion': 'SEMI_REMORQUE',
            'capacite_tonnage': '26.00',
            'volume_m3': '92',
            'capacite_palettes': '33',
            'etat': 'DISPONIBLE',
            'kilometrage': '40000',
            'norme_anti_pollution': 'EURO_6',
            'societe_transport': 'Fret Rapide',
        }
        response = self.client.post(reverse('camions:camion_create'), post_data)
        self.assertEqual(response.status_code, 302)  # Redirection vers la fiche
        self.assertTrue(Camion.objects.filter(immatriculation='333 TUN 4444').exists())

    def test_camion_create_denied_for_non_transporteur(self):
        """Sécurité RBAC : Un gestionnaire d'entrepôt ne peut pas créer de camions."""
        self.client.login(username='entrepot1', password='pass_entrepot')
        post_data = {
            'immatriculation': '777 TUN 8888',
            'marque': 'Volvo',
            'modele': 'FE',
            'annee_fabrication': 2022,
            'type_camion': 'PORTEUR',
            'capacite_tonnage': '12.0',
            'volume_m3': '45',
            'capacite_palettes': '16',
            'etat': 'DISPONIBLE',
            'kilometrage': '60000',
            'norme_anti_pollution': 'EURO_5',
        }
        response = self.client.post(reverse('camions:camion_create'), post_data)
        # Redirigé avec message d'interdiction
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Camion.objects.filter(immatriculation='777 TUN 8888').exists())

    def test_quick_status_change(self):
        """Vérifie le basculement rapide d'état opérationnel."""
        self.client.login(username='transporteur1', password='pass_transporteur')
        response = self.client.post(
            reverse('camions:camion_quick_status', kwargs={'pk': self.camion.pk}),
            {'nouvel_etat': 'EN_MAINTENANCE'}
        )
        self.assertEqual(response.status_code, 302)
        self.camion.refresh_from_db()
        self.assertEqual(self.camion.etat, 'EN_MAINTENANCE')

    def test_ai_diagnostic_endpoint(self):
        """Vérifie l'API asynchrone de diagnostic IA de maintenance prédictive."""
        self.client.login(username='transporteur1', password='pass_transporteur')
        response = self.client.get(reverse('camions:camion_ai_diagnostic', kwargs={'pk': self.camion.pk}))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertIn('health_score', data['report'])
        self.assertIn('risk_level', data['report'])
        self.assertIn('critical_components', data['report'])
        self.assertIn('response_time_ms', data['report'])
