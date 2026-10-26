from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from entrepots.models import Entrepot
from chauffeurs.models import Chauffeur, VisiteChauffeur


class Command(BaseCommand):
    help = "Peuple la base de données avec des profils de chauffeurs réalistes, camions associés et historiques de visites."

    def handle(self, *args, **options):
        self.stdout.write("Génération des profils de chauffeurs et historiques de passage...")

        # Transporteur / Utilisateur lié
        transporteur_user = User.objects.filter(username__in=['khalil', 'admin']).first()
        entrepots = list(Entrepot.objects.all())
        e_rades = next((e for e in entrepots if 'RADES' in e.code or 'Rades' in e.nom), entrepots[0] if entrepots else None)
        e_sfax = next((e for e in entrepots if 'SFAX' in e.code or 'Sfax' in e.nom), entrepots[1] if len(entrepots) > 1 else e_rades)
        e_sousse = next((e for e in entrepots if 'SOUSSE' in e.code or 'Sousse' in e.nom), entrepots[2] if len(entrepots) > 2 else e_rades)

        today = date.today()

        chauffeurs_data = [
            {
                'prenom': "Khalil",
                'nom': "Hlila",
                'cin': "08492011",
                'email': "khalil.hlila@cargolink.tn",
                'telephone': "+216 98 111 222",
                'telephone_urgence': "+216 50 111 999",
                'ville_residence': "Tunis",
                'date_embauche': date(2023, 1, 15),
                'numero_permis': "PERM-TN-849201",
                'categorie_permis': "C_CE_ADR",
                'date_delivrance_permis': date(2019, 5, 10),
                'date_expiration_permis': today + timedelta(days=420),
                'entreprise_transport': "Express Cargo Tunisie",
                'immatriculation_camion': "189-TN-7412",
                'marque_camion': "Volvo FH 500 Globetrotter",
                'type_camion': "SEMI_REMORQUE",
                'capacite_camion_tonnes': 26.0,
                'statut': "DISPONIBLE",
                'badge_acces_portuaire': True,
                'observations': "Conducteur référent. Habilitation matières dangereuses (ADR) classe 3 et 8. Badge portuaire Radès actif.",
            },
            {
                'prenom': "Tarak",
                'nom': "Mansour",
                'cin': "04871234",
                'email': "tarak.mansour@carthage-logistics.tn",
                'telephone': "+216 98 456 123",
                'telephone_urgence': "+216 22 456 000",
                'ville_residence': "Radès",
                'date_embauche': date(2022, 3, 1),
                'numero_permis': "PERM-TN-552019",
                'categorie_permis': "CE",
                'date_delivrance_permis': date(2018, 2, 20),
                'date_expiration_permis': today + timedelta(days=280),
                'entreprise_transport': "Carthage Logistics Fret",
                'immatriculation_camion': "210-TN-3390",
                'marque_camion': "Scania R450 Streamline",
                'type_camion': "SEMI_REMORQUE",
                'capacite_camion_tonnes': 24.5,
                'statut': "EN_MISSION",
                'badge_acces_portuaire': True,
                'observations': "Liaison régulière Tunis - Sfax - Gabès. Spécialité fret conteneurisé maritime.",
            },
            {
                'prenom': "Walid",
                'nom': "Bouazizi",
                'cin': "06912388",
                'email': "walid.bouazizi@sudexpress.tn",
                'telephone': "+216 55 987 654",
                'telephone_urgence': "+216 93 987 000",
                'ville_residence': "Sfax",
                'date_embauche': date(2023, 8, 10),
                'numero_permis': "PERM-TN-991044",
                'categorie_permis': "C",
                'date_delivrance_permis': date(2021, 6, 14),
                'date_expiration_permis': today + timedelta(days=190),
                'entreprise_transport': "Sud Express Fret",
                'immatriculation_camion': "175-TN-9854",
                'marque_camion': "Mercedes-Benz Actros 1845",
                'type_camion': "PORTEUR",
                'capacite_camion_tonnes': 18.0,
                'statut': "A_QUAI",
                'badge_acces_portuaire': True,
                'observations': "Présent sur le Hub de Sfax. Déchargement de palettes agroalimentaires.",
            },
            {
                'prenom': "Nader",
                'nom': "Gharbi",
                'cin': "09822314",
                'email': "nader.gharbi@sahel-distrib.tn",
                'telephone': "+216 93 112 233",
                'telephone_urgence': "+216 52 112 000",
                'ville_residence': "Sousse",
                'date_embauche': date(2024, 2, 1),
                'numero_permis': "PERM-TN-338120",
                'categorie_permis': "B",
                'date_delivrance_permis': date(2020, 11, 5),
                'date_expiration_permis': today + timedelta(days=14),  # Expire bientôt !
                'entreprise_transport': "Sahel Distribution Rapide",
                'immatriculation_camion': "162-TN-6021",
                'marque_camion': "Iveco Daily 35S18",
                'type_camion': "FOURGON",
                'capacite_camion_tonnes': 3.5,
                'statut': "DISPONIBLE",
                'badge_acces_portuaire': False,
                'observations': "⚠️ ALERTE : Permis arrivant à expiration dans 14 jours. Visite médicale programmée.",
            },
            {
                'prenom': "Sami",
                'nom': "Trabelsi",
                'cin': "03491823",
                'email': "sami.trabelsi@transmaghreb.tn",
                'telephone': "+216 22 334 455",
                'telephone_urgence': "+216 98 334 000",
                'ville_residence': "Bizerte",
                'date_embauche': date(2021, 9, 20),
                'numero_permis': "PERM-TN-109482",
                'categorie_permis': "CE",
                'date_delivrance_permis': date(2016, 4, 18),
                'date_expiration_permis': today + timedelta(days=610),
                'entreprise_transport': "Trans-Maghreb Cargo",
                'immatriculation_camion': "204-TN-1188",
                'marque_camion': "Renault Trucks T High 520",
                'type_camion': "FRIGORIFIQUE",
                'capacite_camion_tonnes': 22.0,
                'statut': "EN_REPOS",
                'badge_acces_portuaire': True,
                'observations': "Transport frigorifique sous température dirigée (-20°C / +4°C). Repos obligatoire de 45h.",
            },
            {
                'prenom': "Kamel",
                'nom': "Zouari",
                'cin': "01948201",
                'email': "kamel.zouari@fret-inter.tn",
                'telephone': "+216 29 887 766",
                'telephone_urgence': "+216 55 887 000",
                'ville_residence': "Sfax",
                'date_embauche': date(2020, 5, 12),
                'numero_permis': "PERM-TN-008129",
                'categorie_permis': "C",
                'date_delivrance_permis': date(2015, 8, 30),
                'date_expiration_permis': today - timedelta(days=5),  # Permis expiré !
                'entreprise_transport': "Tunis Fret International",
                'immatriculation_camion': "198-TN-4509",
                'marque_camion': "DAF XF 480 Super Space Cab",
                'type_camion': "SEMI_REMORQUE",
                'capacite_camion_tonnes': 25.0,
                'statut': "INACTIF",
                'badge_acces_portuaire': False,
                'observations': "🚨 CONDUCTEUR SUSPENDU : Permis échu il y a 5 jours. Interdiction de départ en mission jusqu'à renouvellement.",
            },
        ]

        chauffeurs_crees = []
        for data in chauffeurs_data:
            c, created = Chauffeur.objects.update_or_create(
                numero_permis=data['numero_permis'],
                defaults=data
            )
            chauffeurs_crees.append(c)
            action_text = "Créé" if created else "Mis à jour"
            self.stdout.write(f" - {action_text} : {c.nom_complet} ({c.numero_permis})")

        # Génération des visites / passages aux entrepôts
        self.stdout.write("Génération des visites et passages en entrepôt...")
        visites_data = [
            # Visites de Khalil Hlila
            {
                'chauffeur': chauffeurs_crees[0],
                'entrepot': e_rades,
                'quai_numero': "Quai A-01",
                'numero_bl': "CMR-TN-2026-901",
                'type_operation': "DECHARGEMENT",
                'statut': "TERMINE",
                'date_visite': today - timedelta(days=1),
                'heure_arrivee': time(8, 15),
                'heure_depart': time(9, 10),
                'duree_minutes': 55,
                'emargement_valide': True,
                'notes': "Livraison 32 palettes pièces de rechange automobile. Déchargement fluide par chariot frontal.",
            },
            {
                'chauffeur': chauffeurs_crees[0],
                'entrepot': e_sfax,
                'quai_numero': "Quai Sud-02",
                'numero_bl': "BL-2026-8810",
                'type_operation': "CHARGEMENT",
                'statut': "TERMINE",
                'date_visite': today - timedelta(days=4),
                'heure_arrivee': time(14, 0),
                'heure_depart': time(14, 45),
                'duree_minutes': 45,
                'emargement_valide': True,
                'notes': "Chargement export d'huile d'olive conditionnée. Contrôle des scellés validé.",
            },
            # Visites de Tarak Mansour
            {
                'chauffeur': chauffeurs_crees[1],
                'entrepot': e_rades,
                'quai_numero': "Quai F-02 (Frigo)",
                'numero_bl': "CMR-EXP-7741",
                'type_operation': "CHARGEMENT",
                'statut': "ARRIVE",
                'date_visite': today,
                'heure_arrivee': time(10, 30),
                'heure_depart': None,
                'duree_minutes': 40,
                'emargement_valide': False,
                'notes': "Camion enregistré à la guérite d'entrée. En attente de mise à quai.",
            },
            # Visites de Walid Bouazizi
            {
                'chauffeur': chauffeurs_crees[2],
                'entrepot': e_sfax,
                'quai_numero': "Quai Principal",
                'numero_bl': "BL-SFAX-4412",
                'type_operation': "DECHARGEMENT",
                'statut': "A_QUAI",
                'date_visite': today,
                'heure_arrivee': time(9, 0),
                'heure_depart': None,
                'duree_minutes': 60,
                'emargement_valide': True,
                'notes': "Déchargement en cours. Palette 1 à 18 réceptionnées sans avarie.",
            },
            # Visites de Sami Trabelsi
            {
                'chauffeur': chauffeurs_crees[4],
                'entrepot': e_sousse or e_rades,
                'quai_numero': "Quai Frigo 01",
                'numero_bl': "CMR-TN-3310",
                'type_operation': "DECHARGEMENT",
                'statut': "TERMINE",
                'date_visite': today - timedelta(days=2),
                'heure_arrivee': time(6, 45),
                'heure_depart': time(7, 30),
                'duree_minutes': 45,
                'emargement_valide': True,
                'notes': "Température contrôlée à cœur à -19.2°C conforme. Signature lettre de voiture effectuée.",
            },
        ]

        for vd in visites_data:
            VisiteChauffeur.objects.get_or_create(
                chauffeur=vd['chauffeur'],
                numero_bl=vd['numero_bl'],
                defaults=vd
            )

        self.stdout.write(self.style.SUCCESS(
            f"Succès ! {len(chauffeurs_crees)} chauffeurs et {len(visites_data)} visites de démonstration initialisés."
        ))
