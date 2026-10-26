"""
Service d'optimisation déterministe et simulateur 'What-If'.
Périmètre STRICT : Modèles Entrepot et Quai uniquement.
Ne modifie JAMAIS la base de données de production.
"""
from typing import Dict, List, Any, Optional
from entrepots.models import Entrepot, Quai
from .capacity_analyzer import CapacityAnalyzer


class CapacityOptimizer:
    """
    Moteur d'optimisation déterministe de charge et simulateur d'hypothèses de capacité.
    """

    @classmethod
    def find_feasible_redistributions(cls, analysis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Identifie les rééquilibrages physiquement faisables entre entrepôts compatibles.
        Règles d'éligibilité :
        - Même ville (proximité géographique)
        - Entrepôts au statut 'ACTIF'
        - Un entrepôt en surcapacité/critique (>= 75%)
        - Un entrepôt sous-utilisé (<= 35%) avec des quais disponibles
        """
        opportunities = []
        city_imbalances = analysis_data.get('city_imbalances', [])

        for imbalance in city_imbalances:
            source = imbalance['surutilise']
            target = imbalance['sousutilise']

            source_obj = Entrepot.objects.filter(id=source['id']).first()
            target_obj = Entrepot.objects.filter(id=target['id']).first()

            if not source_obj or not target_obj:
                continue

            # Vérifier les types de quais compatibles
            source_quai_types = set(source_obj.quais.values_list('type_quai', flat=True))
            target_quai_types = set(target_obj.quais.filter(statut='DISPONIBLE').values_list('type_quai', flat=True))

            compatible_types = list(source_quai_types.intersection(target_quai_types))

            # Simulation de l'impact d'un délestage de 1 quai opérationnel
            target_dispo = target['nb_disponibles']
            if target_dispo > 0:
                # Si on transfère 1 charge opérationnelle
                simulated_source_occupes = max(0, source['nb_occupes'] - 1)
                simulated_source_util = round(
                    ((simulated_source_occupes + source['nb_reserves']) / max(1, source['quais_operationnels'])) * 100, 1
                )

                simulated_target_occupes = target['nb_occupes'] + 1
                simulated_target_util = round(
                    ((simulated_target_occupes + target['nb_reserves']) / max(1, target['quais_operationnels'])) * 100, 1
                )

                opportunities.append({
                    'id': f"redistrib_{source['id']}_{target['id']}",
                    'source_id': source['id'],
                    'source_nom': source['nom'],
                    'source_ville': source['ville'],
                    'source_util_actuelle': source['utilization_pct'],
                    'source_util_simulee': simulated_source_util,
                    'target_id': target['id'],
                    'target_nom': target['nom'],
                    'target_ville': target['ville'],
                    'target_util_actuelle': target['utilization_pct'],
                    'target_util_simulee': simulated_target_util,
                    'target_disponibles': target_dispo,
                    'types_compatibles': compatible_types,
                    'action_proposee': (
                        f"Dévier 1 flux de chargement/déchargement de {source['nom']} vers {target['nom']} "
                        f"({target['ville']}), qui dispose de {target_dispo} quai(s) libre(s)."
                    ),
                    'benefice_estime': (
                        f"Baisse de saturation sur {source['nom']} de {source['utilization_pct']}% à {simulated_source_util}%. "
                        f"Montée d'efficience sur {target['nom']} de {target['utilization_pct']}% à {simulated_target_util}%."
                    ),
                    'statut_faisabilite': "Faisable — Nécessite confirmation logistique du responsable",
                    'explication_contrainte': (
                        "Le modèle vérifie la compatibilité des équipements de quai et la même zone géographique. "
                        "Les autorisations d'accès physique et de planning doivent être validées avant mise en œuvre."
                    )
                })

        return opportunities

    @classmethod
    def simulate_what_if(
        cls,
        entrepot_id: int,
        proposed_capacite_palettes: Optional[int] = None,
        hypothetical_occupied_docks: Optional[int] = None,
        proposed_quai_throughput: Optional[int] = None,
        selected_quai_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Simulateur de scénarios 'What-If'.
        Calcule en mémoire les impacts hypothétiques sans JAMAIS modifier la base de données.
        """
        entrepot = Entrepot.objects.filter(id=entrepot_id).prefetch_related('quais').first()
        if not entrepot:
            return {'success': False, 'error': "Entrepôt introuvable."}

        quais = list(entrepot.quais.all())
        total_quais = len(quais)
        operational_quais = sum(1 for q in quais if q.statut != 'MAINTENANCE')
        current_occupied = sum(1 for q in quais if q.statut in ('OCCUPE', 'RESERVE'))
        current_available = sum(1 for q in quais if q.statut == 'DISPONIBLE')

        # 1. Simulation de la capacité palettes
        curr_cap = entrepot.capacite_palettes or 0
        prop_cap = proposed_capacite_palettes if proposed_capacite_palettes is not None else curr_cap

        validation_errors = []
        validation_warnings = []

        if prop_cap <= 0:
            validation_errors.append("La capacité en palettes proposée doit être un nombre strictement positif.")
        elif prop_cap > 500000:
            validation_warnings.append("Capacité très élevée : dépassement des dimensions habituelles des hubs régionaux.")

        delta_cap = prop_cap - curr_cap
        delta_cap_pct = round((delta_cap / curr_cap) * 100, 1) if curr_cap > 0 else 0.0

        # Vérification du ratio surface/palettes
        superficie = entrepot.superficie_m2 or 0
        density_before = round(superficie / curr_cap, 2) if curr_cap > 0 and superficie > 0 else None
        density_after = round(superficie / prop_cap, 2) if prop_cap > 0 and superficie > 0 else None

        if density_after and density_after < 0.8:
            validation_warnings.append(
                f"Alerte de densité : la configuration simulée atteint {density_after} m²/palette. "
                "Risque d'engorgement des allées de circulation pour les engins de manutention."
            )

        # 2. Simulation de l'occupation des quais
        if hypothetical_occupied_docks is not None:
            sim_occupied = max(0, min(hypothetical_occupied_docks, operational_quais))
            if hypothetical_occupied_docks > operational_quais:
                validation_warnings.append(
                    f"Le nombre de quais occupés simulé ({hypothetical_occupied_docks}) dépasse les quais opérationnels ({operational_quais}). "
                    f"La simulation est plafonnée à {operational_quais}."
                )
        else:
            sim_occupied = current_occupied

        # Calcul des taux d'utilisation avant / après
        if operational_quais > 0:
            util_before = round((current_occupied / operational_quais) * 100, 1)
            util_after = round((sim_occupied / operational_quais) * 100, 1)
            dispo_after = max(0, operational_quais - sim_occupied)
        else:
            util_before = 0.0
            util_after = 0.0
            dispo_after = 0

        # 3. Simulation spécifique à un quai (débit horaire)
        quai_sim_result = None
        if selected_quai_id and proposed_quai_throughput is not None:
            quai = next((q for q in quais if q.id == selected_quai_id), None)
            if quai:
                curr_tp = quai.capacite_palettes_heure or 0
                prop_tp = max(0, proposed_quai_throughput)
                delta_tp = prop_tp - curr_tp
                quai_sim_result = {
                    'quai_id': quai.id,
                    'quai_numero': quai.numero,
                    'debit_actuel': curr_tp,
                    'debit_propose': prop_tp,
                    'delta_debit': delta_tp,
                    'impact_journalier_estime': delta_tp * 14, # base 14h d'exploitation
                }

        # Détermination du statut de faisabilité
        if validation_errors:
            faisabilite = 'INVALIDE'
        elif validation_warnings:
            faisabilite = 'AVERTISSEMENT'
        else:
            faisabilite = 'OPTIMAL'

        return {
            'success': True,
            'entrepot': {
                'id': entrepot.id,
                'nom': entrepot.nom,
                'code': entrepot.code,
                'ville': entrepot.ville,
            },
            'capacite_palettes': {
                'actuelle': curr_cap,
                'proposee': prop_cap,
                'delta': delta_cap,
                'delta_pct': delta_cap_pct,
                'densite_avant': density_before,
                'densite_apres': density_after,
            },
            'quais': {
                'total': total_quais,
                'operationnels': operational_quais,
                'occupes_actuels': current_occupied,
                'occupes_simules': sim_occupied,
                'disponibles_actuels': current_available,
                'disponibles_simules': dispo_after,
                'taux_utilisation_avant': util_before,
                'taux_utilisation_apres': util_after,
                'delta_utilisation': round(util_after - util_before, 1),
            },
            'quai_simulation': quai_sim_result,
            'faisabilite': faisabilite,
            'erreurs': validation_errors,
            'avertissements': validation_warnings,
            'is_database_modified': False, # Rappel explicite
        }
