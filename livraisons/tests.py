import base64
import json
from datetime import date, datetime, time, timedelta
from io import StringIO
from unittest import mock

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from camions.models import Camion, HistoriquePassage
from chauffeurs.models import Chauffeur, VisiteChauffeur
from creneaux.models import Creneau
from entrepots.models import Entrepot, Quai

from . import geo, services
from .ai_service import DeepSeekLivraisonAI, recherche_locale, risque_local
from .models import IncidentLivraison, Livraison
from .services import TransitionImpossible
from .smart_assign import MoteurAffectation

# Plus petit PNG valide (1x1 pixel) : simule une signature dessinée sur le canvas
PNG_1PX = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=='
)
SIGNATURE = 'data:image/png;base64,' + base64.b64encode(PNG_1PX).decode()


def creer_utilisateur(username, role):
    user = User.objects.create_user(username=username, email=f'{username}@cargolink.tn', password='TestPassword123!')
    user.profile.role = role
    user.profile.save()
    return user


class LivraisonsTestBase(TestCase):
    """Jeu de données commun : 2 entrepôts, quais, camions, chauffeurs et utilisateurs de chaque rôle."""

    def setUp(self):
        self.planificateur = creer_utilisateur('eya_planif', 'PLANIFICATEUR')
        self.transporteur = creer_utilisateur('khalil_transp', 'TRANSPORTEUR')
        self.autre_transporteur = creer_utilisateur('autre_transp', 'TRANSPORTEUR')
        self.gestionnaire_sfax = creer_utilisateur('gest_sfax', 'ENTREPOT')

        self.rades = Entrepot.objects.create(
            nom="Hub Radès", code="ENT-RADES-T", adresse="Port", ville="Radès", code_postal="2040",
            horaire_ouverture=time(5, 0), horaire_fermeture=time(23, 0),
        )
        self.sfax = Entrepot.objects.create(
            nom="Plateforme Sfax Sud", code="ENT-SFAX-T", adresse="Route de Gabès", ville="Sfax", code_postal="3000",
            horaire_ouverture=time(5, 0), horaire_fermeture=time(23, 0), gestionnaire=self.gestionnaire_sfax,
        )
        self.quai_rades = Quai.objects.create(entrepot=self.rades, numero="A-01", type_quai='STANDARD')
        self.quai_rades_2 = Quai.objects.create(entrepot=self.rades, numero="A-02", type_quai='STANDARD')
        self.quai_sfax = Quai.objects.create(entrepot=self.sfax, numero="S-01", type_quai='STANDARD')
        self.quai_sfax_2 = Quai.objects.create(entrepot=self.sfax, numero="S-02", type_quai='STANDARD')

        self.semi = Camion.objects.create(
            immatriculation="234 TUN 5678", marque="Volvo", modele="FH16", type_camion='SEMI_REMORQUE',
            capacite_tonnage=25, capacite_palettes=33, etat='DISPONIBLE', norme_anti_pollution='EURO_6',
            societe_transport="Express Cargo Tunisie",
        )
        self.fourgon = Camion.objects.create(
            immatriculation="241 TUN 3302", marque="Renault", modele="Master", type_camion='FOURGON',
            capacite_tonnage=3.5, capacite_palettes=6, etat='DISPONIBLE', norme_anti_pollution='EURO_5',
        )
        self.camion_maintenance = Camion.objects.create(
            immatriculation="177 TUN 8450", marque="DAF", modele="XF", type_camion='SEMI_REMORQUE',
            capacite_tonnage=26, capacite_palettes=33, etat='EN_MAINTENANCE',
        )

        self.khalil = Chauffeur.objects.create(
            prenom="Khalil", nom="Hlila", telephone="+216 98 111 222", numero_permis="PERM-1",
            categorie_permis='C_CE_ADR', date_expiration_permis=date.today() + timedelta(days=400),
            entreprise_transport="Express Cargo Tunisie", immatriculation_camion="234 TUN 5678",
            type_camion='SEMI_REMORQUE', transporteur_user=self.transporteur,
        )
        self.nader = Chauffeur.objects.create(
            prenom="Nader", nom="Gharbi", telephone="+216 98 333 444", numero_permis="PERM-2",
            categorie_permis='B', date_expiration_permis=date.today() + timedelta(days=400),
        )
        self.kamel = Chauffeur.objects.create(
            prenom="Kamel", nom="Zouari", telephone="+216 98 555 666", numero_permis="PERM-3",
            categorie_permis='CE', date_expiration_permis=date.today() - timedelta(days=5),
        )

        demain = date.today() + timedelta(days=1)
        self.depart = timezone.make_aware(datetime.combine(demain, time(8, 30)))
        self.depart_form = f"{demain:%Y-%m-%d}T08:30"
        self.cr_chargement = Creneau.objects.create(
            entrepot=self.rades, quai=self.quai_rades, date_creneau=demain, heure_debut=time(7, 30),
            heure_fin=time(8, 30), type_operation='CHARGEMENT', statut='EN_ATTENTE',
            transporteur_nom="À affecter", immatriculation_camion="À affecter", chauffeur_nom="À affecter",
        )
        self.cr_dechargement = Creneau.objects.create(
            entrepot=self.sfax, quai=self.quai_sfax, date_creneau=demain, heure_debut=time(13, 0),
            heure_fin=time(14, 0), type_operation='DECHARGEMENT', statut='CONFIRME',
            transporteur_nom="À affecter", immatriculation_camion="À affecter", chauffeur_nom="À affecter",
        )

    def nouvelle_livraison(self, **kwargs):
        donnees = dict(
            type_livraison='INTER_ENTREPOT', entrepot_origine=self.rades, entrepot_destination=self.sfax,
            camion=self.semi, chauffeur=self.khalil, nb_palettes=24, poids_kg=18000,
            date_depart_prevue=self.depart, date_livraison_prevue=self.depart + timedelta(hours=5),
            creneau_chargement=self.cr_chargement, creneau_dechargement=self.cr_dechargement,
            numero_bl="BL-TEST-001", createur=self.planificateur,
        )
        donnees.update(kwargs)
        return Livraison.objects.create(**donnees)


# ==============================================================================
# 1. MODÈLE & RÈGLES DE GESTION
# ==============================================================================

class LivraisonReglesTests(LivraisonsTestBase):

    def test_reference_et_code_suivi_generes(self):
        livraison = self.nouvelle_livraison()
        self.assertTrue(livraison.reference.startswith('LIV-'))
        self.assertEqual(len(livraison.code_suivi), 8)
        self.assertNotIn('O', livraison.code_suivi)

    def test_livraison_valide_passe_la_validation(self):
        self.nouvelle_livraison().full_clean()

    def test_r1_charge_utile_depassee(self):
        livraison = self.nouvelle_livraison(camion=self.fourgon, chauffeur=self.nader, nb_palettes=4)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('poids_kg', ctx.exception.message_dict)

    def test_r2_capacite_palettes_depassee(self):
        livraison = self.nouvelle_livraison(camion=self.fourgon, chauffeur=self.nader, poids_kg=1000)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('nb_palettes', ctx.exception.message_dict)

    def test_r3_camion_en_maintenance_refuse(self):
        livraison = self.nouvelle_livraison(camion=self.camion_maintenance)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('camion', ctx.exception.message_dict)

    def test_r4_permis_expire_refuse(self):
        livraison = self.nouvelle_livraison(chauffeur=self.kamel)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('expiré', ctx.exception.message_dict['chauffeur'][0])

    def test_categorie_permis_insuffisante_pour_semi_remorque(self):
        livraison = self.nouvelle_livraison(chauffeur=self.nader)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('insuffisant', ctx.exception.message_dict['chauffeur'][0])

    def test_r5_matieres_dangereuses_exigent_habilitation_adr(self):
        self.khalil.categorie_permis = 'CE'
        self.khalil.save()
        livraison = self.nouvelle_livraison(type_marchandise='ADR')
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('ADR', ctx.exception.message_dict['chauffeur'][0])

    def test_r6_marchandise_frigorifique_exige_camion_frigorifique(self):
        livraison = self.nouvelle_livraison(type_marchandise='FRIGORIFIQUE')
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('camion', ctx.exception.message_dict)

    def test_r7_double_affectation_refusee(self):
        premiere = self.nouvelle_livraison(creneau_chargement=None, creneau_dechargement=None)
        premiere.statut = 'PLANIFIEE'
        premiere.save()
        seconde = self.nouvelle_livraison(
            creneau_chargement=None, creneau_dechargement=None,
            date_depart_prevue=self.depart + timedelta(hours=2), date_livraison_prevue=self.depart + timedelta(hours=7),
        )
        with self.assertRaises(ValidationError) as ctx:
            seconde.full_clean()
        self.assertIn('camion', ctx.exception.message_dict)
        self.assertIn('chauffeur', ctx.exception.message_dict)

    def test_r8_creneau_de_mauvais_type_ou_entrepot(self):
        livraison = self.nouvelle_livraison(creneau_chargement=self.cr_dechargement, creneau_dechargement=None)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('creneau_chargement', ctx.exception.message_dict)

    def test_r8_creneau_deja_lie_a_une_autre_livraison(self):
        self.nouvelle_livraison()
        autre = self.nouvelle_livraison(camion=None, chauffeur=None, creneau_dechargement=None)
        with self.assertRaises(ValidationError) as ctx:
            autre.full_clean()
        self.assertIn('creneau_chargement', ctx.exception.message_dict)

    def test_r9_echeance_avant_depart(self):
        livraison = self.nouvelle_livraison(date_livraison_prevue=self.depart - timedelta(hours=1))
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        self.assertIn('date_livraison_prevue', ctx.exception.message_dict)

    def test_r10_champs_obligatoires_livraison_client(self):
        livraison = self.nouvelle_livraison(type_livraison='CLIENT', entrepot_destination=None, creneau_dechargement=None)
        with self.assertRaises(ValidationError) as ctx:
            livraison.full_clean()
        for champ in ('destinataire_nom', 'adresse_livraison', 'ville_livraison'):
            self.assertIn(champ, ctx.exception.message_dict)

    def test_estimations_distance_eta_co2(self):
        livraison = self.nouvelle_livraison()
        self.assertTrue(200 < livraison.distance_km < 350)
        self.assertGreater(livraison.eta, livraison.date_depart_prevue)
        self.assertGreater(livraison.co2_estime_kg, 0)
        self.assertEqual(livraison.utilisation_capacite, 73)


# ==============================================================================
# 2. CYCLE DE VIE & INTÉGRATION AVEC LES MODULES DE L'ÉQUIPE
# ==============================================================================

class LivraisonCycleDeVieTests(LivraisonsTestBase):

    def test_scenario_nominal_rades_sfax(self):
        livraison = self.nouvelle_livraison()

        # Planification : créneau EN_ATTENTE confirmé + données recopiées pour Kacem et Khalil
        services.planifier(livraison, self.planificateur)
        self.cr_chargement.refresh_from_db()
        self.assertEqual(livraison.statut, 'PLANIFIEE')
        self.assertEqual(self.cr_chargement.statut, 'CONFIRME')
        self.assertEqual(self.cr_chargement.chauffeur_nom, "Khalil Hlila")
        self.assertEqual(self.cr_chargement.immatriculation_camion, "234 TUN 5678")

        # Chargement : créneau EN_COURS, quai occupé (code Kacem/Aziz), camion et chauffeur à quai
        services.charger(livraison, self.transporteur)
        self.cr_chargement.refresh_from_db(); self.quai_rades.refresh_from_db()
        self.semi.refresh_from_db(); self.khalil.refresh_from_db()
        self.assertEqual(self.cr_chargement.statut, 'EN_COURS')
        self.assertEqual(self.quai_rades.statut, 'OCCUPE')
        self.assertEqual(self.semi.etat, 'A_QUAI')
        self.assertEqual(self.khalil.statut, 'A_QUAI')

        # Départ : quai libéré, camion en transit, historiques de Rahma et Khalil alimentés
        services.partir(livraison, self.transporteur)
        self.cr_chargement.refresh_from_db(); self.quai_rades.refresh_from_db()
        self.semi.refresh_from_db(); self.khalil.refresh_from_db()
        self.assertEqual(self.cr_chargement.statut, 'TERMINE')
        self.assertEqual(self.quai_rades.statut, 'DISPONIBLE')
        self.assertEqual(self.semi.etat, 'EN_TRANSIT')
        self.assertEqual(self.khalil.statut, 'EN_MISSION')
        self.assertEqual(HistoriquePassage.objects.filter(camion=self.semi, type_operation='CHARGEMENT').count(), 1)
        self.assertEqual(VisiteChauffeur.objects.filter(chauffeur=self.khalil, entrepot=self.rades).count(), 1)
        self.assertIsNotNone(livraison.date_depart_reelle)

        # Arrivée : mise à quai à Sfax
        services.arriver(livraison, self.gestionnaire_sfax)
        self.cr_dechargement.refresh_from_db(); self.quai_sfax.refresh_from_db()
        self.assertEqual(self.cr_dechargement.statut, 'EN_COURS')
        self.assertEqual(self.quai_sfax.statut, 'OCCUPE')

        # Preuve de livraison obligatoire
        with self.assertRaises(TransitionImpossible):
            services.livrer(livraison, self.gestionnaire_sfax, receptionnaire_nom="Sami")
        services.livrer(livraison, self.gestionnaire_sfax, receptionnaire_nom="Sami", signature_data_url=SIGNATURE,
                        reserves="1 palette abîmée", conforme=False)
        livraison.refresh_from_db(); self.semi.refresh_from_db(); self.khalil.refresh_from_db()
        self.quai_sfax.refresh_from_db(); self.cr_dechargement.refresh_from_db()
        self.assertEqual(livraison.statut, 'LIVREE')
        self.assertTrue(livraison.signature.name.endswith('.png'))
        self.assertEqual(self.cr_dechargement.statut, 'TERMINE')
        self.assertEqual(self.quai_sfax.statut, 'DISPONIBLE')
        self.assertEqual(self.semi.etat, 'DISPONIBLE')
        self.assertEqual(self.khalil.statut, 'DISPONIBLE')
        self.assertEqual(HistoriquePassage.objects.filter(camion=self.semi).count(), 2)
        self.assertTrue(livraison.incidents.filter(type_incident='DOMMAGE').exists())
        self.assertEqual(livraison.suivis.count(), 5)

    def test_livraison_client_sans_creneau_de_dechargement(self):
        livraison = self.nouvelle_livraison(
            type_livraison='CLIENT', entrepot_destination=None, creneau_dechargement=None,
            destinataire_nom="Délice Sousse", adresse_livraison="Zone industrielle", ville_livraison="Sousse",
        )
        for etape in (services.planifier, services.charger, services.partir, services.arriver):
            etape(livraison, self.transporteur if etape != services.planifier else self.planificateur)
        services.livrer(livraison, self.transporteur, receptionnaire_nom="M. Ben Ali", signature_data_url=SIGNATURE)
        self.assertEqual(livraison.statut, 'LIVREE')
        passage = HistoriquePassage.objects.filter(camion=self.semi, type_operation='DECHARGEMENT').get()
        self.assertIsNone(passage.entrepot)

    def test_planifier_sans_affectation_impossible(self):
        livraison = self.nouvelle_livraison(camion=None, chauffeur=None)
        with self.assertRaises(TransitionImpossible):
            services.planifier(livraison, self.planificateur)
        self.assertEqual(livraison.statut, 'BROUILLON')

    def test_transition_dans_le_mauvais_ordre_refusee(self):
        livraison = self.nouvelle_livraison()
        with self.assertRaises(TransitionImpossible):
            services.partir(livraison, self.planificateur)

    def test_annulation_libere_les_creneaux(self):
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        services.annuler(livraison, self.planificateur, "Commande client reportée")
        self.cr_chargement.refresh_from_db(); self.cr_dechargement.refresh_from_db()
        self.assertEqual(livraison.statut, 'ANNULEE')
        self.assertEqual(self.cr_chargement.statut, 'ANNULE')
        self.assertEqual(self.cr_dechargement.statut, 'ANNULE')

    def test_annulation_impossible_en_transit(self):
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        services.charger(livraison, self.planificateur)
        services.partir(livraison, self.planificateur)
        with self.assertRaises(TransitionImpossible):
            services.annuler(livraison, self.planificateur, "Trop tard")

    def test_echec_cree_un_incident_et_libere_les_ressources(self):
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        services.charger(livraison, self.planificateur)
        services.partir(livraison, self.planificateur)
        services.echouer(livraison, self.transporteur, "Destinataire absent", 'ADRESSE_INTROUVABLE')
        self.semi.refresh_from_db(); self.cr_dechargement.refresh_from_db()
        self.assertEqual(livraison.statut, 'ECHEC')
        self.assertEqual(self.semi.etat, 'DISPONIBLE')
        self.assertEqual(self.cr_dechargement.statut, 'ANNULE')
        self.assertTrue(livraison.incidents.filter(type_incident='ADRESSE_INTROUVABLE').exists())

    def test_reaffectation_apres_panne(self):
        remplacant = Camion.objects.create(
            immatriculation="198 TUN 1124", marque="Scania", modele="R450", type_camion='SEMI_REMORQUE',
            capacite_tonnage=24, capacite_palettes=33, etat='DISPONIBLE',
        )
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        services.charger(livraison, self.planificateur)
        services.partir(livraison, self.planificateur)
        services.declarer_incident(livraison, self.transporteur, 'PANNE', 'CRITIQUE', "Moteur en panne à Enfidha")
        services.reaffecter(livraison, self.planificateur, camion=remplacant, ancien_camion_en_panne=True)
        self.semi.refresh_from_db(); remplacant.refresh_from_db()
        self.assertEqual(self.semi.etat, 'EN_MAINTENANCE')
        self.assertEqual(remplacant.etat, 'EN_TRANSIT')
        self.assertEqual(livraison.nb_incidents_ouverts, 0)

    def test_reservation_automatique_du_creneau_via_allocateur_kacem(self):
        livraison = self.nouvelle_livraison(creneau_chargement=None, creneau_dechargement=None)
        creneau, resultat = services.reserver_creneau_auto(livraison, self.planificateur, 'chargement')
        self.assertTrue(resultat['success'])
        self.assertEqual(creneau.type_operation, 'CHARGEMENT')
        self.assertEqual(creneau.statut, 'EN_ATTENTE')
        self.assertEqual(creneau.entrepot, self.rades)
        self.assertEqual(creneau.heure_fin, time(8, 30))
        self.assertEqual(livraison.creneau_chargement, creneau)
        # Le quai S-01 est déjà pris par un créneau existant : l'allocateur choisit S-02
        creneau2, _ = services.reserver_creneau_auto(livraison, self.planificateur, 'dechargement')
        self.assertEqual(creneau2.entrepot, self.sfax)
        self.assertEqual(creneau2.quai, self.quai_sfax_2)
        self.assertEqual(creneau2.heure_debut.minute % 15, 0)

    def test_detection_des_retards(self):
        livraison = self.nouvelle_livraison(
            creneau_chargement=None, creneau_dechargement=None,
            date_depart_prevue=timezone.now() - timedelta(hours=6),
            date_livraison_prevue=timezone.now() - timedelta(hours=1),
        )
        livraison.statut = 'EN_TRANSIT'
        livraison.save()
        nouvelles = services.marquer_retards()
        livraison.refresh_from_db()
        self.assertEqual(nouvelles, [livraison])
        self.assertTrue(livraison.est_en_retard)
        self.assertEqual(services.marquer_retards(), [])

    def test_creneau_deplace_par_un_autre_module_bloque_le_chargement(self):
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        # Simule l'affectation de mission du module Chauffeurs qui déplace le créneau vers un autre entrepôt
        Creneau.objects.filter(pk=self.cr_chargement.pk).update(entrepot=self.sfax, quai=self.quai_sfax_2)
        with self.assertRaises(TransitionImpossible):
            services.charger(livraison, self.planificateur)
        self.quai_sfax_2.refresh_from_db()
        self.assertEqual(self.quai_sfax_2.statut, 'DISPONIBLE')

    def test_signature_invalide_ignoree(self):
        self.assertIsNone(services._image_depuis_data_url('data:image/png;base64,PHN2Zz4=', 's.png'))
        self.assertIsNone(services._image_depuis_data_url('javascript:alert(1)', 's.png'))


# ==============================================================================
# 3. AFFECTATION INTELLIGENTE
# ==============================================================================

class AffectationIntelligenteTests(LivraisonsTestBase):

    def test_recommandation_respecte_les_contraintes(self):
        resultat = MoteurAffectation().recommander(
            poids_kg=18000, nb_palettes=24, debut=self.depart, fin=self.depart + timedelta(hours=5)
        )
        self.assertTrue(resultat['success'])
        meilleur = resultat['recommandations'][0]
        self.assertEqual(meilleur['camion_id'], self.semi.id)
        self.assertEqual(meilleur['chauffeur_id'], self.khalil.id)
        self.assertIn("Camion habituel du chauffeur", meilleur['points_forts'])
        exclus = {e['label'] for e in resultat['exclusions_camions']}
        self.assertIn(self.fourgon.immatriculation, exclus)
        self.assertIn("Kamel Zouari", {e['label'] for e in resultat['exclusions_chauffeurs']})

    def test_aucune_solution(self):
        resultat = MoteurAffectation().recommander(
            poids_kg=40000, nb_palettes=60, debut=self.depart, fin=self.depart + timedelta(hours=5)
        )
        self.assertFalse(resultat['success'])

    def test_api_affectation_reservee_aux_planificateurs(self):
        self.client.force_login(self.transporteur)
        reponse = self.client.post(reverse('livraisons:api_smart_assign'), {})
        self.assertEqual(reponse.status_code, 403)

    def test_api_affectation_calcule_l_echeance_si_absente(self):
        self.client.force_login(self.planificateur)
        reponse = self.client.post(reverse('livraisons:api_smart_assign'), {
            'type_livraison': 'INTER_ENTREPOT', 'entrepot_origine': self.rades.id,
            'entrepot_destination': self.sfax.id, 'date_depart_prevue': self.depart_form,
            'poids_kg': 18000, 'nb_palettes': 24, 'type_marchandise': 'STANDARD',
        })
        donnees = reponse.json()
        self.assertTrue(donnees['success'])
        self.assertEqual(donnees['explication']['source'], 'local')


# ==============================================================================
# 4. IA DEEPSEEK (API simulée) & MOTEURS LOCAUX
# ==============================================================================

def reponse_deepseek(contenu):
    reponse = mock.Mock(status_code=200)
    reponse.json.return_value = {'choices': [{'message': {'content': json.dumps(contenu)}}]}
    return reponse


class DeepSeekTests(LivraisonsTestBase):

    def test_sans_cle_repli_local(self):
        livraison = self.nouvelle_livraison()
        resultat = DeepSeekLivraisonAI(api_key='').analyser_risque(livraison)
        self.assertEqual(resultat['source'], 'local')

    @mock.patch('livraisons.ai_service.requests.post')
    def test_analyse_risque_valide_la_reponse(self, post):
        post.return_value = reponse_deepseek({
            'niveau': 'élevé', 'score': 250, 'facteurs': ['Trajet long', 42],
            'recommandations': ['Prévenir le client'], 'resume': 'Risque élevé.',
        })
        resultat = DeepSeekLivraisonAI(api_key='cle-test').analyser_risque(self.nouvelle_livraison())
        self.assertEqual(resultat['source'], 'deepseek')
        self.assertEqual(resultat['niveau'], 'eleve')
        self.assertEqual(resultat['score'], 100)
        self.assertEqual(resultat['facteurs'], ['Trajet long'])
        envoye = post.call_args.kwargs['json']
        self.assertEqual(envoye['response_format'], {'type': 'json_object'})
        self.assertNotIn('+216', envoye['messages'][1]['content'])

    @mock.patch('livraisons.ai_service.requests.post')
    def test_recherche_ia_filtre_les_valeurs_non_autorisees(self, post):
        post.return_value = reponse_deepseek({
            'statuts': ['EN_TRANSIT', 'DROP TABLE'], 'entrepot_id': 99999, 'priorite': 'URGENTE',
            'type_marchandise': 'PLUTONIUM', 'en_retard': True, 'date_du': 'pas-une-date',
            'explication': 'Livraisons urgentes en route',
        })
        resultat = DeepSeekLivraisonAI(api_key='cle-test').interpreter_recherche(
            "urgentes en route", list(Entrepot.objects.all())
        )
        self.assertEqual(resultat['filtres'], {'statut': ['EN_TRANSIT'], 'priorite': 'URGENTE', 'en_retard': True})

    @mock.patch('livraisons.ai_service.requests.post')
    def test_erreur_api_repli_local(self, post):
        post.return_value = mock.Mock(status_code=500, text='erreur')
        resultat = DeepSeekLivraisonAI(api_key='cle-test').rediger_message(self.nouvelle_livraison(), 'en')
        self.assertEqual(resultat['source'], 'local')
        self.assertIn('Hello', resultat['message'])

    def test_recherche_locale_comprend_une_phrase(self):
        resultat = recherche_locale("livraisons urgentes en retard vers Sfax cette semaine", list(Entrepot.objects.all()))
        filtres = resultat['filtres']
        self.assertEqual(filtres['priorite'], 'URGENTE')
        self.assertTrue(filtres['en_retard'])
        self.assertEqual(filtres['ville'], 'Sfax')
        self.assertIn('date_du', filtres)

    def test_risque_local_detecte_affectation_incomplete(self):
        resultat = risque_local(self.nouvelle_livraison(camion=None, chauffeur=None))
        self.assertTrue(any('incomplète' in f for f in resultat['facteurs']))

    def test_message_arabe(self):
        resultat = DeepSeekLivraisonAI(api_key='').rediger_message(self.nouvelle_livraison(), 'ar', 'retard')
        self.assertIn('نعتذر', resultat['message'])


# ==============================================================================
# 5. VUES, RÔLES & PÉRIMÈTRE
# ==============================================================================

class LivraisonVuesTests(LivraisonsTestBase):

    def test_anonyme_redirige_vers_accueil(self):
        reponse = self.client.get(reverse('livraisons:livraison_list'))
        self.assertRedirects(reponse, reverse('landing'))

    def test_planificateur_voit_le_tableau_de_bord(self):
        self.nouvelle_livraison()
        self.client.force_login(self.planificateur)
        reponse = self.client.get(reverse('livraisons:livraison_list'))
        self.assertContains(reponse, 'LIV-')

    def test_transporteur_ne_voit_que_ses_livraisons(self):
        mienne = self.nouvelle_livraison()
        autre = self.nouvelle_livraison(
            camion=self.fourgon, chauffeur=self.nader, nb_palettes=4, poids_kg=1000,
            creneau_chargement=None, creneau_dechargement=None,
        )
        self.client.force_login(self.transporteur)
        self.assertEqual(self.client.get(reverse('livraisons:livraison_detail', args=[mienne.pk])).status_code, 200)
        self.assertEqual(self.client.get(reverse('livraisons:livraison_detail', args=[autre.pk])).status_code, 404)
        self.client.force_login(self.autre_transporteur)
        self.assertEqual(self.client.get(reverse('livraisons:livraison_detail', args=[mienne.pk])).status_code, 404)

    def test_gestionnaire_ne_peut_pas_creer(self):
        self.client.force_login(self.gestionnaire_sfax)
        reponse = self.client.get(reverse('livraisons:livraison_create'))
        self.assertRedirects(reponse, reverse('livraisons:livraison_list'))

    def test_creation_via_formulaire_avec_echeance_automatique(self):
        self.client.force_login(self.planificateur)
        reponse = self.client.post(reverse('livraisons:livraison_create'), {
            'type_livraison': 'INTER_ENTREPOT', 'priorite': 'NORMALE',
            'entrepot_origine': self.rades.id, 'entrepot_destination': self.sfax.id,
            'type_marchandise': 'STANDARD', 'nb_palettes': 24, 'poids_kg': 18000,
            'date_depart_prevue': self.depart_form, 'date_livraison_prevue': '',
            'camion': self.semi.id, 'chauffeur': self.khalil.id, 'planifier': '1',
        })
        livraison = Livraison.objects.get()
        self.assertRedirects(reponse, reverse('livraisons:livraison_detail', args=[livraison.pk]))
        self.assertEqual(livraison.statut, 'PLANIFIEE')
        self.assertGreater(livraison.date_livraison_prevue, livraison.date_depart_prevue)

    def test_actions_uniquement_en_post(self):
        livraison = self.nouvelle_livraison()
        self.client.force_login(self.planificateur)
        reponse = self.client.get(reverse('livraisons:livraison_action', args=[livraison.pk, 'planifier']))
        self.assertEqual(reponse.status_code, 405)

    def test_transporteur_demarre_le_chargement_de_sa_livraison(self):
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        self.client.force_login(self.transporteur)
        self.client.post(reverse('livraisons:livraison_action', args=[livraison.pk, 'charger']))
        livraison.refresh_from_db()
        self.assertEqual(livraison.statut, 'EN_CHARGEMENT')

    def test_transporteur_ne_peut_pas_annuler(self):
        livraison = self.nouvelle_livraison()
        self.client.force_login(self.transporteur)
        self.client.post(reverse('livraisons:livraison_action', args=[livraison.pk, 'annuler']), {'motif': 'test'})
        livraison.refresh_from_db()
        self.assertEqual(livraison.statut, 'BROUILLON')

    def test_gestionnaire_destination_peut_receptionner(self):
        livraison = self.nouvelle_livraison()
        for etape in (services.planifier, services.charger, services.partir):
            etape(livraison, self.planificateur)
        self.client.force_login(self.gestionnaire_sfax)
        self.client.post(reverse('livraisons:livraison_action', args=[livraison.pk, 'arriver']))
        reponse = self.client.post(reverse('livraisons:livraison_pod', args=[livraison.pk]), {
            'receptionnaire_nom': 'Responsable quai', 'signature_data': SIGNATURE, 'livraison_conforme': 'on',
        })
        livraison.refresh_from_db()
        self.assertEqual(livraison.statut, 'LIVREE')
        self.assertRedirects(reponse, reverse('livraisons:livraison_detail', args=[livraison.pk]))

    def test_recherche_avancee_et_export_csv(self):
        self.nouvelle_livraison(priorite='URGENTE')
        self.nouvelle_livraison(camion=None, chauffeur=None, creneau_chargement=None, creneau_dechargement=None,
                                priorite='NORMALE', numero_bl='BL-AUTRE')
        self.client.force_login(self.planificateur)
        reponse = self.client.get(reverse('livraisons:livraison_list'), {'priorite': 'URGENTE'})
        self.assertEqual(len(reponse.context['livraisons']), 1)
        export = self.client.get(reverse('livraisons:livraison_export_csv'), {'q': 'BL-AUTRE'})
        contenu = export.content.decode('utf-8-sig')
        self.assertIn('BL-AUTRE', contenu)
        self.assertNotIn('BL-TEST-001', contenu)

    def test_recherche_ia_redirige_vers_les_filtres(self):
        self.client.force_login(self.planificateur)
        reponse = self.client.post(reverse('livraisons:api_recherche_ia'), {'texte': 'livraisons en retard vers Sfax'})
        url = reponse.json()['url']
        self.assertIn('en_retard=1', url)
        self.assertIn('ville=Sfax', url)

    def test_pages_detail_bon_et_missions(self):
        livraison = self.nouvelle_livraison()
        services.planifier(livraison, self.planificateur)
        self.client.force_login(self.planificateur)
        self.assertContains(self.client.get(reverse('livraisons:livraison_detail', args=[livraison.pk])), livraison.reference)
        self.assertContains(self.client.get(reverse('livraisons:bon_livraison', args=[livraison.pk])), 'BON DE LIVRAISON')
        self.client.force_login(self.transporteur)
        self.assertContains(self.client.get(reverse('livraisons:mes_missions')), 'Je suis à quai')


class SuiviPublicTests(LivraisonsTestBase):

    def test_suivi_public_sans_connexion_et_sans_donnees_personnelles(self):
        livraison = self.nouvelle_livraison(destinataire_telephone='+216 22 000 111')
        reponse = self.client.get(reverse('livraisons:suivi_public', args=[livraison.code_suivi]))
        self.assertEqual(reponse.status_code, 200)
        self.assertNotContains(reponse, '+216')
        self.assertNotContains(reponse, 'Hlila')

    def test_code_inconnu(self):
        reponse = self.client.get(reverse('livraisons:suivi_public', args=['XXXXXXXX']))
        self.assertEqual(reponse.status_code, 404)


class CommandesTests(LivraisonsTestBase):

    def test_populate_et_check_retards(self):
        sortie = StringIO()
        call_command('populate_livraisons', stdout=sortie)
        self.assertEqual(Livraison.objects.filter(numero_bl__startswith='DEMO-LIV-').count(), 6)
        call_command('check_retards_livraisons', '--dry-run', stdout=sortie)
        call_command('populate_livraisons', '--clear', stdout=sortie)
        self.assertFalse(Livraison.objects.exists())

    def test_geo_ville_inconnue(self):
        self.assertIsNone(geo.distance_km('Radès', 'Atlantide'))
        self.assertEqual(geo.normaliser_ville('Radès'), 'rades')
