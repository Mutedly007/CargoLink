from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Entrepot, Quai


class EntrepotCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='aziz_manager',
            email='aziz@cargolink.tn',
            password='TestPassword123!',
            first_name='Aziz',
            last_name='Hammami'
        )
        self.user.profile.role = 'ENTREPOT'
        self.user.profile.save()

        self.entrepot = Entrepot.objects.create(
            nom="Hub Logistique Rades Port",
            code="ENT-RADES-01",
            adresse="Zone Portuaire, Terminal 3",
            ville="Rades",
            code_postal="2040",
            telephone="+216 71 111 222",
            email_contact="rades@cargolink.tn",
            horaire_ouverture="06:00",
            horaire_fermeture="22:00",
            jours_ouverture="Lundi - Samedi",
            capacite_palettes=3000,
            superficie_m2=12000,
            statut="ACTIF",
            gestionnaire=self.user
        )

        self.quai1 = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai A-01",
            type_quai="STANDARD",
            statut="DISPONIBLE",
            capacite_palettes_heure=33,
            type_camion_accepte="SEMI_REMORQUE"
        )

        self.quai2 = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai Frigo F-01",
            type_quai="FRIGORIFIQUE",
            statut="OCCUPE",
            capacite_palettes_heure=25,
            type_camion_accepte="TOUS"
        )

    def test_model_computed_properties(self):
        """Vérifie le calcul dynamique des métriques de quai sur l'entrepôt."""
        self.assertEqual(self.entrepot.nb_quais, 2)
        self.assertEqual(self.entrepot.nb_quais_disponibles, 1)
        self.assertEqual(self.entrepot.nb_quais_occupes, 1)
        self.assertEqual(self.entrepot.taux_disponibilite, 50)

    def test_quai_toggle_methods(self):
        """Vérifie les méthodes d'action rapide occuper() et liberer()."""
        self.quai1.occuper()
        self.assertEqual(self.quai1.statut, 'OCCUPE')
        self.quai1.liberer()
        self.assertEqual(self.quai1.statut, 'DISPONIBLE')

    def test_entrepot_list_view(self):
        """R (Read List) : Vérifie l'affichage de la liste et le moteur de recherche."""
        response = self.client.get(reverse('entrepots:entrepot_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hub Logistique Rades Port")
        self.assertContains(response, "ENT-RADES-01")

        # Test de recherche par ville
        search_res = self.client.get(reverse('entrepots:entrepot_list'), {'q': 'Rades'})
        self.assertEqual(search_res.status_code, 200)
        self.assertContains(search_res, "Hub Logistique Rades Port")

        # Test de recherche infructueuse
        empty_res = self.client.get(reverse('entrepots:entrepot_list'), {'q': 'InconnuVille'})
        self.assertEqual(empty_res.status_code, 200)
        self.assertContains(empty_res, "Aucun entrepôt trouvé")

    def test_entrepot_detail_view(self):
        """R (Read Detail) : Vérifie la fiche détaillée et ses quais."""
        response = self.client.get(reverse('entrepots:entrepot_detail', kwargs={'pk': self.entrepot.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hub Logistique Rades Port")
        self.assertContains(response, "Quai A-01")
        self.assertContains(response, "Quai Frigo F-01")

    def test_entrepot_create_requires_login(self):
        """Vérifie que la création d'entrepôt redirige vers /login/?next=... si non connecté."""
        response = self.client.get(reverse('entrepots:entrepot_create'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('login'), response.url)
        self.assertIn('next=', response.url)

    def test_entrepot_create_view(self):
        """C (Create) : Ajout d'un nouvel entrepôt avec validation."""
        self.client.force_login(self.user)
        create_data = {
            'nom': "Centre Logistique Sfax Sud",
            'code': "ENT-SFAX-02",
            'adresse': "Route de Gabès Km 4",
            'ville': "Sfax",
            'code_postal': "3000",
            'telephone': "+216 74 222 333",
            'email_contact': "sfax@cargolink.tn",
            'horaire_ouverture': "07:00",
            'horaire_fermeture': "21:00",
            'jours_ouverture': "Lundi - Vendredi",
            'capacite_palettes': 1800,
            'superficie_m2': 6500,
            'statut': "ACTIF",
            'gestionnaire': self.user.pk,
        }
        response = self.client.post(reverse('entrepots:entrepot_create'), data=create_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Entrepot.objects.filter(code="ENT-SFAX-02").exists())

    def test_entrepot_update_view(self):
        """U (Update) : Modification d'un entrepôt existant."""
        self.client.force_login(self.user)
        update_data = {
            'nom': "Hub Logistique Rades Port (Agrandissement)",
            'code': "ENT-RADES-01",
            'adresse': "Zone Portuaire, Terminal 3 & 4",
            'ville': "Rades",
            'code_postal': "2040",
            'telephone': "+216 71 111 222",
            'email_contact': "rades@cargolink.tn",
            'horaire_ouverture': "05:00",
            'horaire_fermeture': "23:00",
            'jours_ouverture': "7j/7",
            'capacite_palettes': 4500,
            'superficie_m2': 18000,
            'statut': "ACTIF",
            'gestionnaire': self.user.pk,
        }
        response = self.client.post(
            reverse('entrepots:entrepot_update', kwargs={'pk': self.entrepot.pk}),
            data=update_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.entrepot.refresh_from_db()
        self.assertEqual(self.entrepot.nom, "Hub Logistique Rades Port (Agrandissement)")
        self.assertEqual(self.entrepot.capacite_palettes, 4500)

    def test_entrepot_delete_view(self):
        """D (Delete) : Suppression d'un entrepôt et cascade."""
        self.client.force_login(self.user)
        pk = self.entrepot.pk
        response = self.client.post(reverse('entrepots:entrepot_delete', kwargs={'pk': pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Entrepot.objects.filter(pk=pk).exists())
        self.assertFalse(Quai.objects.filter(entrepot_id=pk).exists())


class QuaiCRUDTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='quai_operator',
            password='TestPassword123!'
        )
        self.entrepot = Entrepot.objects.create(
            nom="Plateforme Fret Tunis Nord",
            code="ENT-TUNIS-01",
            adresse="Zone Industrielle Charguia 2",
            ville="Tunis",
            code_postal="2035",
            capacite_palettes=2000
        )
        self.quai = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai B-01",
            type_quai="STANDARD",
            statut="DISPONIBLE",
            capacite_palettes_heure=30
        )

    def test_quai_list_view(self):
        """R (Read List) : Liste de tous les quais."""
        response = self.client.get(reverse('entrepots:quai_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Quai B-01")

    def test_quai_create_view(self):
        """C (Create) : Création d'un nouveau quai."""
        self.client.force_login(self.user)
        create_data = {
            'entrepot': self.entrepot.pk,
            'numero': "Quai ADR-09",
            'type_quai': "ADR",
            'statut': "DISPONIBLE",
            'capacite_camions_simultanes': 1,
            'capacite_palettes_heure': 20,
            'type_camion_accepte': "SEMI_REMORQUE",
            'a_niveleur': True,
            'a_sas_isotherme': False,
            'remarques': "Quai réservé aux produits chimiques et matières inflammables.",
        }
        response = self.client.post(reverse('entrepots:quai_create'), data=create_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Quai.objects.filter(numero="Quai ADR-09").exists())

    def test_quai_update_view(self):
        """U (Update) : Modification d'un quai."""
        self.client.force_login(self.user)
        update_data = {
            'entrepot': self.entrepot.pk,
            'numero': "Quai B-01 (Rénové)",
            'type_quai': "GROS_VOLUME",
            'statut': "OCCUPE",
            'capacite_camions_simultanes': 1,
            'capacite_palettes_heure': 40,
            'type_camion_accepte': "TOUS",
            'a_niveleur': True,
            'a_sas_isotherme': True,
            'remarques': "Nouveau sas installé.",
        }
        response = self.client.post(
            reverse('entrepots:quai_update', kwargs={'pk': self.quai.pk}),
            data=update_data,
            follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.quai.refresh_from_db()
        self.assertEqual(self.quai.numero, "Quai B-01 (Rénové)")
        self.assertEqual(self.quai.type_quai, "GROS_VOLUME")

    def test_quai_toggle_status_view(self):
        """Action rapide : bascule directe du statut du quai en 1 clic."""
        self.client.force_login(self.user)
        self.assertEqual(self.quai.statut, 'DISPONIBLE')
        
        # Bascule vers OCCUPE
        response = self.client.get(reverse('entrepots:quai_toggle_status', kwargs={'pk': self.quai.pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.quai.refresh_from_db()
        self.assertEqual(self.quai.statut, 'OCCUPE')

        # Bascule vers LIBRE
        response2 = self.client.get(reverse('entrepots:quai_toggle_status', kwargs={'pk': self.quai.pk}), follow=True)
        self.assertEqual(response2.status_code, 200)
        self.quai.refresh_from_db()
        self.assertEqual(self.quai.statut, 'DISPONIBLE')

    def test_quai_delete_view(self):
        """D (Delete) : Suppression d'un quai."""
        self.client.force_login(self.user)
        pk = self.quai.pk
        response = self.client.post(reverse('entrepots:quai_delete', kwargs={'pk': pk}), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Quai.objects.filter(pk=pk).exists())


class SmartCapacityOptimizerTests(TestCase):
    """
    Tests automatisés complets pour le module Smart Capacity Optimizer AI.
    Périmètre STRICT : Entrepot et Quai uniquement.
    """
    def setUp(self):
        self.user = User.objects.create_user(
            username='optimizer_manager',
            email='opt@cargolink.tn',
            password='Password123!'
        )
        self.user.profile.role = 'ENTREPOT'
        self.user.profile.save()

        # Entrepôt 1 : Radès Port (Saturé)
        self.ent1 = Entrepot.objects.create(
            nom="Hub Logistique Rades Port",
            code="ENT-RADES-OPT1",
            adresse="Zone Portuaire",
            ville="Rades",
            code_postal="2040",
            capacite_palettes=3000,
            superficie_m2=10000,
            statut="ACTIF",
            gestionnaire=self.user
        )
        self.q1_1 = Quai.objects.create(
            entrepot=self.ent1,
            numero="Quai R-01",
            type_quai="STANDARD",
            statut="OCCUPE",
            capacite_palettes_heure=30
        )
        self.q1_2 = Quai.objects.create(
            entrepot=self.ent1,
            numero="Quai R-02",
            type_quai="STANDARD",
            statut="OCCUPE",
            capacite_palettes_heure=30
        )

        # Entrepôt 2 : Radès Express (Sous-utilisé dans la même ville)
        self.ent2 = Entrepot.objects.create(
            nom="Plateforme Rades Express",
            code="ENT-RADES-OPT2",
            adresse="Avenue Habib Bourguiba",
            ville="Rades",
            code_postal="2040",
            capacite_palettes=2000,
            superficie_m2=8000,
            statut="ACTIF",
            gestionnaire=self.user
        )
        self.q2_1 = Quai.objects.create(
            entrepot=self.ent2,
            numero="Quai EXP-01",
            type_quai="STANDARD",
            statut="DISPONIBLE",
            capacite_palettes_heure=25
        )
        self.q2_2 = Quai.objects.create(
            entrepot=self.ent2,
            numero="Quai EXP-02",
            type_quai="STANDARD",
            statut="DISPONIBLE",
            capacite_palettes_heure=25
        )

    def test_capacity_analyzer_deterministic_metrics(self):
        """Vérifie l'exactitude des calculs déterministes de capacité et d'occupation."""
        from entrepots.services import CapacityAnalyzer
        analysis = CapacityAnalyzer.get_full_analysis()
        metrics = analysis['metrics']

        self.assertEqual(metrics['total_entrepots'], 2)
        self.assertEqual(metrics['total_quais'], 4)
        self.assertEqual(metrics['capacite_totale_palettes'], 5000)
        self.assertEqual(metrics['quais_occupes'], 2)
        self.assertEqual(metrics['quais_disponibles'], 2)
        self.assertEqual(metrics['taux_utilisation_quais_global'], 50.0)

        # Vérification des classifications
        ent1_data = next(w for w in analysis['warehouses'] if w['id'] == self.ent1.id)
        ent2_data = next(w for w in analysis['warehouses'] if w['id'] == self.ent2.id)

        self.assertEqual(ent1_data['utilization_pct'], 100.0)
        self.assertEqual(ent1_data['classification'], 'CRITIQUE')
        self.assertEqual(ent2_data['utilization_pct'], 0.0)
        self.assertEqual(ent2_data['classification'], 'SOUS_UTILISE')

    def test_city_imbalance_and_redistribution_opportunity(self):
        """Vérifie l'identification déterministe d'un déséquilibre dans la même ville."""
        from entrepots.services import CapacityAnalyzer, CapacityOptimizer
        analysis = CapacityAnalyzer.get_full_analysis()
        self.assertEqual(len(analysis['city_imbalances']), 1)
        self.assertEqual(analysis['city_imbalances'][0]['ville'], 'Rades')

        opportunities = CapacityOptimizer.find_feasible_redistributions(analysis)
        self.assertEqual(len(opportunities), 1)
        opp = opportunities[0]
        self.assertEqual(opp['source_id'], self.ent1.id)
        self.assertEqual(opp['target_id'], self.ent2.id)
        self.assertIn("Dévier 1 flux", opp['action_proposee'])

    def test_what_if_simulator_never_modifies_database(self):
        """Vérifie que le simulateur What-If calcule sans JAMAIS altérer la base de données."""
        from entrepots.services import CapacityOptimizer
        result = CapacityOptimizer.simulate_what_if(
            entrepot_id=self.ent1.id,
            proposed_capacite_palettes=4500,
            hypothetical_occupied_docks=1
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['capacite_palettes']['actuelle'], 3000)
        self.assertEqual(result['capacite_palettes']['proposee'], 4500)
        self.assertEqual(result['capacite_palettes']['delta'], 1500)
        self.assertEqual(result['capacite_palettes']['delta_pct'], 50.0)
        self.assertEqual(result['quais']['occupes_actuels'], 2)
        self.assertEqual(result['quais']['occupes_simules'], 1)
        self.assertEqual(result['quais']['taux_utilisation_apres'], 50.0)
        self.assertFalse(result['is_database_modified'])

        # Vérification en base : strictement inchangée !
        self.ent1.refresh_from_db()
        self.assertEqual(self.ent1.capacite_palettes, 3000)

    def test_what_if_simulator_handles_invalid_inputs(self):
        """Vérifie la robustesse du simulateur face aux saisies invalides."""
        from entrepots.services import CapacityOptimizer
        result = CapacityOptimizer.simulate_what_if(
            entrepot_id=self.ent1.id,
            proposed_capacite_palettes=-500
        )
        self.assertTrue(result['success'])
        self.assertEqual(result['faisabilite'], 'INVALIDE')
        self.assertTrue(len(result['erreurs']) > 0)

    def test_gemini_recommender_fallback_schema(self):
        """Vérifie que le moteur déterministe de repli respecte rigoureusement le schéma JSON."""
        from entrepots.services import CapacityAnalyzer, CapacityOptimizer, GeminiCapacityRecommender
        analysis = CapacityAnalyzer.get_full_analysis()
        opportunities = CapacityOptimizer.find_feasible_redistributions(analysis)

        fallback_result = GeminiCapacityRecommender._generate_deterministic_fallback(
            analysis, opportunities, reason="Test unitaire"
        )
        self.assertIn('summary', fallback_result)
        self.assertIn('recommendations', fallback_result)
        self.assertEqual(fallback_result['source'], 'deterministic_fallback')

        for rec in fallback_result['recommendations']:
            self.assertIn('id', rec)
            self.assertIn('title', rec)
            self.assertIn('description', rec)
            self.assertIn('affected_entity', rec)
            self.assertIn('detected_issue', rec)
            self.assertIn('supporting_metrics', rec)
            self.assertIn('recommended_action', rec)
            self.assertIn('expected_benefit', rec)
            self.assertIn('priority_level', rec)
            self.assertIn('category', rec)
            self.assertIn('is_actionable', rec)
            self.assertIn('constraints_or_missing_data', rec)
            self.assertIn('confidence_level', rec)

    def test_optimizer_dashboard_view_authenticated(self):
        """Vérifie l'accès au tableau de bord avec un utilisateur connecté."""
        self.client.force_login(self.user)
        response = self.client.get(reverse('entrepots:capacity_optimizer'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Smart Capacity Optimizer")
        self.assertContains(response, "État de Capacité par Entrepôt")
        self.assertContains(response, "Simulateur d'Hypothèses de Capacité (What-If)")

    def test_optimizer_simulate_api_post(self):
        """Vérifie l'API AJAX de simulation What-If."""
        self.client.force_login(self.user)
        import json
        payload = {
            'entrepot_id': self.ent1.id,
            'proposed_capacite_palettes': 4000,
            'hypothetical_occupied_docks': 1
        }
        response = self.client.post(
            reverse('entrepots:capacity_optimizer_simulate'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data['success'])
        self.assertEqual(data['capacite_palettes']['proposee'], 4000)

    def test_optimizer_action_api_review_and_dismiss(self):
        """Vérifie la gestion des recommandations via la session."""
        self.client.force_login(self.user)
        import json
        payload = {
            'rec_id': 'rec-1',
            'action': 'review'
        }
        res = self.client.post(
            reverse('entrepots:capacity_optimizer_action'),
            data=json.dumps(payload),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertTrue(data['success'])
        self.assertTrue(data['is_reviewed'])

        # Dismiss action
        res2 = self.client.post(
            reverse('entrepots:capacity_optimizer_action'),
            data=json.dumps({'rec_id': 'rec-1', 'action': 'dismiss'}),
            content_type='application/json'
        )
        self.assertEqual(res2.status_code, 200)
        self.assertTrue(res2.json()['is_dismissed'])
