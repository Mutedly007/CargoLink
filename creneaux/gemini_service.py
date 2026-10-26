import json
from datetime import date, datetime
import requests
from django.conf import settings
from entrepots.models import Entrepot, Quai
from .models import Creneau


class GeminiSlotAssistant:
    """
    Service d'Intelligence Artificielle Google Gemini dédié STRICTEMENT au module Gestion des Créneaux (Module Kacem).
    Applique un filtrage rigoureux pour ne traiter QUE les sujets liés aux créneaux, quais et plannings.
    """

    SYSTEM_PROMPT = """Tu es "CargoLink Slot Copilot", l'assistant IA propulsé par Google Gemini, dédié STRICTEMENT et EXCLUSIVEMENT au module de Gestion des Créneaux (conçu par Kacem) de la plateforme logistique CargoLink.

RÈGLES ABSOLUES ET STRICTES DE COMPORTEMENT :
1. TU DOIS RÉPONDRE UNIQUEMENT aux questions relatives au module de Gestion des Créneaux :
   - Les créneaux horaires enregistrés (références, dates, horaires de début/fin, durées, statuts, type d'opération).
   - L'état d'occupation et la disponibilité des quais pour les créneaux.
   - Les conflits horaires, les risques de chevauchement et l'arbitrage des créneaux.
   - Le cycle de vie d'un créneau (Demande, Confirmation, Arrivée camion, Mise à quai, Clôture/Terminé, Annulation).
   - Les recommandations logistiques d'optimisation horaire et d'attribution des quais.
2. SI L'UTILISATEUR POSE UNE QUESTION HORS DU PÉRIMÈTRE DE LA GESTION DES CRÉNEAUX (sujet général, météo, cuisine, blague, ou gestion complète des fiches chauffeurs/camions en dehors de leur créneau de quai) :
   TU DOIS REFUSER CATÉGORIQUEMENT ET POLIMENT de répondre en disant exactement :
   "⚠️ En tant qu'assistant IA spécialisé, je suis configuré pour répondre exclusivement aux questions relatives au module de Gestion des Créneaux de CargoLink (planning, horaires des quais, disponibilités, conflits et suivi des opérations). Comment puis-je vous aider sur vos créneaux ?"
3. Base tes réponses sur les DONNÉES RÉELLES fournies ci-dessous dans le contexte.
4. Reste clair, concis, bien structuré (avec des puces), et utilise des emojis logistiques (🚛, 🏭, ⏱️, 📅, ✅, ⚠️).
"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '') or ''
        # Modèles optimisés pour rapidité et compatibilité avec la clé API
        self.models_to_try = ["gemini-3.5-flash-lite", "gemini-3.1-flash-lite", "gemini-flash-latest"]
        self.base_api_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def ask(self, user_prompt: str, user=None) -> dict:
        """
        Interroge Gemini avec injection du contexte réel des créneaux de la base Django.
        """
        # Vérification préalable rapide du sujet
        if not self._is_slot_related(user_prompt):
            return {
                'success': True,
                'source': 'guardrail',
                'response': (
                    "⚠️ En tant qu'assistant IA spécialisé, je suis configuré pour répondre exclusivement "
                    "aux questions relatives au module de **Gestion des Créneaux** de CargoLink "
                    "(planning, horaires des quais, disponibilités, conflits et suivi des opérations).\n\n"
                    "Comment puis-je vous aider sur vos créneaux horaires ou l'état de vos quais ?"
                )
            }

        # Construction du contexte temps réel depuis la base de données
        context_data = self._build_database_context()

        # Si une clé API est fournie, appel direct à Gemini
        if self.api_key:
            return self._call_gemini_api(user_prompt, context_data)
        else:
            # Fallback intelligent local (moteur expert basé sur les vraies données)
            return self._expert_local_fallback(user_prompt, context_data)

    def _is_slot_related(self, prompt: str) -> bool:
        """Filtre préventif pour s'assurer que la question concerne les créneaux ou les quais."""
        prompt_lower = prompt.lower().strip()
        
        # Mots-clés autorisés du module créneaux
        keywords = [
            'creneau', 'créneau', 'creneaux', 'créneaux', 'slot', 'quai', 'quais',
            'planning', 'horaire', 'horaires', 'heure', 'retard', 'conflit', 'chevauchement',
            'disponible', 'disponibilité', 'disponibilite', 'occupe', 'occupé', 'statut',
            'attente', 'confirme', 'confirmé', 'confirmation', 'arrive', 'arrivé',
            'cours', 'termine', 'terminé', 'annule', 'annulé', 'dechargement', 'déchargement',
            'chargement', 'palette', 'palettes', 'bl', 'cmr', 'radès', 'rades', 'entrepot', 'entrepôt',
            'cargolink', 'kacem', 'optimisation', 'camion', 'transporteur', 'recommandation'
        ]

        # Si la question contient au moins un mot-clé du domaine, on accepte
        return any(k in prompt_lower for k in keywords)

    def _build_database_context(self) -> str:
        """Génère un résumé textuel structuré des données actuelles en base pour Gemini (RAG)."""
        today = date.today()
        creneaux = Creneau.objects.select_related('entrepot', 'quai').all()
        quais = Quai.objects.select_related('entrepot').all()

        creneaux_jour = creneaux.filter(date_creneau=today)
        
        lignes_creneaux = []
        for c in creneaux.order_by('date_creneau', 'heure_debut')[:15]:
            lignes_creneaux.append(
                f"- Réf: {c.reference} | Date: {c.date_creneau.strftime('%d/%m/%Y')} | "
                f"Horaires: {c.heure_debut.strftime('%H:%M')}-{c.heure_fin.strftime('%H:%M')} | "
                f"Site: {c.entrepot.nom} (Quai: {c.quai.numero}) | "
                f"Opération: {c.get_type_operation_display()} | Statut: {c.get_statut_display()} | "
                f"Transporteur: {c.transporteur_nom} ({c.immatriculation_camion}) | Palettes: {c.nb_palettes}"
            )

        lignes_quais = []
        for q in quais:
            lignes_quais.append(f"- {q.numero} ({q.entrepot.nom}) : Type {q.get_type_quai_display()} - Statut: {q.get_statut_display()}")

        total = creneaux.count()
        en_attente = creneaux.filter(statut='EN_ATTENTE').count()
        en_cours = creneaux.filter(statut='EN_COURS').count()
        confirmes = creneaux.filter(statut='CONFIRME').count()
        termines = creneaux.filter(statut='TERMINE').count()

        return f"""
DONNÉES EN DIRECT DE LA BASE DE DONNÉES CARGOLINK (Aujourd'hui : {today.strftime('%d/%m/%Y')}) :
- Total des créneaux : {total} (Aujourd'hui : {creneaux_jour.count()})
- Créneaux en attente de confirmation : {en_attente}
- Créneaux confirmés : {confirmes}
- Opérations en cours à quai : {en_cours}
- Opérations terminées : {termines}

LISTE DES CRÉNEAUX EN BASE :
{chr(10).join(lignes_creneaux) if lignes_creneaux else 'Aucun créneau enregistré.'}

ÉTAT DES QUAIS :
{chr(10).join(lignes_quais) if lignes_quais else 'Aucun quai configuré.'}
"""

    def _call_gemini_api(self, user_prompt: str, context_data: str) -> dict:
        """Appel HTTP à l'API Google Gemini avec bascule automatique de modèle."""
        full_prompt = f"{self.SYSTEM_PROMPT}\n\n{context_data}\n\nQUESTION DE L'UTILISATEUR :\n{user_prompt}"

        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": full_prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 600
            }
        }

        headers = {"Content-Type": "application/json"}

        for model in self.models_to_try:
            url = f"{self.base_api_url}/{model}:generateContent?key={self.api_key}"
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data['candidates'][0]['content']['parts'][0]['text']
                    return {
                        'success': True,
                        'source': 'gemini_api',
                        'response': answer
                    }
            except Exception:
                continue

        # Si l'appel distant échoue ou timeout
        return self._expert_local_fallback(user_prompt, context_data)

    def _expert_local_fallback(self, user_prompt: str, context_data: str, error_msg: str = None) -> dict:
        """
        Moteur d'inférence expert local : garantit une réponse factuelle et instantanée
        même sans clé API ou hors connexion internet.
        """
        prompt_lower = user_prompt.lower()
        today = date.today()
        creneaux = Creneau.objects.select_related('entrepot', 'quai').all()

        en_attente = creneaux.filter(statut='EN_ATTENTE')
        en_cours = creneaux.filter(statut='EN_COURS')
        confirmes = creneaux.filter(statut='CONFIRME')
        du_jour = creneaux.filter(date_creneau=today)

        # 1. Question sur les créneaux en attente
        if 'attente' in prompt_lower:
            if en_attente.exists():
                items = [f"• **{c.reference}** : {c.transporteur_nom} ({c.nb_palettes} pal.) le {c.date_creneau.strftime('%d/%m')} à {c.heure_debut.strftime('%H:%M')} sur {c.quai.numero}" for c in en_attente]
                resp = f"📋 Il y a actuellement **{en_attente.count()} demande(s) de créneau en attente de confirmation** :\n\n" + "\n".join(items) + "\n\n💡 *Vous pouvez confirmer ces créneaux en un clic depuis leur fiche détail.*"
            else:
                resp = "✅ **Aucune demande de créneau en attente** pour le moment. Tous les créneaux sont déjà arbitrés."

        # 2. Question sur les créneaux du jour / aujourd'hui
        elif 'aujourd' in prompt_lower or 'jour' in prompt_lower:
            items = [f"• **{c.reference}** ({c.heure_debut.strftime('%H:%M')}-{c.heure_fin.strftime('%H:%M')}) : Quai {c.quai.numero} - {c.get_statut_display()} [{c.transporteur_nom}]" for c in du_jour]
            resp = f"📅 **Créneaux planifiés aujourd'hui ({du_jour.count()} au total)** :\n\n" + ("\n".join(items) if items else "Aucun créneau programmé aujourd'hui.")

        # 3. Question sur les opérations en cours / à quai
        elif 'cours' in prompt_lower or 'quai' in prompt_lower and 'occup' in prompt_lower:
            if en_cours.exists():
                items = [f"• **Quai {c.quai.numero}** : Camion `{c.immatriculation_camion}` ({c.transporteur_nom}) - Début effectif : {c.heure_debut_operation.strftime('%H:%M') if c.heure_debut_operation else c.heure_debut.strftime('%H:%M')}" for c in en_cours]
                resp = f"🚛 **Opérations actuellement en cours à quai ({en_cours.count()})** :\n\n" + "\n".join(items)
            else:
                resp = "🟢 **Aucune opération en cours pour l'instant**. Les quais sont libres ou en attente des prochains arrivages."

        # 4. Question sur les conflits ou disponibilités
        elif 'conflit' in prompt_lower or 'disponib' in prompt_lower:
            resp = (
                "🛡️ **Analyse des Conflits & Disponibilités** :\n\n"
                "Le système applique le moteur anti-chevauchement strict : aucun créneau actif ne peut se chevaucher sur le même quai à la même date.\n"
                f"• Quais configurés : **{Quai.objects.count()}**\n"
                f"• Quais libres actuellement : **{Quai.objects.filter(statut='DISPONIBLE').count()}**\n"
                "💡 *Pour affecter automatiquement le quai le plus fluide, utilisez le bouton d'optimisation IA sur le formulaire de créneau.*"
            )

        # 5. Synthèse globale par défaut
        else:
            resp = (
                f"📊 **Synthèse du Module Créneaux (CargoLink)** :\n\n"
                f"• Total créneaux enregistrés : **{creneaux.count()}**\n"
                f"• Prévus aujourd'hui : **{du_jour.count()}**\n"
                f"• En attente de validation : **{en_attente.count()}**\n"
                f"• En cours de traitement : **{en_cours.count()}**\n"
                f"• Opérations terminées : **{creneaux.filter(statut='TERMINE').count()}**\n\n"
                f"Que souhaitez-vous savoir précisément sur le planning, les quais ou un créneau particulier ?"
            )

        notice = "\n\n*(⚡ Analyse générée par le Copilot IA Spécialisé Créneaux)*"
        return {
            'success': True,
            'source': 'expert_fallback',
            'response': resp + notice
        }
