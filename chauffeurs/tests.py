from datetime import date, timedelta
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from entrepots.models import Entrepot, Quai
from camions.models import Camion
from creneaux.models import Creneau
from chauffeurs.models import Chauffeur, VisiteChauffeur
from chauffeurs.forms import ChauffeurForm, VisiteChauffeurForm


class ChauffeurModelTests(TestCase):
    def setUp(self):
        self.today = date.today()
        self.chauffeur = Chauffeur.objects.create(
            prenom="Khalil",
            nom="Hlila",
            cin="08492011",
            telephone="+216 98 111 222",
            numero_permis="PERM-TN-849201",
            categorie_permis="C_CE_ADR",
            date_delivrance_permis=self.today - timedelta(days=500),
            date_expiration_permis=self.today + timedelta(days=200),
            entreprise_transport="Express Cargo Tunisie",
            immatriculation_camion="189-TN-7412",
            marque_camion="Volvo FH 500",
            statut="DISPONIBLE"
        )

    def test_chauffeur_properties(self):
        self.assertEqual(self.chauffeur.nom_complet, "Khalil Hlila")
        self.assertEqual(self.chauffeur.initiales, "KH")
        self.assertFalse(self.chauffeur.est_permis_expire)
        self.assertFalse(self.chauffeur.expire_bientot)
        self.assertEqual(self.chauffeur.statut_validite_permis, "VALIDE")
        self.assertEqual(self.chauffeur.badge_statut_css, "status-badge-disponible")

    def test_permis_expiration_alerts(self):
        # Permis expirant dans 10 jours (< 30 jours)
        c_bientot = Chauffeur.objects.create(
            prenom="Chauffeur",
            nom="Bientot",
            telephone="+216 22 000 111",
            numero_permis="PERM-BIENTOT-01",
            categorie_permis="C",
            date_expiration_permis=self.today + timedelta(days=10),
            statut="DISPONIBLE"
        )
        self.assertTrue(c_bientot.expire_bientot)
        self.assertFalse(c_bientot.est_permis_expire)
        self.assertEqual(c_bientot.statut_validite_permis, "EXPIRE_BIENTOT")

        # Permis déjà expiré
        c_expire = Chauffeur.objects.create(
            prenom="Chauffeur",
            nom="Expire",
            telephone="+216 22 000 222",
            numero_permis="PERM-EXPIRE-01",
            categorie_permis="C",
            date_expiration_permis=self.today - timedelta(days=2),
            statut="INACTIF"
        )
        self.assertTrue(c_expire.est_permis_expire)
        self.assertEqual(c_expire.statut_validite_permis, "EXPIRE")


class ChauffeurCRUDViewsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.today = date.today()

        self.entrepot = Entrepot.objects.create(
            nom="Hub Logistique Test",
            code="ENT-TEST-01",
            adresse="Zone Industrielle",
            ville="Tunis",
            code_postal="1000",
            statut="ACTIF"
        )

        self.chauffeur = Chauffeur.objects.create(
            prenom="Khalil",
            nom="Hlila",
            telephone="+216 98 111 222",
            numero_permis="PERM-TN-849201",
            categorie_permis="CE",
            date_delivrance_permis=self.today - timedelta(days=365),
            date_expiration_permis=self.today + timedelta(days=180),
            entreprise_transport="Express Cargo",
            immatriculation_camion="189-TN-7412",
            statut="DISPONIBLE"
        )

        self.visite = VisiteChauffeur.objects.create(
            chauffeur=self.chauffeur,
            entrepot=self.entrepot,
            quai_numero="Quai 1",
            numero_bl="BL-12345",
            type_operation="DECHARGEMENT",
            statut="TERMINE",
            date_visite=self.today
        )

        self.user = User.objects.create_user(
            username="test_chauffeur",
            password="password123",
            email="test_chauffeur@cargolink.tn"
        )
        self.user.profile.role = "TRANSPORTEUR"
        self.user.profile.save()
        self.client.login(username="test_chauffeur", password="password123")

    def test_chauffeur_list_unauthenticated_redirects_to_landing(self):
        """Vérifie qu'un utilisateur non connecté est redirigé vers la page d'accueil principale."""
        self.client.logout()
        response = self.client.get(reverse('chauffeurs:chauffeur_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_chauffeur_list_non_chauffeur_redirects_to_landing(self):
        """Vérifie qu'un utilisateur sans session chauffeur (ex: gestionnaire entrepôt) est redirigé vers la landing page."""
        self.client.logout()
        other_user = User.objects.create_user(
            username="test_entrepot",
            password="password123",
            email="entrepot@cargolink.tn"
        )
        other_user.profile.role = "ENTREPOT"
        other_user.profile.save()
        self.client.login(username="test_entrepot", password="password123")

        response = self.client.get(reverse('chauffeurs:chauffeur_list'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('landing'))

    def test_chauffeur_list_view(self):
        response = self.client.get(reverse('chauffeurs:chauffeur_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Khalil Hlila")
        self.assertContains(response, "189-TN-7412")
        self.assertEqual(response.context['total_chauffeurs'], 1)

    def test_chauffeur_search_and_filter(self):
        # Search match
        response = self.client.get(reverse('chauffeurs:chauffeur_list'), {'q': 'Khalil'})
        self.assertEqual(len(response.context['chauffeurs']), 1)

        # Search no match
        response = self.client.get(reverse('chauffeurs:chauffeur_list'), {'q': 'Inexistant'})
        self.assertEqual(len(response.context['chauffeurs']), 0)

        # Filter by statut
        response = self.client.get(reverse('chauffeurs:chauffeur_list'), {'statut': 'DISPONIBLE'})
        self.assertEqual(len(response.context['chauffeurs']), 1)
        response = self.client.get(reverse('chauffeurs:chauffeur_list'), {'statut': 'INACTIF'})
        self.assertEqual(len(response.context['chauffeurs']), 0)

    def test_chauffeur_detail_view(self):
        response = self.client.get(reverse('chauffeurs:chauffeur_detail', kwargs={'pk': self.chauffeur.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Khalil Hlila")
        self.assertContains(response, "BL-12345")
        self.assertEqual(len(response.context['visites']), 1)

    def test_chauffeur_create_view(self):
        url = reverse('chauffeurs:chauffeur_create')
        # GET
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # POST
        data = {
            'prenom': "Nouveau",
            'nom': "Chauffeur",
            'cin': "11223344",
            'email': "nouveau@cargolink.tn",
            'telephone': "+216 55 123 456",
            'ville_residence': "Sousse",
            'date_embauche': self.today,
            'numero_permis': "PERM-NOUV-01",
            'categorie_permis': "C",
            'date_delivrance_permis': self.today - timedelta(days=200),
            'date_expiration_permis': self.today + timedelta(days=300),
            'entreprise_transport': "Transport Rapide",
            'immatriculation_camion': "199-TN-1111",
            'marque_camion': "Scania",
            'type_camion': "PORTEUR",
            'capacite_camion_tonnes': 19.0,
            'statut': "DISPONIBLE",
            'badge_acces_portuaire': True,
        }
        post_response = self.client.post(url, data)
        self.assertEqual(post_response.status_code, 302)
        self.assertTrue(Chauffeur.objects.filter(numero_permis="PERM-NOUV-01").exists())

    def test_chauffeur_update_view(self):
        url = reverse('chauffeurs:chauffeur_update', kwargs={'pk': self.chauffeur.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        data = {
            'prenom': "Khalil",
            'nom': "Hlila",
            'cin': "08492011",
            'telephone': "+216 98 999 888",  # updated phone
            'ville_residence': "Tunis",
            'date_embauche': self.today,
            'numero_permis': "PERM-TN-849201",
            'categorie_permis': "CE",
            'date_delivrance_permis': self.today - timedelta(days=365),
            'date_expiration_permis': self.today + timedelta(days=180),
            'entreprise_transport': "Express Cargo Tunisie",
            'immatriculation_camion': "189-TN-7412",
            'marque_camion': "Volvo FH 500",
            'type_camion': "SEMI_REMORQUE",
            'capacite_camion_tonnes': 26.0,
            'statut': "EN_MISSION",  # updated status
        }
        post_response = self.client.post(url, data)
        self.assertEqual(post_response.status_code, 302)
        self.chauffeur.refresh_from_db()
        self.assertEqual(self.chauffeur.telephone, "+216 98 999 888")
        self.assertEqual(self.chauffeur.statut, "EN_MISSION")

    def test_chauffeur_statut_quick_update(self):
        url = reverse('chauffeurs:chauffeur_statut_update', kwargs={'pk': self.chauffeur.pk})
        response = self.client.post(url, {'nouveau_statut': 'A_QUAI'})
        self.assertEqual(response.status_code, 302)
        self.chauffeur.refresh_from_db()
        self.assertEqual(self.chauffeur.statut, 'A_QUAI')

    def test_visite_create_view(self):
        url = reverse('chauffeurs:visite_create', kwargs={'chauffeur_pk': self.chauffeur.pk})
        data = {
            'entrepot': self.entrepot.pk,
            'quai_numero': "Quai Sud",
            'numero_bl': "BL-NEW-999",
            'type_operation': "CHARGEMENT",
            'statut': "TERMINE",
            'date_visite': self.today,
            'duree_minutes': 45,
            'emargement_valide': True,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(VisiteChauffeur.objects.filter(numero_bl="BL-NEW-999").exists())

    def test_chauffeur_portal_mobile_view(self):
        response = self.client.get(reverse('chauffeurs:chauffeur_portal_mobile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Mon Espace Chauffeur")
        self.assertContains(response, "Disponible")
        self.assertContains(response, "En Route / Mission")

    def test_chauffeurs_export_view(self):
        response = self.client.get(reverse('chauffeurs:chauffeurs_export'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        content = response.content.decode('utf-8')
        self.assertIn("Nom Complet", content)
        self.assertIn("Khalil Hlila", content)

    def test_chauffeur_delete_view(self):
        url = reverse('chauffeurs:chauffeur_delete', kwargs={'pk': self.chauffeur.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Chauffeur.objects.filter(pk=self.chauffeur.pk).exists())

    def test_chauffeur_affecter_mission_success(self):
        quai = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai A-01",
            statut="DISPONIBLE"
        )
        camion = Camion.objects.create(
            immatriculation="205-TN-9999",
            marque="Mercedes-Benz",
            modele="Actros",
            etat="DISPONIBLE",
            type_camion="SEMI_REMORQUE",
            capacite_tonnage=26.0
        )
        url = reverse('chauffeurs:chauffeur_affecter_mission', kwargs={'pk': self.chauffeur.pk})
        data = {
            'camion_id': camion.pk,
            'quai_id': quai.pk,
            'type_operation': 'DECHARGEMENT'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.chauffeur.refresh_from_db()
        camion.refresh_from_db()
        self.assertEqual(self.chauffeur.statut, 'EN_MISSION')
        self.assertEqual(self.chauffeur.immatriculation_camion, "205-TN-9999")
        self.assertEqual(camion.etat, 'EN_TRANSIT')
        self.assertTrue(Creneau.objects.filter(immatriculation_camion="205-TN-9999", quai=quai).exists())
        self.assertTrue(VisiteChauffeur.objects.filter(chauffeur=self.chauffeur, quai_numero="Quai A-01").exists())

    def test_chauffeur_affecter_mission_camion_indisponible_rejete(self):
        quai = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai B-02",
            statut="DISPONIBLE"
        )
        camion_occupe = Camion.objects.create(
            immatriculation="210-TN-8888",
            marque="Volvo",
            modele="FH",
            etat="EN_TRANSIT",
            type_camion="SEMI_REMORQUE"
        )
        url = reverse('chauffeurs:chauffeur_affecter_mission', kwargs={'pk': self.chauffeur.pk})
        data = {
            'camion_id': camion_occupe.pk,
            'quai_id': quai.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.chauffeur.refresh_from_db()
        self.assertEqual(self.chauffeur.statut, 'DISPONIBLE')

    def test_chauffeur_affecter_mission_quai_indisponible_rejete(self):
        quai_occupe = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai C-03",
            statut="OCCUPE"
        )
        camion = Camion.objects.create(
            immatriculation="215-TN-7777",
            marque="Scania",
            modele="R500",
            etat="DISPONIBLE",
            type_camion="SEMI_REMORQUE"
        )
        url = reverse('chauffeurs:chauffeur_affecter_mission', kwargs={'pk': self.chauffeur.pk})
        data = {
            'camion_id': camion.pk,
            'quai_id': quai_occupe.pk,
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)

        self.chauffeur.refresh_from_db()
        self.assertEqual(self.chauffeur.statut, 'DISPONIBLE')
        camion.refresh_from_db()
        self.assertEqual(camion.etat, 'DISPONIBLE')

    def test_chauffeur_liberer_mission(self):
        quai = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai D-04",
            statut="RESERVE"
        )
        camion = Camion.objects.create(
            immatriculation="220-TN-6666",
            marque="Renault",
            modele="T",
            etat="EN_TRANSIT",
            type_camion="SEMI_REMORQUE"
        )
        self.chauffeur.statut = "EN_MISSION"
        self.chauffeur.immatriculation_camion = camion.immatriculation
        self.chauffeur.save()

        creneau = Creneau.objects.create(
            entrepot=self.entrepot,
            quai=quai,
            date_creneau=self.today,
            heure_debut="10:00",
            heure_fin="12:00",
            statut="CONFIRME",
            chauffeur_nom=self.chauffeur.nom_complet,
            immatriculation_camion=camion.immatriculation,
            transporteur_nom="Express Cargo"
        )

        url = reverse('chauffeurs:chauffeur_liberer_mission', kwargs={'pk': self.chauffeur.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.chauffeur.refresh_from_db()
        camion.refresh_from_db()
        quai.refresh_from_db()
        creneau.refresh_from_db()

        self.assertEqual(self.chauffeur.statut, 'DISPONIBLE')
        self.assertEqual(camion.etat, 'DISPONIBLE')
        self.assertEqual(quai.statut, 'DISPONIBLE')
        self.assertEqual(creneau.statut, 'TERMINE')

    def test_chauffeur_affecter_mission_with_next_chauffeur_detail_redirects_properly(self):
        quai = Quai.objects.create(
            entrepot=self.entrepot,
            numero="Quai E-05",
            statut="DISPONIBLE"
        )
        camion = Camion.objects.create(
            immatriculation="230-TN-5555",
            marque="DAF",
            modele="XF",
            etat="DISPONIBLE",
            type_camion="SEMI_REMORQUE"
        )
        url = reverse('chauffeurs:chauffeur_affecter_mission', kwargs={'pk': self.chauffeur.pk})
        data = {
            'camion_id': camion.pk,
            'quai_id': quai.pk,
            'next': 'chauffeurs:chauffeur_detail',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('chauffeurs:chauffeur_detail', kwargs={'pk': self.chauffeur.pk}))


