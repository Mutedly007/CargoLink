from datetime import date, time, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from entrepots.models import Entrepot, Quai
from .models import Creneau, HistoriqueStatutCreneau


class CreneauxModuleTests(TestCase):
    def setUp(self):
        # Utilisateur Test
        self.user = User.objects.create_user(
            username='kacem_planner',
            email='kacem@cargolink.tn',
            password='TestPassword123!',
            first_name='Kacem',
            last_name='Trabelsi'
        )
        self.user.profile.role = 'PLANIFICATEUR'
        self.user.profile.save()
        self.client.login(username='kacem_planner', password='TestPassword123!')

        # Entrepôt Test
        self.entrepot = Entrepot.objects.create(
            nom="Hub Logistique Rades Port",
            code="ENT-RADES-01",
            adresse="Zone Portuaire, Terminal 3",
            ville="Rades",
            code_postal="2040",
            horaire_ouverture=time(6, 0),
            horaire_fermeture=time(22, 0),
            statut="ACTIF"
        )

        # Quai Test Standard
        self.quai = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai A-01",
            type_quai="STANDARD",
            statut="DISPONIBLE",
            type_camion_accepte="SEMI_REMORQUE"
        )

        # Quai Frigo
        self.quai_frigo = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai F-01",
            type_quai="FRIGORIFIQUE",
            statut="DISPONIBLE",
            type_camion_accepte="TOUS"
        )

        self.today = date.today()

    def test_creneau_list_unauthenticated_redirects_to_landing(self):
        """Vérifie qu'un visiteur non connecté est redirigé vers la page d'accueil principale."""
        self.client.logout()
        response = self.client.get(reverse('creneaux:creneau_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_creneau_list_unauthorized_role_redirects_to_landing(self):
        """Vérifie qu'un rôle non autorisé (ex: Transporteur) est redirigé vers la page d'accueil principale."""
        self.client.logout()
        transporteur_user = User.objects.create_user(
            username='user_transp_test',
            email='transp@cargolink.tn',
            password='TestPassword123!',
        )
        transporteur_user.profile.role = 'TRANSPORTEUR'
        transporteur_user.profile.save()
        self.client.login(username='user_transp_test', password='TestPassword123!')

        response = self.client.get(reverse('creneaux:creneau_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_creneau_creation_and_reference(self):
        """Vérifie la création d'un créneau et la génération automatique de sa référence."""
        creneau = Creneau.objects.create(
            entrepot=self.entrepot,
            quai=self.quai,
            date_creneau=self.today,
            heure_debut=time(9, 0),
            heure_fin=time(10, 30),
            type_operation='DECHARGEMENT',
            transporteur_nom="Transports Express",
            immatriculation_camion="123-TN-4567",
            chauffeur_nom="Ali Ben Salah",
            nb_palettes=25,
            statut='CONFIRME'
        )
        self.assertTrue(creneau.reference.startswith("CRN-"))
        self.assertEqual(creneau.duree_minutes, 90)

    def test_conflict_detection_prevents_overlap(self):
        """Vérifie que deux créneaux qui se chevauchent sur le même quai et la même date lèvent une ValidationError."""
        # Créneau 1 : 09:00 - 10:30
        Creneau.objects.create(
            entrepot=self.entrepot,
            quai=self.quai,
            date_creneau=self.today,
            heure_debut=time(9, 0),
            heure_fin=time(10, 30),
            transporteur_nom="Transports A",
            immatriculation_camion="111-TN-1111",
            chauffeur_nom="Chauffeur 1",
            statut='CONFIRME'
        )

        # Créneau 2 en conflit : 10:00 - 11:30 (chevauchement de 30 min)
        creneau_conflit = Creneau(
            entrepot=self.entrepot,
            quai=self.quai,
            date_creneau=self.today,
            heure_debut=time(10, 0),
            heure_fin=time(11, 30),
            transporteur_nom="Transports B",
            immatriculation_camion="222-TN-2222",
            chauffeur_nom="Chauffeur 2",
            statut='CONFIRME'
        )

        with self.assertRaises(ValidationError):
            creneau_conflit.clean()

    def test_respect_horaires_entrepot(self):
        """Vérifie qu'un créneau en dehors des horaires de l'entrepôt est refusé."""
        # Horaire ouverture entrepôt = 06:00, début = 05:00
        creneau_hors_plage = Creneau(
            entrepot=self.entrepot,
            quai=self.quai,
            date_creneau=self.today,
            heure_debut=time(5, 0),
            heure_fin=time(6, 30),
            transporteur_nom="Transports Nuit",
            immatriculation_camion="333-TN-3333",
            chauffeur_nom="Chauffeur Nuit"
        )
        with self.assertRaises(ValidationError):
            creneau_hors_plage.clean()

    def test_statut_workflow_and_quai_synchronization(self):
        """Vérifie le cycle de vie du créneau et la synchronisation automatique du statut du quai."""
        creneau = Creneau.objects.create(
            entrepot=self.entrepot,
            quai=self.quai,
            date_creneau=self.today,
            heure_debut=time(14, 0),
            heure_fin=time(15, 0),
            transporteur_nom="Logistique Tunis",
            immatriculation_camion="444-TN-4444",
            chauffeur_nom="Mounir Khemir",
            statut='EN_ATTENTE'
        )

        # 1. Confirmation
        creneau.confirmer(user=self.user)
        self.assertEqual(creneau.statut, 'CONFIRME')
        self.assertEqual(self.quai.statut, 'DISPONIBLE')

        # 2. Arrivée
        creneau.marquer_arrive(user=self.user)
        self.assertEqual(creneau.statut, 'ARRIVE')
        self.assertIsNotNone(creneau.heure_arrivee_reelle)

        # 3. Mettre à quai (Début opération) -> Occupe automatiquement le quai
        creneau.mettre_a_quai(user=self.user)
        self.assertEqual(creneau.statut, 'EN_COURS')
        self.quai.refresh_from_db()
        self.assertEqual(self.quai.statut, 'OCCUPE')

        # 4. Terminer -> Libère automatiquement le quai
        creneau.terminer(user=self.user)
        self.assertEqual(creneau.statut, 'TERMINE')
        self.quai.refresh_from_db()
        self.assertEqual(self.quai.statut, 'DISPONIBLE')

        # 5. Vérification traçabilité
        self.assertEqual(creneau.historique.count(), 4)

    def test_views_response(self):
        """Vérifie que les vues principales répondent HTTP 200."""
        # Liste
        res = self.client.get(reverse('creneaux:creneau_list'))
        self.assertEqual(res.status_code, 200)

        # Planning
        res = self.client.get(reverse('creneaux:creneau_planning'))
        self.assertEqual(res.status_code, 200)

        # Demande de créneau (Module Kacem)
        res = self.client.get(reverse('creneaux:demande_creneau'))
        self.assertEqual(res.status_code, 200)

        # Export CSV
        res = self.client.get(reverse('creneaux:creneau_export_csv'))
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res['Content-Type'], 'text/csv; charset=utf-8')

    def test_ai_smart_dock_allocator(self):
        """Vérifie le moteur IA d'optimisation et d'attribution du meilleur quai (Volet IA - Kacem)."""
        from .ai_optimizer import SmartDockAllocator

        allocator = SmartDockAllocator()
        # Test 1 : Recommandation pour de la marchandise standard
        rec = allocator.recommend_best_dock(
            entrepot_id=self.entrepot.id,
            date_creneau=self.today,
            heure_debut=time(11, 0),
            heure_fin=time(12, 30),
            type_marchandise='STANDARD',
            type_camion='SEMI_REMORQUE',
            nb_palettes=20
        )
        self.assertTrue(rec['success'])
        self.assertIn('meilleur_quai_id', rec)
        self.assertGreaterEqual(rec['score_optimal'], 50)

        # Test 2 : Requête AJAX API
        api_res = self.client.get(reverse('creneaux:api_ai_recommend_dock'), {
            'entrepot_id': self.entrepot.id,
            'date': self.today.strftime('%Y-%m-%d'),
            'heure_debut': '11:00',
            'heure_fin': '12:30',
            'type_marchandise': 'STANDARD',
            'type_camion': 'SEMI_REMORQUE',
            'nb_palettes': 15
        })
        self.assertEqual(api_res.status_code, 200)
        json_data = api_res.json()
        self.assertTrue(json_data['success'])
        self.assertEqual(json_data['meilleur_quai_id'], rec['meilleur_quai_id'])

    def test_gemini_slot_assistant(self):
        """Vérifie l'assistant Gemini bridé strictement au module des créneaux."""
        from .gemini_service import GeminiSlotAssistant

        assistant = GeminiSlotAssistant()

        # Test 1 : Question autorisée sur les créneaux
        res_valid = assistant.ask("Combien de créneaux sont prévus aujourd'hui ?")
        self.assertTrue(res_valid['success'])
        self.assertIn("créneau", res_valid['response'].lower())

        # Test 2 : Question hors-périmètre (doit être refusée par le garde-fou)
        res_hors_sujet = assistant.ask("Donne-moi une recette de cuisine pour ce soir.")
        self.assertTrue(res_hors_sujet['success'])
        self.assertIn("exclusivement aux questions relatives au module", res_hors_sujet['response'])
        self.assertIn("Gestion des Créneaux", res_hors_sujet['response'])

        # Test 3 : Page assistant HTTP 200
        res_page = self.client.get(reverse('creneaux:assistant_creneaux'))
        self.assertEqual(res_page.status_code, 200)

    def test_entrepot_role_consultation_only_restriction(self):
        """
        Vérifie que la session Gestionnaire d'Entrepôt est limitée à la consultation :
        - Consultation OK (liste, planning, détail).
        - Planification, modification, annulation et validation strictement bloquées.
        """
        # 1. Création d'un utilisateur au rôle ENTREPOT
        entrepot_user = User.objects.create_user(
            username='user_entrepot_test',
            email='entrepot@cargolink.tn',
            password='Password123!',
        )
        entrepot_user.profile.role = 'ENTREPOT'
        entrepot_user.profile.save()

        # Création d'un créneau pour tester les accès détail, modifier, annuler
        creneau = Creneau.objects.create(
            entrepot=self.entrepot,
            quai=self.quai,
            date_creneau=self.today + timedelta(days=2),
            heure_debut=time(14, 0),
            heure_fin=time(15, 0),
            statut='EN_ATTENTE',
            type_operation='DECHARGEMENT',
            transporteur_nom='Trans Express',
            immatriculation_camion='999-TN-999',
            chauffeur_nom='Chauffeur Test',
            consignes='Colis divers',
            type_marchandise='STANDARD',
            nb_palettes=10
        )

        self.client.login(username='user_entrepot_test', password='Password123!')

        # 2. Consultation autorisée (Liste, Planning, Détail)
        res_list = self.client.get(reverse('creneaux:creneau_list'))
        self.assertEqual(res_list.status_code, 200)
        self.assertTrue(res_list.context['is_entrepot_role'])

        res_planning = self.client.get(reverse('creneaux:creneau_planning'))
        self.assertEqual(res_planning.status_code, 200)
        self.assertTrue(res_planning.context['is_entrepot_role'])

        res_detail = self.client.get(reverse('creneaux:creneau_detail', kwargs={'pk': creneau.pk}))
        self.assertEqual(res_detail.status_code, 200)
        self.assertTrue(res_detail.context['is_entrepot_role'])

        # 3. Actions d'écriture interdites (Redirections avec message d'avertissement)
        # Création directe
        res_create = self.client.get(reverse('creneaux:creneau_create'))
        self.assertEqual(res_create.status_code, 302)
        self.assertRedirects(res_create, reverse('creneaux:creneau_list'))

        # Demande de créneau
        res_demande = self.client.get(reverse('creneaux:demande_creneau'))
        self.assertEqual(res_demande.status_code, 302)
        self.assertRedirects(res_demande, reverse('creneaux:creneau_list'))

        # Modification
        res_update = self.client.get(reverse('creneaux:creneau_update', kwargs={'pk': creneau.pk}))
        self.assertEqual(res_update.status_code, 302)
        self.assertRedirects(res_update, reverse('creneaux:creneau_detail', kwargs={'pk': creneau.pk}))

        # Annulation
        res_cancel = self.client.get(reverse('creneaux:creneau_cancel', kwargs={'pk': creneau.pk}))
        self.assertEqual(res_cancel.status_code, 302)
        self.assertRedirects(res_cancel, reverse('creneaux:creneau_detail', kwargs={'pk': creneau.pk}))

        # Confirmation
        res_confirm = self.client.get(reverse('creneaux:creneau_confirm', kwargs={'pk': creneau.pk}))
        self.assertEqual(res_confirm.status_code, 302)
        self.assertRedirects(res_confirm, reverse('creneaux:creneau_detail', kwargs={'pk': creneau.pk}))

