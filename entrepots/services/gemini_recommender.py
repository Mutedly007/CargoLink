"""
Service de recommandation IA avec Google Gemini et fallback déterministe.
Périmètre STRICT : Modèles Entrepot et Quai uniquement.
Utilise le SDK officiel Google GenAI avec validation de schéma JSON strict.
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Charger les variables d'environnement (.env)
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiCapacityRecommender:
    """
    Générateur de recommandations stratégiques de capacité pour les entrepôts et quais.
    S'appuie sur Google Gemini avec repli déterministe automatique si l'API est indisponible.
    """

    @classmethod
    def get_api_key(cls) -> Optional[str]:
        return os.getenv('GOOGLE_API_KEY')

    @classmethod
    def get_model_name(cls) -> str:
        return os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')

    @classmethod
    def generate_recommendations(
        cls,
        analysis_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Génère des recommandations structurées à partir des métriques calculées.
        Tente d'appeler Google Gemini. En cas d'erreur ou d'absence de clé,
        bascule automatiquement et de manière transparente sur le moteur déterministe local.
        """
        api_key = cls.get_api_key()
        if not api_key:
            logger.info("GOOGLE_API_KEY non configurée. Utilisation du moteur de repli déterministe.")
            return cls._generate_deterministic_fallback(
                analysis_data, opportunities, reason="Clé API non configurée"
            )

        # Préparer le contexte minimal et anonymisé
        minimal_context = cls._build_minimal_context(analysis_data, opportunities)

        try:
            # Appel via le SDK officiel google-genai
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=api_key)
            model_name = cls.get_model_name()

            prompt = cls._build_prompt(minimal_context)

            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2, # Température basse pour une factualité maximale
                    response_mime_type="application/json",
                )
            )

            raw_text = response.text.strip()
            # Nettoyer d'éventuels backticks markdown
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:]
            if raw_text.startswith("```"):
                raw_text = raw_text[3:]
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]

            parsed_json = json.loads(raw_text.strip())
            validated_data = cls._validate_and_sanitize_response(parsed_json)
            validated_data['source'] = 'gemini'
            validated_data['model_used'] = model_name
            return validated_data

        except Exception as exc:
            logger.warning("Erreur lors de l'appel à Google Gemini: %s. Bascule en mode déterministe.", exc)
            return cls._generate_deterministic_fallback(
                analysis_data, opportunities, reason=f"Gemini indisponible ({type(exc).__name__})"
            )

    @classmethod
    def _build_minimal_context(cls, analysis_data: Dict[str, Any], opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Construit un résumé factuel sans PII ni données superflues."""
        metrics = analysis_data.get('metrics', {})
        thresholds = analysis_data.get('thresholds', {})

        warehouses_summary = []
        for w in analysis_data.get('warehouses', []):
            warehouses_summary.append({
                'nom': w['nom'],
                'code': w['code'],
                'ville': w['ville'],
                'statut': w['statut'],
                'capacite_palettes': w['capacite_palettes'],
                'superficie_m2': w['superficie_m2'],
                'nb_quais': w['nb_quais'],
                'quais_disponibles': w['nb_disponibles'],
                'quais_occupes': w['nb_occupes'],
                'quais_reserves': w['nb_reserves'],
                'quais_maintenance': w['nb_maintenance'],
                'taux_utilisation_pct': w['utilization_pct'],
                'classification': w['classification'],
            })

        return {
            'global_metrics': {
                'total_entrepots': metrics.get('total_entrepots'),
                'total_quais': metrics.get('total_quais'),
                'taux_utilisation_global_pct': metrics.get('taux_utilisation_quais_global'),
                'quais_disponibles': metrics.get('quais_disponibles'),
                'quais_occupes': metrics.get('quais_occupes'),
                'quais_maintenance': metrics.get('quais_maintenance'),
            },
            'thresholds': thresholds,
            'warehouses': warehouses_summary,
            'anomalies_detected': analysis_data.get('anomalies', []),
            'feasible_redistributions': opportunities,
        }

    @classmethod
    def _build_prompt(cls, minimal_context: Dict[str, Any]) -> str:
        """Construit le prompt système pour Gemini garantissant la stricte factualité."""
        return f"""
Tu es l'ingénieur IA d'optimisation de capacité logistique pour la plateforme CargoLink.
Ton rôle est d'analyser les données ci-dessous (concernant STRICTEMENT les entrepôts et les quais) et de formuler des recommandations claires, opérationnelles et hiérarchisées pour les gestionnaires de sites.

RÈGLES IMPÉRATIVES DE SÉCURITÉ ET FACTUALITÉ :
1. Tu n'inventes AUCUN chiffre, AUCUN pourcentage d'occupation, AUCUN nouvel entrepôt et AUCUN nouveau quai non mentionné dans les données.
2. Tu utilises EXCLUSIVEMENT les faits fournis ci-dessous.
3. Tout bénéfice attendu doit être explicitement désigné comme une estimation ("gain estimé", "réduction estimée").
4. Si une donnée n'est pas modélisée (ex: le contenu exact des palettes ou les camions), mentionne-le clairement dans le champ 'constraints_or_missing_data'.
5. Réponds STRICTEMENT en français et renvoie UNIQUEMENT un objet JSON conforme au schéma spécifié.

DONNÉES FACTUELLES DES ENTREPÔTS ET QUAIS :
{json.dumps(minimal_context, ensure_ascii=False, indent=2)}

SCHÉMA JSON ATTENDU :
{{
  "summary": "Synthèse globale en 2 ou 3 phrases sur l'état de la capacité des entrepôts et des quais.",
  "recommendations": [
    {{
      "id": "rec-1",
      "title": "Titre court et orienté action",
      "description": "Diagnostic clair basé sur les métriques observées.",
      "affected_entity": "Nom de l'entrepôt ou du quai concerné",
      "detected_issue": "Description précise de l'anomalie ou du problème de capacité",
      "supporting_metrics": ["Métrique 1 exacte", "Métrique 2 exacte"],
      "recommended_action": "Action concrète à réaliser par le gestionnaire",
      "expected_benefit": "Bénéfice estimé réaliste",
      "priority_level": "HIGH" | "MEDIUM" | "LOW",
      "category": "REBALANCING" | "MAINTENANCE" | "CAPACITY" | "DATA_QUALITY",
      "is_actionable": true | false,
      "constraints_or_missing_data": "Mention des contraintes physiques ou des données absentes à vérifier",
      "confidence_level": "HIGH" | "MEDIUM" | "LOW"
    }}
  ]
}}
"""

    @classmethod
    def _format_metric_chip(cls, text: str) -> str:
        """Nettoie les clés techniques pour un affichage lisible et élégant."""
        s = str(text).strip()
        replacements = [
            ('taux_utilisation_pct:', 'Occupation :'),
            ('taux_utilisation_pct', 'Occupation'),
            ('capacite_palettes:', 'Capacité :'),
            ('capacite_palettes', 'Capacité'),
            ('superficie_m2:', 'Superficie :'),
            ('nb_quais:', 'Quais totaux :'),
            ('nb_quais', 'Quais totaux'),
            ('quais_disponibles:', 'Quais libres :'),
            ('quais_disponibles', 'Quais libres'),
            ('quais_occupes:', 'Quais occupés :'),
            ('quais_occupes', 'Quais occupés'),
            ('quais_reserves:', 'Quais réservés :'),
            ('quais_reserves', 'Quais réservés'),
            ('quais_maintenance:', 'En maintenance :'),
            ('quais_maintenance', 'En maintenance'),
            ('total_quais:', 'Total quais :'),
            ('total_entrepots:', 'Total entrepôts :'),
        ]
        for old, new in replacements:
            s = s.replace(old, new)
        return s

    @classmethod
    def _validate_and_sanitize_response(cls, data: Any) -> Dict[str, Any]:
        """Valide et nettoie la réponse JSON pour garantir l'intégrité de l'affichage."""
        if not isinstance(data, dict):
            raise ValueError("La réponse racine doit être un dictionnaire JSON.")

        summary = data.get('summary', "Analyse des capacités effectuée avec succès.")
        raw_recs = data.get('recommendations', [])
        clean_recs = []

        valid_priorities = {'HIGH', 'MEDIUM', 'LOW'}
        valid_categories = {'REBALANCING', 'MAINTENANCE', 'CAPACITY', 'DATA_QUALITY'}
        valid_confidence = {'HIGH', 'MEDIUM', 'LOW'}

        for idx, item in enumerate(raw_recs):
            if not isinstance(item, dict):
                continue

            # Nettoyage et formatage des métriques de support
            raw_metrics = list(item.get('supporting_metrics', []))
            formatted_metrics = [cls._format_metric_chip(m) for m in raw_metrics]

            clean_recs.append({
                'id': str(item.get('id', f'rec-{idx+1}')),
                'title': str(item.get('title', 'Optimisation suggérée')),
                'description': str(item.get('description', '')),
                'affected_entity': str(item.get('affected_entity', 'Réseau global')),
                'detected_issue': str(item.get('detected_issue', 'Écart d\'utilisation')),
                'supporting_metrics': formatted_metrics,
                'recommended_action': str(item.get('recommended_action', 'Vérifier la configuration du site.')),
                'expected_benefit': str(item.get('expected_benefit', 'Gain d\'efficience estimé.')),
                'priority_level': item.get('priority_level') if item.get('priority_level') in valid_priorities else 'MEDIUM',
                'category': item.get('category') if item.get('category') in valid_categories else 'CAPACITY',
                'is_actionable': bool(item.get('is_actionable', True)),
                'constraints_or_missing_data': str(item.get('constraints_or_missing_data', 'Aucune contrainte bloquante relevée.')),
                'confidence_level': item.get('confidence_level') if item.get('confidence_level') in valid_confidence else 'HIGH',
            })

        return {
            'summary': summary,
            'recommendations': clean_recs,
        }

    @classmethod
    def _generate_deterministic_fallback(
        cls,
        analysis_data: Dict[str, Any],
        opportunities: List[Dict[str, Any]],
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Générateur déterministe fiable garantissant le fonctionnement continu
        même sans accès internet ou sans quota API.
        """
        recs = []
        rec_counter = 1

        # 1. Recommandations basées sur les rééquilibrages géographiques
        for opp in opportunities:
            recs.append({
                'id': f'rec-{rec_counter}',
                'title': f"Rééquilibrage de flux : {opp['source_nom']} ➔ {opp['target_nom']}",
                'description': (
                    f"L'entrepôt {opp['source_nom']} à {opp['source_ville']} approche de la saturation ({opp['source_util_actuelle']}%), "
                    f"alors que {opp['target_nom']} dans la même ville ne fonctionne qu'à {opp['target_util_actuelle']}% "
                    f"avec {opp['target_disponibles']} quai(s) disponible(s)."
                ),
                'affected_entity': f"{opp['source_nom']} & {opp['target_nom']}",
                'detected_issue': "Déséquilibre critique de charge entre sites d'un même bassin logistique",
                'supporting_metrics': [
                    f"Taux {opp['source_nom']} : {opp['source_util_actuelle']}%",
                    f"Taux {opp['target_nom']} : {opp['target_util_actuelle']}%",
                    f"Quais libres sur récepteur : {opp['target_disponibles']}",
                ],
                'recommended_action': opp['action_proposee'],
                'expected_benefit': opp['benefice_estime'],
                'priority_level': 'HIGH',
                'category': 'REBALANCING',
                'is_actionable': True,
                'constraints_or_missing_data': opp['explication_contrainte'],
                'confidence_level': 'HIGH',
            })
            rec_counter += 1

        # 2. Recommandations basées sur les anomalies détectées
        for anom in analysis_data.get('anomalies', []):
            prio = anom.get('niveau', 'MEDIUM')
            category = 'DATA_QUALITY'
            if anom['type'] == 'INDISPONIBILITE_MAINTENANCE':
                category = 'MAINTENANCE'
            elif anom['type'] in ('CAPACITE_NULLE', 'SITE_SANS_QUAI'):
                category = 'CAPACITY'

            recs.append({
                'id': f'rec-{rec_counter}',
                'title': f"Correction requise : {anom['type'].replace('_', ' ')}",
                'description': anom['message'],
                'affected_entity': f"{anom.get('entrepôt', 'Entrepôt')} ({anom.get('code', 'N/A')})",
                'detected_issue': anom['message'],
                'supporting_metrics': [f"Valeur actuelle : {anom.get('valeur_actuelle', 'N/A')}"],
                'recommended_action': anom.get('action', 'Mettre à jour les données du site.'),
                'expected_benefit': "Fiabilisation des calculs de capacité et déblocage de l'exploitation.",
                'priority_level': prio,
                'category': category,
                'is_actionable': True,
                'constraints_or_missing_data': "Vérification manuelle requise avec le chef de site.",
                'confidence_level': 'HIGH',
            })
            rec_counter += 1

        # 3. Entrepôts critiques sans quai disponible
        for crit in analysis_data.get('critical_warehouses', []):
            # Éviter de dupliquer si déjà dans les opportunités
            if not any(crit['nom'] in r['affected_entity'] for r in recs):
                recs.append({
                    'id': f'rec-{rec_counter}',
                    'title': f"Saturation critique des quais sur {crit['nom']}",
                    'description': crit['explanation'],
                    'affected_entity': crit['nom'],
                    'detected_issue': "Absence totale de quai disponible et risque de file d'attente",
                    'supporting_metrics': [
                        f"Taux d'occupation : {crit['utilization_pct']}%",
                        f"Quais occupés/réservés : {crit['nb_occupes'] + crit['nb_reserves']}/{crit['quais_operationnels']}",
                    ],
                    'recommended_action': "Prioriser la libération des quais en cours d'opération ou adapter les plages horaires.",
                    'expected_benefit': "Décongestion estimée du site et fluidification des flux entrants.",
                    'priority_level': 'HIGH',
                    'category': 'CAPACITY',
                    'is_actionable': True,
                    'constraints_or_missing_data': "Les créneaux de livraison précis ne sont pas consultables depuis ce module.",
                    'confidence_level': 'HIGH',
                })
                rec_counter += 1

        global_metrics = analysis_data.get('metrics', {})
        summary = (
            f"Analyse déterministe locale : {global_metrics.get('total_entrepots', 0)} entrepôt(s) et "
            f"{global_metrics.get('total_quais', 0)} quai(s) analysés. "
            f"Taux d'occupation opérationnel global estimé à {global_metrics.get('taux_utilisation_quais_global', 0)}%. "
            f"{len(recs)} opportunité(s) d'optimisation identifiée(s)."
        )

        return {
            'summary': summary,
            'recommendations': recs,
            'source': 'deterministic_fallback',
            'fallback_reason': reason,
        }
