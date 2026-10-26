"""
Service d'analyse déterministe de capacité pour CargoLink.
Périmètre STRICT : Modèles Entrepot et Quai uniquement.
Aucune dépendance vers d'autres modules métier.
"""
from typing import Dict, List, Any, Optional
from django.db.models import Sum, Count, Q
from entrepots.models import Entrepot, Quai


class CapacityAnalyzer:
    """
    Moteur d'analyse déterministe de capacité et de détection d'anomalies.
    Applique des formules mathématiques fiables et des seuils explicites.
    """

    # Seuils configurables explicites
    UNDERUTILIZED_THRESHOLD = 35.0   # Taux d'utilisation <= 35% : Sous-utilisé
    NEAR_CAPACITY_THRESHOLD = 75.0   # Taux d'utilisation >= 75% : Proche saturation
    CRITICAL_THRESHOLD = 90.0        # Taux d'utilisation >= 90% : Critique / Bloquant
    HIGH_DOWNTIME_THRESHOLD = 50.0   # >= 50% des quais en maintenance : Indisponibilité critique

    @classmethod
    def get_full_analysis(cls) -> Dict[str, Any]:
        """
        Exécute l'analyse globale complète sur l'ensemble des entrepôts et quais.
        Retourne un dictionnaire structuré prêt pour l'affichage et l'IA.
        """
        entrepots_qs = Entrepot.objects.all().prefetch_related('quais')
        quais_qs = Quai.objects.all().select_related('entrepot')

        total_entrepots = entrepots_qs.count()
        total_quais = quais_qs.count()

        # Métriques globales
        capacite_totale_palettes = entrepots_qs.aggregate(t=Sum('capacite_palettes'))['t'] or 0
        superficie_totale_m2 = entrepots_qs.aggregate(t=Sum('superficie_m2'))['t'] or 0

        # Décompte des statuts de quais
        docks_status_counts = {
            'DISPONIBLE': 0,
            'OCCUPE': 0,
            'RESERVE': 0,
            'MAINTENANCE': 0,
        }
        total_debit_theorique = 0
        total_debit_disponible = 0

        for quai in quais_qs:
            status = quai.statut
            if status in docks_status_counts:
                docks_status_counts[status] += 1
            else:
                docks_status_counts[status] = 1

            debit = quai.capacite_palettes_heure or 0
            total_debit_theorique += debit
            if status == 'DISPONIBLE':
                total_debit_disponible += debit

        quais_operationnels = (
            docks_status_counts['DISPONIBLE'] +
            docks_status_counts['OCCUPE'] +
            docks_status_counts['RESERVE']
        )
        quais_en_activite = docks_status_counts['OCCUPE'] + docks_status_counts['RESERVE']

        # Utilisation globale des quais (formule sécurisée)
        if quais_operationnels > 0:
            taux_utilisation_quais_global = round((quais_en_activite / quais_operationnels) * 100, 1)
            taux_disponibilite_quais_global = round((docks_status_counts['DISPONIBLE'] / quais_operationnels) * 100, 1)
        else:
            taux_utilisation_quais_global = 0.0
            taux_disponibilite_quais_global = 0.0

        # Analyse détaillée par entrepôt
        warehouses_data: List[Dict[str, Any]] = []
        underutilized_warehouses: List[Dict[str, Any]] = []
        near_capacity_warehouses: List[Dict[str, Any]] = []
        critical_warehouses: List[Dict[str, Any]] = []
        anomalies: List[Dict[str, Any]] = []

        # Regroupement par ville pour détection de déséquilibres locaux
        by_city: Dict[str, List[Dict[str, Any]]] = {}

        for ent in entrepots_qs:
            quais_list = list(ent.quais.all())
            nb_total = len(quais_list)
            nb_dispo = sum(1 for q in quais_list if q.statut == 'DISPONIBLE')
            nb_occupe = sum(1 for q in quais_list if q.statut == 'OCCUPE')
            nb_reserve = sum(1 for q in quais_list if q.statut == 'RESERVE')
            nb_maint = sum(1 for q in quais_list if q.statut == 'MAINTENANCE')

            nb_oper = nb_dispo + nb_occupe + nb_reserve
            nb_charge = nb_occupe + nb_reserve

            # Calcul du taux d'utilisation opérationnel
            if nb_oper > 0:
                utilization_pct = round((nb_charge / nb_oper) * 100, 1)
            else:
                utilization_pct = 0.0

            # Débit total et disponible par heure
            debit_total = sum(q.capacite_palettes_heure or 0 for q in quais_list)
            debit_dispo = sum(q.capacite_palettes_heure or 0 for q in quais_list if q.statut == 'DISPONIBLE')

            # Détermination de la classification & explication
            if ent.statut != 'ACTIF':
                classification = 'INACTIF'
                explanation = f"Entrepôt non opérationnel (Statut : {ent.get_statut_display()})."
            elif nb_total == 0:
                classification = 'SANS_QUAI'
                explanation = "Aucun quai de chargement n'est encore configuré pour ce site actif."
            elif nb_oper == 0 and nb_maint > 0:
                classification = 'CRITIQUE'
                explanation = f"100% des quais sont en maintenance ({nb_maint}/{nb_total}). Site complètement à l'arrêt."
            elif utilization_pct >= cls.CRITICAL_THRESHOLD or (nb_total > 0 and nb_dispo == 0 and nb_oper > 0):
                classification = 'CRITIQUE'
                explanation = (
                    f"Taux d'occupation des quais à {utilization_pct}% (Seuil critique >= {cls.CRITICAL_THRESHOLD}%). "
                    f"Aucun quai disponible ({nb_dispo}/{nb_oper} opérationnels)."
                )
            elif utilization_pct >= cls.NEAR_CAPACITY_THRESHOLD:
                classification = 'PROCHE_SATURATION'
                explanation = (
                    f"Taux d'occupation des quais à {utilization_pct}% (Seuil d'alerte >= {cls.NEAR_CAPACITY_THRESHOLD}%). "
                    f"Seulement {nb_dispo} quai(s) disponible(s)."
                )
            elif utilization_pct <= cls.UNDERUTILIZED_THRESHOLD and nb_oper > 0:
                classification = 'SOUS_UTILISE'
                explanation = (
                    f"Taux d'occupation des quais à {utilization_pct}% (Seuil sous-utilisation <= {cls.UNDERUTILIZED_THRESHOLD}%). "
                    f"Capacité excédentaire avec {nb_dispo}/{nb_oper} quais disponibles."
                )
            else:
                classification = 'EQUILIBRE'
                explanation = f"Taux d'occupation optimal à {utilization_pct}% ({nb_charge}/{nb_oper} quais occupés/réservés)."

            ent_record = {
                'id': ent.id,
                'nom': ent.nom,
                'code': ent.code,
                'ville': ent.ville,
                'statut': ent.statut,
                'statut_display': ent.get_statut_display(),
                'capacite_palettes': ent.capacite_palettes,
                'superficie_m2': ent.superficie_m2,
                'nb_quais': nb_total,
                'nb_disponibles': nb_dispo,
                'nb_occupes': nb_occupe,
                'nb_reserves': nb_reserve,
                'nb_maintenance': nb_maint,
                'quais_operationnels': nb_oper,
                'utilization_pct': utilization_pct,
                'debit_total_palettes_heure': debit_total,
                'debit_disponible_palettes_heure': debit_dispo,
                'classification': classification,
                'explanation': explanation,
            }

            warehouses_data.append(ent_record)

            if classification == 'SOUS_UTILISE':
                underutilized_warehouses.append(ent_record)
            elif classification == 'PROCHE_SATURATION':
                near_capacity_warehouses.append(ent_record)
            elif classification == 'CRITIQUE':
                critical_warehouses.append(ent_record)

            # Rapprochement géographique par ville
            city_key = ent.ville.strip().lower()
            if city_key not in by_city:
                by_city[city_key] = []
            by_city[city_key].append(ent_record)

            # --- Détection d'anomalies de données et configurations invalides ---
            # 1. Capacité nulle ou manquante
            if not ent.capacite_palettes or ent.capacite_palettes <= 0:
                anomalies.append({
                    'type': 'CAPACITE_NULLE',
                    'niveau': 'HIGH',
                    'entrepôt': ent.nom,
                    'code': ent.code,
                    'message': f"Capacité palettes nulle ou non renseignée ({ent.capacite_palettes} palettes).",
                    'valeur_actuelle': ent.capacite_palettes,
                    'action': "Définir la capacité réelle de stockage en palettes."
                })

            # 2. Entrepôt actif sans quai
            if ent.statut == 'ACTIF' and nb_total == 0:
                anomalies.append({
                    'type': 'SITE_SANS_QUAI',
                    'niveau': 'HIGH',
                    'entrepôt': ent.nom,
                    'code': ent.code,
                    'message': "Entrepôt déclaré actif mais ne disposant d'aucun quai d'amarrage.",
                    'valeur_actuelle': 0,
                    'action': "Créer au moins un quai d'exploitation pour rendre le site opérationnel."
                })

            # 3. Ratio superficie / palettes atypique
            if ent.superficie_m2 and ent.capacite_palettes:
                ratio = ent.superficie_m2 / ent.capacite_palettes
                if ratio < 0.8:
                    anomalies.append({
                        'type': 'DENSITE_ANORMALE',
                        'niveau': 'MEDIUM',
                        'entrepôt': ent.nom,
                        'code': ent.code,
                        'message': f"Densité suspecte : {ratio:.2f} m² par palette (norme logistique habituelle : 1.5 - 4 m²).",
                        'valeur_actuelle': f"{ratio:.2f} m²/palette",
                        'action': "Vérifier la cohérence entre la superficie déclarée et la capacité de rayonnage."
                    })

            # 4. Paralysie pour cause de maintenance
            if nb_total > 0 and (nb_maint / nb_total) * 100 >= cls.HIGH_DOWNTIME_THRESHOLD:
                anomalies.append({
                    'type': 'INDISPONIBILITE_MAINTENANCE',
                    'niveau': 'HIGH',
                    'entrepôt': ent.nom,
                    'code': ent.code,
                    'message': f"{nb_maint}/{nb_total} quais en maintenance technique ({(nb_maint/nb_total)*100:.0f}% d'indisponibilité).",
                    'valeur_actuelle': f"{nb_maint}/{nb_total} quais",
                    'action': "Accélérer la réouverture des quais ou dérouter le trafic."
                })

        # --- Détection de déséquilibres entre entrepôts comparables (même ville) ---
        city_imbalances: List[Dict[str, Any]] = []
        for city_name, ents in by_city.items():
            if len(ents) >= 2:
                # Trier par utilisation
                sorted_by_util = sorted(ents, key=lambda x: x['utilization_pct'], reverse=True)
                highest = sorted_by_util[0]
                lowest = sorted_by_util[-1]
                ecart = highest['utilization_pct'] - lowest['utilization_pct']

                if ecart >= 45.0 and highest['quais_operationnels'] > 0 and lowest['quais_operationnels'] > 0:
                    city_imbalances.append({
                        'ville': highest['ville'],
                        'ecart_utilization': ecart,
                        'surutilise': highest,
                        'sousutilise': lowest,
                        'message': (
                            f"Déséquilibre majeur à {highest['ville']} : {highest['nom']} est saturé à {highest['utilization_pct']}% "
                            f"alors que {lowest['nom']} est à seulement {lowest['utilization_pct']}% (écart : {ecart:.1f}%)."
                        )
                    })

        # Données sur les quais : quais sous-utilisés ou approchant de la saturation
        docks_analysis = cls._analyze_docks(quais_qs)

        # Rapport des limites de données
        data_limitations = [
            {
                'domaine': "Stock physique instantané de palettes",
                'statut': "Non modélisé dans Entrepot",
                'explication': (
                    "Le modèle `Entrepot` stocke la capacité totale théorique (`capacite_palettes`). "
                    "Le niveau d'occupation en temps réel est évalué via le statut opérationnel des quais "
                    "(`OCCUPE`, `RESERVE`, `DISPONIBLE`, `MAINTENANCE`) et le débit horaire (`capacite_palettes_heure`)."
                )
            },
            {
                'domaine': "Types de marchandises stockées",
                'statut': "Non modélisé dans Entrepot",
                'explication': (
                    "La compatibilité logistique est calculée sur la base des équipements des quais "
                    "(`type_quai`: STANDARD, FRIGORIFIQUE, ADR, etc.) et de la localisation géographique."
                )
            }
        ]

        return {
            'metrics': {
                'total_entrepots': total_entrepots,
                'total_quais': total_quais,
                'capacite_totale_palettes': capacite_totale_palettes,
                'superficie_totale_m2': superficie_totale_m2,
                'quais_operationnels': quais_operationnels,
                'quais_disponibles': docks_status_counts['DISPONIBLE'],
                'quais_occupes': docks_status_counts['OCCUPE'],
                'quais_reserves': docks_status_counts['RESERVE'],
                'quais_maintenance': docks_status_counts['MAINTENANCE'],
                'docks_status_counts': docks_status_counts,
                'taux_utilisation_quais_global': taux_utilisation_quais_global,
                'taux_disponibilite_quais_global': taux_disponibilite_quais_global,
                'total_debit_theorique': total_debit_theorique,
                'total_debit_disponible': total_debit_disponible,
            },
            'thresholds': {
                'underutilized': cls.UNDERUTILIZED_THRESHOLD,
                'near_capacity': cls.NEAR_CAPACITY_THRESHOLD,
                'critical': cls.CRITICAL_THRESHOLD,
                'high_downtime': cls.HIGH_DOWNTIME_THRESHOLD,
            },
            'warehouses': warehouses_data,
            'underutilized_warehouses': underutilized_warehouses,
            'near_capacity_warehouses': near_capacity_warehouses,
            'critical_warehouses': critical_warehouses,
            'city_imbalances': city_imbalances,
            'anomalies': anomalies,
            'docks_analysis': docks_analysis,
            'data_limitations': data_limitations,
        }

    @classmethod
    def _analyze_docks(cls, quais_qs) -> Dict[str, Any]:
        """
        Analyse détaillée des quais individuels.
        """
        by_type: Dict[str, Dict[str, int]] = {}
        for quai in quais_qs:
            t = quai.type_quai
            if t not in by_type:
                by_type[t] = {'total': 0, 'disponible': 0, 'occupe': 0, 'reserve': 0, 'maintenance': 0}
            by_type[t]['total'] += 1
            status_key = quai.statut.lower()
            if status_key in by_type[t]:
                by_type[t][status_key] += 1

        # Anomalies sur les quais
        dock_anomalies = []
        for q in quais_qs:
            if not q.capacite_palettes_heure or q.capacite_palettes_heure <= 0:
                dock_anomalies.append({
                    'quai': q.numero,
                    'entrepot': q.entrepot.nom,
                    'probleme': "Débit horaire (palettes/heure) non configuré ou nul."
                })

        return {
            'by_type': by_type,
            'dock_anomalies': dock_anomalies,
        }
