from datetime import date, time, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from entrepots.models import Entrepot, Quai
from creneaux.models import Creneau


class Command(BaseCommand):
    help = "Génère des créneaux horaires réalistes de démonstration pour CargoLink (Module Kacem)."

    def handle(self, *args, **options):
        self.stdout.write("Génération des créneaux de démonstration...")

        user = User.objects.filter(username__in=['kacem', 'aziz_logi', 'admin']).first()
        if not user:
            user = User.objects.first()

        entrepots = Entrepot.objects.all()
        if not entrepots.exists():
            self.stdout.write(self.style.WARNING("Aucun entrepôt trouvé. Veuillez exécuter 'python manage.py populate_entrepots' d'abord."))
            return

        today = date.today()
        demain = today + timedelta(days=1)
        apres_demain = today + timedelta(days=2)

        # Récupération de quais variés
        quais = Quai.objects.all()
        if not quais.exists():
            self.stdout.write(self.style.WARNING("Aucun quai trouvé."))
            return

        demo_slots = [
            # 1. En cours (À quai) aujourd'hui
            {
                'entrepot': quais[0].entrepot,
                'quai': quais[0],
                'date_creneau': today,
                'heure_debut': time(8, 30),
                'heure_fin': time(10, 0),
                'type_operation': 'DECHARGEMENT',
                'statut': 'EN_COURS',
                'priorite': 'URGENTE',
                'transporteur_nom': "SNTM Transports Maghreb",
                'immatriculation_camion': "189-TN-7412",
                'type_camion': 'SEMI_REMORQUE',
                'chauffeur_nom': "Tarak Mansour",
                'chauffeur_telephone': "+216 98 456 123",
                'type_marchandise': 'STANDARD',
                'nb_palettes': 33,
                'poids_kg': 18500,
                'numero_bl': "BL-2026-0891",
                'consignes': "Déchargement urgent composants industriels."
            },
            # 2. Arrivé sur site aujourd'hui
            {
                'entrepot': quais[1 % len(quais)].entrepot,
                'quai': quais[1 % len(quais)],
                'date_creneau': today,
                'heure_debut': time(10, 30),
                'heure_fin': time(12, 0),
                'type_operation': 'CHARGEMENT',
                'statut': 'ARRIVE',
                'priorite': 'NORMALE',
                'transporteur_nom': "Carthage Fret Express",
                'immatriculation_camion': "210-TN-3390",
                'type_camion': 'PORTEUR',
                'chauffeur_nom': "Walid Bouazizi",
                'chauffeur_telephone': "+216 55 987 654",
                'type_marchandise': 'PALETTES',
                'nb_palettes': 18,
                'poids_kg': 9200,
                'numero_bl': "CMR-TN-45210",
                'consignes': "Chargement produits finis pour Sousse."
            },
            # 3. Confirmé / Planifié pour cet après-midi
            {
                'entrepot': quais[0].entrepot,
                'quai': quais[0],
                'date_creneau': today,
                'heure_debut': time(14, 0),
                'heure_fin': time(15, 30),
                'type_operation': 'DECHARGEMENT',
                'statut': 'CONFIRME',
                'priorite': 'NORMALE',
                'transporteur_nom': "Euro-Tunisie Logistique",
                'immatriculation_camion': "175-TN-9854",
                'type_camion': 'SEMI_REMORQUE',
                'chauffeur_nom': "Sami Trabelsi",
                'chauffeur_telephone': "+216 22 334 455",
                'type_marchandise': 'STANDARD',
                'nb_palettes': 28,
                'poids_kg': 14000,
                'numero_bl': "BL-99432",
                'consignes': "Contrôle qualité à réception obligatoire."
            },
            # 4. En attente de validation (demande chauffeur)
            {
                'entrepot': quais[2 % len(quais)].entrepot,
                'quai': quais[2 % len(quais)],
                'date_creneau': demain,
                'heure_debut': time(9, 0),
                'heure_fin': time(10, 30),
                'type_operation': 'DECHARGEMENT',
                'statut': 'EN_ATTENTE',
                'priorite': 'NORMALE',
                'transporteur_nom': "Trans-Sahel Cargo",
                'immatriculation_camion': "204-TN-1188",
                'type_camion': 'SEMI_REMORQUE',
                'chauffeur_nom': "Nader Gharbi",
                'chauffeur_telephone': "+216 93 112 233",
                'type_marchandise': 'GROS_VOLUME',
                'nb_palettes': 24,
                'poids_kg': 16200,
                'numero_bl': "BL-SAHEL-771",
                'consignes': "Arrivée prévue depuis le port de Sfax."
            },
            # 5. Terminé (historique réussi)
            {
                'entrepot': quais[0].entrepot,
                'quai': quais[0],
                'date_creneau': today,
                'heure_debut': time(6, 30),
                'heure_fin': time(8, 0),
                'type_operation': 'DECHARGEMENT',
                'statut': 'TERMINE',
                'priorite': 'NORMALE',
                'transporteur_nom': "Méditerranée Transports",
                'immatriculation_camion': "162-TN-6021",
                'type_camion': 'FOURGON',
                'chauffeur_nom': "Houssem Riahi",
                'chauffeur_telephone': "+216 29 887 766",
                'type_marchandise': 'STANDARD',
                'nb_palettes': 8,
                'poids_kg': 3200,
                'numero_bl': "BL-MED-0034",
                'consignes': "Livraison express du matin."
            },
            # 6. Planifié pour après-demain
            {
                'entrepot': quais[1 % len(quais)].entrepot,
                'quai': quais[1 % len(quais)],
                'date_creneau': apres_demain,
                'heure_debut': time(11, 0),
                'heure_fin': time(12, 30),
                'type_operation': 'CHARGEMENT',
                'statut': 'CONFIRME',
                'priorite': 'FLEXIBLE',
                'transporteur_nom': "Atlas Freight Lines",
                'immatriculation_camion': "198-TN-4509",
                'type_camion': 'SEMI_REMORQUE',
                'chauffeur_nom': "Kamel Zouari",
                'chauffeur_telephone': "+216 52 441 122",
                'type_marchandise': 'STANDARD',
                'nb_palettes': 30,
                'poids_kg': 17500,
                'numero_bl': "CMR-ATL-550",
                'consignes': "Expédition vers la plateforme logistique Sud."
            }
        ]

        count = 0
        for data in demo_slots:
            statut_init = data.pop('statut')
            cr, created = Creneau.objects.get_or_create(
                entrepot=data['entrepot'],
                quai=data['quai'],
                date_creneau=data['date_creneau'],
                heure_debut=data['heure_debut'],
                defaults={**data, 'statut': statut_init, 'demandeur': user}
            )
            if created:
                count += 1
                cr._enregistrer_historique(statut_init, user, f"Création du créneau de démonstration ({statut_init})")
                # Si le créneau est en cours, marquer le quai occupé
                if statut_init == 'EN_COURS':
                    cr.quai.occuper()

        self.stdout.write(self.style.SUCCESS(f"{count} créneaux de démonstration créés avec succès !"))
