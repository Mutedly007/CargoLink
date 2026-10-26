from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from camions.models import Camion, HistoriquePassage
from entrepots.models import Entrepot, Quai


class Command(BaseCommand):
    help = "Génère des camions et historiques de passages de démonstration réalistes pour CargoLink."

    def handle(self, *args, **options):
        self.stdout.write("Génération de la flotte de camions et des passages...")

        # Récupère un utilisateur transporteur ou admin
        user = User.objects.filter(profile__role='TRANSPORTEUR').first() or User.objects.first()
        today = date.today()
        now = timezone.now()

        entrepots = list(Entrepot.objects.all())
        e1 = entrepots[0] if len(entrepots) > 0 else None
        e2 = entrepots[1] if len(entrepots) > 1 else e1

        q1 = Quai.objects.filter(entrepot=e1).first() if e1 else None
        q2 = Quai.objects.filter(entrepot=e2).first() if e2 else q1

        # 1. Semi-remorque Volvo FH16 (Actif, Euro 6)
        c1, _ = Camion.objects.get_or_create(
            immatriculation="234 TUN 5678",
            defaults={
                'marque': "Volvo Trucks",
                'modele': "FH16 540 Globetrotter",
                'annee_fabrication': 2022,
                'type_camion': "SEMI_REMORQUE",
                'capacite_tonnage': 25.00,
                'volume_m3': 90,
                'capacite_palettes': 33,
                'etat': "DISPONIBLE",
                'kilometrage': 94500,
                'norme_anti_pollution': "EURO_6",
                'societe_transport': "TransMed Express",
                'transporteur': user,
                'date_derniere_maintenance': today - timedelta(days=45),
                'date_prochain_controle': today + timedelta(days=120),
            }
        )

        # 2. Camion Frigorifique Scania R450 (À Quai)
        c2, _ = Camion.objects.get_or_create(
            immatriculation="198 TUN 1124",
            defaults={
                'marque': "Scania",
                'modele': "R450 Highline Frigo",
                'annee_fabrication': 2021,
                'type_camion': "FRIGORIFIQUE",
                'capacite_tonnage': 22.50,
                'volume_m3': 85,
                'capacite_palettes': 30,
                'etat': "A_QUAI",
                'kilometrage': 142000,
                'norme_anti_pollution': "EURO_6",
                'societe_transport': "STAF Agro Logistics",
                'transporteur': user,
                'date_derniere_maintenance': today - timedelta(days=70),
                'date_prochain_controle': today + timedelta(days=10),  # Alerte urgente
            }
        )

        # 3. Porteur Mercedes Actros (En transit)
        c3, _ = Camion.objects.get_or_create(
            immatriculation="215 TUN 9931",
            defaults={
                'marque': "Mercedes-Benz",
                'modele': "Actros 1845 L",
                'annee_fabrication': 2023,
                'type_camion': "PORTEUR",
                'capacite_tonnage': 18.00,
                'volume_m3': 60,
                'capacite_palettes': 22,
                'etat': "EN_TRANSIT",
                'kilometrage': 48000,
                'norme_anti_pollution': "EURO_6",
                'societe_transport': "Express Fret Tunisie",
                'transporteur': user,
                'date_derniere_maintenance': today - timedelta(days=20),
                'date_prochain_controle': today + timedelta(days=220),
            }
        )

        # 4. Fourgon Renault Master Électrique (100% Zéro Émission)
        c4, _ = Camion.objects.get_or_create(
            immatriculation="241 TUN 3302",
            defaults={
                'marque': "Renault Trucks",
                'modele': "E-Tech Master City",
                'annee_fabrication': 2024,
                'type_camion': "FOURGON",
                'capacite_tonnage': 3.50,
                'volume_m3': 20,
                'capacite_palettes': 6,
                'etat': "DISPONIBLE",
                'kilometrage': 12000,
                'norme_anti_pollution': "ELECTRIQUE",
                'societe_transport': "GreenCargo Livraisons",
                'transporteur': user,
                'date_derniere_maintenance': today - timedelta(days=15),
                'date_prochain_controle': today + timedelta(days=340),
            }
        )

        # 5. Citerne DAF XF (En maintenance)
        c5, _ = Camion.objects.get_or_create(
            immatriculation="177 TUN 8450",
            defaults={
                'marque': "DAF",
                'modele': "XF 480 Super Space",
                'annee_fabrication': 2019,
                'type_camion': "CITERNE",
                'capacite_tonnage': 26.00,
                'volume_m3': 75,
                'capacite_palettes': 28,
                'etat': "EN_MAINTENANCE",
                'kilometrage': 285000,
                'norme_anti_pollution': "EURO_5",
                'societe_transport': "PetroTrans Maghreb",
                'transporteur': user,
                'date_derniere_maintenance': today - timedelta(days=12),
                'date_prochain_controle': today + timedelta(days=5),
            }
        )

        # Génération des historiques de passage
        if e1:
            HistoriquePassage.objects.get_or_create(
                camion=c1,
                date_entree=now - timedelta(days=3, hours=5),
                defaults={
                    'entrepot': e1,
                    'quai': q1,
                    'date_sortie': now - timedelta(days=3, hours=3, minutes=15),
                    'type_operation': "DECHARGEMENT",
                    'statut': "TERMINE",
                    'poids_mesure_kg': 24100,
                    'numero_bon_livraison': "BL-RADES-9921",
                    'observations': "Réception conforme 33 palettes de pièces détachées sans réserve."
                }
            )

        if e2:
            HistoriquePassage.objects.get_or_create(
                camion=c2,
                date_entree=now - timedelta(hours=1, minutes=20),
                defaults={
                    'entrepot': e2,
                    'quai': q2,
                    'date_sortie': None,
                    'type_operation': "CHARGEMENT",
                    'statut': "EN_COURS",
                    'poids_mesure_kg': 21850,
                    'numero_bon_livraison': "CMR-AGRO-7740",
                    'observations': "Opération en cours au quai sous température dirigée (-18°C)."
                }
            )

        self.stdout.write(self.style.SUCCESS("Génération terminée avec succès : 5 camions et passages créés."))
