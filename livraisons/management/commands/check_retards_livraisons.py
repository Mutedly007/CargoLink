from django.core.management.base import BaseCommand
from django.utils import timezone

from livraisons.models import Livraison
from livraisons.services import marquer_retards


class Command(BaseCommand):
    help = (
        "Détecte les livraisons actives dont l'échéance est dépassée ou dont l'arrivée estimée "
        "dépasse l'échéance, et les signale en retard (à planifier toutes les 15 min : cron, tâche Windows ou n8n)."
    )

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help="Affiche les retards sans rien enregistrer.")

    def handle(self, *args, **options):
        if options['dry_run']:
            maintenant = timezone.now()
            candidates = [
                l for l in Livraison.objects.filter(
                    statut__in=('PLANIFIEE', 'EN_CHARGEMENT', 'EN_TRANSIT'), est_en_retard=False
                ).select_related('camion', 'entrepot_origine', 'entrepot_destination')
                if maintenant > l.date_livraison_prevue or l.eta > l.date_livraison_prevue
            ]
            for l in candidates:
                self.stdout.write(f"  [simulation] {l.reference} : retard projeté de {l.retard_minutes} min")
            self.stdout.write(self.style.WARNING(f"{len(candidates)} livraison(s) seraient signalées en retard."))
            return

        nouvelles = marquer_retards()
        for l in nouvelles:
            self.stdout.write(f"  {l.reference} ({l.ville_depart} -> {l.ville_arrivee}) : retard de {l.retard_minutes} min")
        self.stdout.write(self.style.SUCCESS(f"{len(nouvelles)} livraison(s) nouvellement signalée(s) en retard."))
