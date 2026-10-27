from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from camions.models import Camion
from chauffeurs.models import Chauffeur
from entrepots.models import Entrepot
from livraisons.models import IncidentLivraison, Livraison, SuiviLivraison

PREFIXE_DEMO = 'DEMO-LIV-'


class Command(BaseCommand):
    help = (
        "Crée des livraisons de démonstration (tous les statuts) à partir des entrepôts, camions et chauffeurs existants. "
        "Ne modifie aucune donnée des autres modules. Option --clear pour supprimer uniquement ces démos."
    )

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help="Supprime les livraisons de démonstration existantes.")

    def handle(self, *args, **options):
        demos = Livraison.objects.filter(numero_bl__startswith=PREFIXE_DEMO)
        if options['clear']:
            nb = demos.count()
            demos.delete()
            self.stdout.write(self.style.SUCCESS(f"{nb} livraison(s) de démonstration supprimée(s)."))
            return
        if demos.exists():
            self.stdout.write(self.style.WARNING("Des livraisons de démonstration existent déjà (utilisez --clear pour les recréer)."))
            return

        entrepots = list(Entrepot.objects.filter(statut='ACTIF').order_by('id'))
        if len(entrepots) < 2:
            self.stdout.write(self.style.ERROR("Il faut au moins 2 entrepôts actifs (lancez populate_entrepots)."))
            return

        def entrepot(ville, defaut):
            return next((e for e in entrepots if ville.lower() in e.ville.lower()), defaut)

        rades = entrepot('Rad', entrepots[0])
        tunis = entrepot('Tunis', entrepots[1])
        sfax = entrepot('Sfax', entrepots[-1] if entrepots[-1] not in (rades, tunis) else entrepots[1])

        def camion(etat=None, types=None):
            qs = Camion.objects.exclude(etat__in=('EN_MAINTENANCE', 'HORS_SERVICE'))
            if etat:
                qs = qs.filter(etat=etat)
            if types:
                qs = qs.filter(type_camion__in=types)
            return qs.first() or Camion.objects.exclude(etat__in=('EN_MAINTENANCE', 'HORS_SERVICE')).first()

        def chauffeur(statut=None, permis=('CE', 'C_CE_ADR')):
            qs = Chauffeur.objects.exclude(statut='INACTIF').filter(categorie_permis__in=permis)
            if statut:
                qs = qs.filter(statut=statut)
            return qs.first() or Chauffeur.objects.exclude(statut='INACTIF').filter(categorie_permis__in=permis).first()

        maintenant = timezone.now().replace(second=0, microsecond=0)
        scenarios = [
            {
                'statut': 'BROUILLON', 'origine': rades, 'destination': sfax, 'camion': None, 'chauffeur': None,
                'depart': maintenant + timedelta(days=1, hours=2), 'duree': timedelta(hours=5),
                'description': "Pièces automobiles (à affecter)", 'palettes': 24, 'poids': 18000, 'priorite': 'NORMALE',
                'suivi': "Livraison créée.",
            },
            {
                'statut': 'PLANIFIEE', 'origine': tunis, 'destination': rades, 'camion': camion('DISPONIBLE', ['FOURGON', 'PORTEUR']),
                'chauffeur': chauffeur('DISPONIBLE', ('B', 'C', 'CE', 'C_CE_ADR')),
                'depart': maintenant + timedelta(hours=4), 'duree': timedelta(hours=1, minutes=30),
                'description': "Colis express e-commerce", 'palettes': 4, 'poids': 1800, 'priorite': 'URGENTE',
                'suivi': "Livraison planifiée.",
            },
            {
                'statut': 'EN_TRANSIT', 'origine': rades, 'destination': sfax, 'camion': camion('EN_TRANSIT', ['SEMI_REMORQUE']),
                'chauffeur': chauffeur('EN_MISSION'),
                'depart': maintenant - timedelta(hours=1, minutes=30), 'duree': timedelta(hours=5),
                'description': "Électroménager", 'palettes': 26, 'poids': 15500, 'priorite': 'NORMALE',
                'suivi': "Départ du site.",
            },
            {
                'statut': 'LIVREE', 'origine': sfax, 'destination': tunis, 'camion': camion(types=['FRIGORIFIQUE']),
                'chauffeur': chauffeur(), 'type_marchandise': 'FRIGORIFIQUE',
                'depart': maintenant - timedelta(days=1, hours=8), 'duree': timedelta(hours=5),
                'description': "Produits laitiers", 'palettes': 18, 'poids': 9000, 'priorite': 'NORMALE',
                'suivi': "Livraison réceptionnée dans les délais.", 'retard': timedelta(minutes=-20),
            },
            {
                'statut': 'LIVREE', 'origine': tunis, 'destination': sfax, 'camion': camion(types=['PORTEUR', 'SEMI_REMORQUE']),
                'chauffeur': chauffeur(), 'depart': maintenant - timedelta(days=2, hours=6), 'duree': timedelta(hours=5),
                'description': "Matériaux de construction", 'palettes': 20, 'poids': 16000, 'priorite': 'NORMALE',
                'suivi': "Livraison réceptionnée avec 45 min de retard.", 'retard': timedelta(minutes=45),
            },
            {
                'statut': 'ECHEC', 'origine': rades, 'destination': None, 'camion': camion(types=['FOURGON', 'PORTEUR']),
                'chauffeur': chauffeur(permis=('B', 'C', 'CE', 'C_CE_ADR')),
                'depart': maintenant - timedelta(days=3, hours=4), 'duree': timedelta(hours=2),
                'description': "Mobilier de bureau", 'palettes': 5, 'poids': 2100, 'priorite': 'FLEXIBLE',
                'client': ("Bureau Plus Sousse", "Zone industrielle Sidi Abdelhamid", "Sousse"),
                'suivi': "Livraison en échec.", 'motif_echec': "Destinataire absent, entrepôt client fermé.",
            },
        ]

        creees = 0
        for i, s in enumerate(scenarios, start=1):
            depart = s['depart']
            livraison = Livraison(
                type_livraison='CLIENT' if s.get('client') else 'INTER_ENTREPOT',
                statut=s['statut'],
                priorite=s['priorite'],
                entrepot_origine=s['origine'],
                entrepot_destination=s['destination'],
                camion=s['camion'],
                chauffeur=s['chauffeur'],
                type_marchandise=s.get('type_marchandise', 'STANDARD'),
                description_marchandise=s['description'],
                nb_palettes=s['palettes'],
                poids_kg=s['poids'],
                numero_bl=f"{PREFIXE_DEMO}{i:03d}",
                date_depart_prevue=depart,
                date_livraison_prevue=depart + s['duree'],
                consignes="Livraison de démonstration générée par populate_livraisons.",
            )
            if s.get('client'):
                livraison.destinataire_nom, livraison.adresse_livraison, livraison.ville_livraison = s['client']
            if s['statut'] in ('EN_TRANSIT', 'LIVREE', 'ECHEC'):
                livraison.date_depart_reelle = depart + timedelta(minutes=10)
            if s['statut'] == 'LIVREE':
                livraison.date_arrivee_reelle = livraison.date_livraison_prevue + s['retard'] - timedelta(minutes=15)
                livraison.date_livraison_reelle = livraison.date_livraison_prevue + s['retard']
                livraison.est_en_retard = s['retard'] > timedelta(0)
                livraison.receptionnaire_nom = "Responsable réception"
            if s['statut'] == 'ECHEC':
                livraison.date_arrivee_reelle = livraison.date_livraison_prevue
                livraison.motif_echec = s['motif_echec']
            livraison.save()
            SuiviLivraison.objects.create(livraison=livraison, statut=s['statut'], commentaire=s['suivi'])
            if s['statut'] == 'ECHEC':
                IncidentLivraison.objects.create(
                    livraison=livraison, type_incident='ADRESSE_INTROUVABLE', gravite='CRITIQUE',
                    description=s['motif_echec'],
                )
            creees += 1
            self.stdout.write(f"  {livraison.reference} • {livraison.get_statut_display()} • {livraison.ville_depart} -> {livraison.ville_arrivee}")

        self.stdout.write(self.style.SUCCESS(f"{creees} livraisons de démonstration créées."))
