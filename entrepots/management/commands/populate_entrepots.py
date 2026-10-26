from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from entrepots.models import Entrepot, Quai


class Command(BaseCommand):
    help = "Génère des entrepôts et des quais de démonstration réalistes pour CargoLink."

    def handle(self, *args, **options):
        # Récupère un gestionnaire d'entrepôt par défaut
        user = User.objects.filter(username__in=['aziz_logi', 'admin']).first()
        if not user:
            user = User.objects.first()

        self.stdout.write("Génération des données de démonstration...")

        # 1. Hub Logistique Port de Rades
        e1, _ = Entrepot.objects.get_or_create(
            code="ENT-RADES-01",
            defaults={
                'nom': "Hub Logistique Portuaire de Radès",
                'adresse': "Zone Portuaire - Terminal Conteneurs",
                'ville': "Radès",
                'code_postal': "2040",
                'telephone': "+216 71 448 100",
                'email_contact': "contact.rades@cargolink.tn",
                'horaire_ouverture': "06:00",
                'horaire_fermeture': "22:00",
                'jours_ouverture': "24h/24, 7j/7",
                'capacite_palettes': 4500,
                'superficie_m2': 16000,
                'statut': "ACTIF",
                'gestionnaire': user
            }
        )

        Quai.objects.get_or_create(
            entrepot=e1,
            numero="Quai A-01 (Import/Export)",
            defaults={
                'type_quai': "STANDARD",
                'statut': "DISPONIBLE",
                'capacite_palettes_heure': 33,
                'type_camion_accepte': "SEMI_REMORQUE",
                'a_niveleur': True,
                'a_sas_isotherme': True,
                'remarques': "Quai principal pour semi-remorques 40 tonnes."
            }
        )

        Quai.objects.get_or_create(
            entrepot=e1,
            numero="Quai F-02 (Frigorifique Fret)",
            defaults={
                'type_quai': "FRIGORIFIQUE",
                'statut': "OCCUPE",
                'capacite_palettes_heure': 26,
                'type_camion_accepte': "TOUS",
                'a_niveleur': True,
                'a_sas_isotherme': True,
                'remarques': "Contrôle continu de température (-20°C à +4°C)."
            }
        )

        Quai.objects.get_or_create(
            entrepot=e1,
            numero="Quai ADR-03 (Matières Spéciales)",
            defaults={
                'type_quai': "ADR",
                'statut': "RESERVE",
                'capacite_palettes_heure': 18,
                'type_camion_accepte': "SEMI_REMORQUE",
                'a_niveleur': True,
                'a_sas_isotherme': False,
                'remarques': "Équipé de buses extinctrices et bac de rétention."
            }
        )

        # 2. Centre Logistique Tunis Charguia
        e2, _ = Entrepot.objects.get_or_create(
            code="ENT-TUNIS-02",
            defaults={
                'nom': "Centre Logistique Tunis Aéroport",
                'adresse': "Zone Industrielle Charguia 2",
                'ville': "Tunis",
                'code_postal': "2035",
                'telephone': "+216 71 800 200",
                'email_contact': "charguia@cargolink.tn",
                'horaire_ouverture': "07:00",
                'horaire_fermeture': "20:00",
                'jours_ouverture': "Lundi - Samedi",
                'capacite_palettes': 2800,
                'superficie_m2': 9000,
                'statut': "ACTIF",
                'gestionnaire': user
            }
        )

        Quai.objects.get_or_create(
            entrepot=e2,
            numero="Quai Express 1",
            defaults={
                'type_quai': "STANDARD",
                'statut': "DISPONIBLE",
                'capacite_palettes_heure': 45,
                'type_camion_accepte': "FOURGON",
                'a_niveleur': True,
                'a_sas_isotherme': True,
                'remarques': "Dédié aux livraisons urbaines et messagerie rapide."
            }
        )

        Quai.objects.get_or_create(
            entrepot=e2,
            numero="Quai Lourd 2",
            defaults={
                'type_quai': "GROS_VOLUME",
                'statut': "DISPONIBLE",
                'capacite_palettes_heure': 30,
                'type_camion_accepte': "PORTEUR",
                'a_niveleur': True,
                'a_sas_isotherme': False,
                'remarques': "Accès pour camions porteurs et marchandises volumineuses."
            }
        )

        # 3. Plateforme Régionale Sfax Sud
        e3, _ = Entrepot.objects.get_or_create(
            code="ENT-SFAX-03",
            defaults={
                'nom': "Plateforme Agro-Logistique Sfax Sud",
                'adresse': "Route de Gabès Km 5",
                'ville': "Sfax",
                'code_postal': "3000",
                'telephone': "+216 74 610 900",
                'email_contact': "sfax@cargolink.tn",
                'horaire_ouverture': "05:30",
                'horaire_fermeture': "21:30",
                'jours_ouverture': "Lundi - Samedi",
                'capacite_palettes': 3600,
                'superficie_m2': 14000,
                'statut': "ACTIF",
                'gestionnaire': user
            }
        )

        Quai.objects.get_or_create(
            entrepot=e3,
            numero="Quai Froid Nord",
            defaults={
                'type_quai': "FRIGORIFIQUE",
                'statut': "DISPONIBLE",
                'capacite_palettes_heure': 28,
                'type_camion_accepte': "SEMI_REMORQUE",
                'a_niveleur': True,
                'a_sas_isotherme': True,
                'remarques': "Spécialisé export huile et produits frais."
            }
        )

        self.stdout.write(self.style.SUCCESS("[OK] Donnees de demonstration generees avec succes (3 entrepots, 6 quais)."))
