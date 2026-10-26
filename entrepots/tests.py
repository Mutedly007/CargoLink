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
