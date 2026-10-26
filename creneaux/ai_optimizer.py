from datetime import datetime, date, time
from django.db.models import Count, Q
from entrepots.models import Entrepot, Quai
from .models import Creneau


class SmartDockAllocator:
    """
    Moteur d'Intelligence Artificielle pour l'Attribution Optimale des Quais (Module Kacem).
    Résout le problème d'affectation sous contraintes opérationnelles (Constraint Satisfaction & Multi-Criteria Optimization).
    
    Critères d'évaluation :
    1. Contraintes dures (Hard constraints) :
       - Disponibilité horaire stricte (détection de chevauchement temporelle)
       - Compatibilité gabarit véhicule (Semi-remorque, Porteur, Fourgon)
       - Compatibilité nature marchandise (Standard, Frigo, ADR)
       - Quai non en maintenance technique
    
    2. Critères d'optimisation souples (Soft weighted criteria) :
       - Débit palettes/heure adapté au volume (35%)
       - Équilibrage de charge / Load Balancing entre quais (30%)
       - Niveau d'équipements : Niveleur & Sas isotherme (25%)
       - Adéquation de gabarit spécifique (10%)
    """

    POIDS_DEBIT = 0.35
    POIDS_LOAD_BALANCING = 0.30
    POIDS_EQUIPEMENTS = 0.25
    POIDS_GABARIT = 0.10

    def recommend_best_dock(
        self,
        entrepot_id: int,
        date_creneau: date,
        heure_debut: time,
        heure_fin: time,
        type_marchandise: str = 'STANDARD',
        type_camion: str = 'SEMI_REMORQUE',
        nb_palettes: int = 10
    ) -> dict:
        """
        Calcule et retourne le quai optimal ainsi que le classement complet de tous les quais.
        """
        entrepot = Entrepot.objects.filter(id=entrepot_id).first()
        if not entrepot:
            return {
                'success': False,
                'message': "Entrepôt introuvable."
            }

        # Récupération de tous les quais de cet entrepôt
        quais = Quai.objects.filter(entrepot=entrepot)
        if not quais.exists():
            return {
                'success': False,
                'message': "Aucun quai configuré pour cet entrepôt."
            }

        # Nombre de créneaux déjà réservés sur chaque quai pour équilibrage de charge
        charge_par_quai = {
            row['quai_id']: row['nb']
            for row in Creneau.objects.filter(
                quai__in=quais,
                date_creneau=date_creneau
            ).exclude(statut='ANNULE').values('quai_id').annotate(nb=Count('id'))
        }
        max_charge = max(charge_par_quai.values()) if charge_par_quai else 0

        quais_analyses = []

        for q in quais:
            rejet_motif = self._verifier_contraintes_dures(
                q, date_creneau, heure_debut, heure_fin, type_marchandise, type_camion
            )
            
            if rejet_motif:
                quais_analyses.append({
                    'quai_id': q.id,
                    'numero': q.numero,
                    'type_quai': q.get_type_quai_display(),
                    'eligible': False,
                    'motif_rejet': rejet_motif,
                    'score': 0,
                    'details': {}
                })
                continue

            # Calcul du score multi-critères
            score_data = self._calculer_score_optimisation(
                q, nb_palettes, charge_par_quai.get(q.id, 0), max_charge, type_camion
            )

            quais_analyses.append({
                'quai_id': q.id,
                'numero': q.numero,
                'type_quai': q.get_type_quai_display(),
                'eligible': True,
                'motif_rejet': None,
                'score': score_data['score_global'],
                'details': score_data
            })

        # Filtrer les quais éligibles et les trier par score décroissant
        quais_eligibles = [q for q in quais_analyses if q['eligible']]
        quais_eligibles.sort(key=lambda x: x['score'], reverse=True)

        if not quais_eligibles:
            return {
                'success': False,
                'message': "Aucun quai disponible ou compatible sur ce créneau horaire.",
                'quais_analyses': quais_analyses
            }

        meilleur = quais_eligibles[0]

        # Construction des arguments d'explication IA
        arguments = []
        d = meilleur['details']
        if d['score_debit'] >= 80:
            arguments.append(f"Débit optimal ({d['debit_heure']} palettes/h) réduisant le temps d'attente")
        if d['score_charge'] >= 80:
            arguments.append("Quai le moins saturé de la journée (Équilibrage de charge)")
        if d['equipements_complets']:
            arguments.append("Équipé de niveleur hydraulique et sas d'étanchéité isotherme")
        if not arguments:
            arguments.append("Quai libre et compatible avec le gabarit du véhicule")

        return {
            'success': True,
            'meilleur_quai_id': meilleur['quai_id'],
            'meilleur_quai_numero': meilleur['numero'],
            'score_optimal': round(meilleur['score']),
            'explication': " • ".join(arguments),
            'criteres_valides': arguments,
            'quais_analyses': quais_analyses,
            'total_eligibles': len(quais_eligibles),
            'total_quais': len(quais)
        }

    def _verifier_contraintes_dures(
        self,
        quai: Quai,
        date_creneau: date,
        heure_debut: time,
        heure_fin: time,
        type_marchandise: str,
        type_camion: str
    ) -> str:
        """Vérifie si le quai respecte les contraintes strictes. Retourne le motif de rejet ou None."""
        if quai.statut == 'MAINTENANCE':
            return "Quai en maintenance technique"

        # Compatibilité marchandise
        if type_marchandise == 'FRIGORIFIQUE' and quai.type_quai != 'FRIGORIFIQUE':
            return "Non frigorifique (incompatible température dirigée)"
        if type_marchandise == 'ADR' and quai.type_quai != 'ADR':
            return "Non habilité matières dangereuses (ADR)"

        # Compatibilité gabarit
        if quai.type_camion_accepte != 'TOUS':
            if quai.type_camion_accepte != type_camion:
                return f"Gabarit non admis (réservé aux {quai.get_type_camion_accepte_display()})"

        # Détection de chevauchement horaire (aucun conflit)
        conflits = Creneau.objects.filter(
            quai=quai,
            date_creneau=date_creneau,
            heure_debut__lt=heure_fin,
            heure_fin__gt=heure_debut
        ).exclude(statut__in=['ANNULE', 'TERMINE'])

        if conflits.exists():
            c = conflits.first()
            return f"Occupé de {c.heure_debut.strftime('%H:%M')} à {c.heure_fin.strftime('%H:%M')}"

        return None

    def _calculer_score_optimisation(
        self,
        quai: Quai,
        nb_palettes: int,
        charge_quai: int,
        max_charge: int,
        type_camion: str
    ) -> dict:
        """Calcule la note pondérée sur 100 de chaque quai éligible."""
        # 1. Score Débit (35 pts max) : adéquation débit palettes/heure
        debit = quai.capacite_palettes_heure or 25
        # Débit optimal normalisé entre 10 et 50 pal/h
        score_debit = min(100, int((debit / 40.0) * 100))

        # 2. Score Équilibrage de charge (30 pts max)
        # Moins le quai a de créneaux sur la journée, plus le score est élevé
        if max_charge > 0:
            score_charge = int((1.0 - (charge_quai / (max_charge + 1))) * 100)
        else:
            score_charge = 100

        # 3. Score Équipements techniques (25 pts max)
        score_equip = 0
        if quai.a_niveleur:
            score_equip += 50
        if quai.a_sas_isotherme:
            score_equip += 50

        # 4. Score Gabarit spécifique (10 pts max)
        # Un quai dédié spécifiquement à ce type de camion a plus de points qu'un quai "TOUS"
        if quai.type_camion_accepte == type_camion:
            score_gabarit = 100
        else:
            score_gabarit = 80

        score_global = (
            (score_debit * self.POIDS_DEBIT) +
            (score_charge * self.POIDS_LOAD_BALANCING) +
            (score_equip * self.POIDS_EQUIPEMENTS) +
            (score_gabarit * self.POIDS_GABARIT)
        )

        return {
            'score_global': round(score_global, 1),
            'score_debit': score_debit,
            'score_charge': score_charge,
            'score_equipements': score_equip,
            'debit_heure': debit,
            'charge_creneaux_jour': charge_quai,
            'equipements_complets': quai.a_niveleur and quai.a_sas_isotherme
        }
