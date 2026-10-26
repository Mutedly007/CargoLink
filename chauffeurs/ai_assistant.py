import re
import json
from datetime import date, datetime, timedelta
import requests
from django.conf import settings
from django.db.models import Count
from chauffeurs.models import Chauffeur, VisiteChauffeur


class GeminiChauffeurAssistant:
    """
    Assistant Conversationnel Intelligent (IA) pour le Module Chauffeurs (CargoLink).
    Propulsé par Google Gemini avec support multilingue : Français, Arabe (العربية), Anglais.
    Permet aux responsables de rechercher, filtrer et analyser les chauffeurs en langage naturel.
    """

    SYSTEM_PROMPT = """Tu es "CargoLink Driver Copilot", l'assistant IA conversationnel expert de la gestion des chauffeurs et de la conformité logistique de CargoLink.
Ta mission est d'aider les responsables d'exploitation et transporteurs à rechercher, analyser et gérer les chauffeurs en langage naturel.

RÈGLES ABSOLUES ET STRICTES :
1. PÉRIMÈTRE STRICT : Tu réponds UNIQUEMENT aux questions relatives aux chauffeurs, à leurs permis (validité, expiration, catégories), à leurs visites en entrepôt, leurs camions affectés, leurs missions et leurs statuts.
2. REFUS DES QUESTIONS HORS SUJET : Si la question est sans rapport avec les chauffeurs ou la logistique CargoLink, refuse poliment dans la langue de l'utilisateur.
3. MULTILINGUISME :
   - Si la question est posée en ARABE (ou si le mode Arabe est actif), réponds dans un Arabe clair, professionnel et fluide (الفصحى).
   - Si la question est posée en ANGLAIS, réponds en Anglais professionnel.
   - Si la question est posée en FRANÇAIS, réponds en Français professionnel.
4. BASÉ SUR LES DONNÉES RÉELLES : Toutes tes réponses doivent s'appuyer strictement sur les DONNÉES RÉELLES fournies ci-dessous dans le contexte. N'invente aucun chauffeur ni date.
5. FORMATAGE ÉLÉGANT :
   - Structure tes réponses avec des puces (•), du texte en gras (**nom**), et des emojis logistiques (🚚, 🪪, ⚠️, 📅, 🏢, ✅, ⏱️).
   - Pour les alertes de permis expirant ou expirés, mets clairement en évidence le délai et les actions requises.
   - Pour les historiques de chauffeurs, propose une synthèse concise : identité, permis, camion attitré, visites réalisées et statut actuel.
"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'GEMINI_API_KEY', '') or ''
        self.models_to_try = [
            "gemini-3.8-flash",
            "gemini-3.5-flash-lite",
            "gemini-3.1-flash-lite",
            "gemini-flash-latest"
        ]
        self.base_api_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def ask(self, user_prompt: str, lang: str = 'fr', user=None) -> dict:
        """
        Traite la requête en langage naturel avec contexte RAG complet et support multilingue.
        """
        clean_prompt = user_prompt.strip()
        detected_lang = self._detect_language(clean_prompt, preferred_lang=lang)

        # Vérification du périmètre (Guardrail)
        if not self._is_chauffeur_related(clean_prompt):
            return {
                'success': True,
                'source': 'guardrail',
                'language': detected_lang,
                'response': self._guardrail_response(detected_lang)
            }

        # Construction du contexte RAG
        context_data = self._build_database_context()

        # Appel à l'API Gemini si clé configurée
        if self.api_key:
            api_result = self._call_gemini_api(clean_prompt, context_data, detected_lang)
            if api_result.get('success'):
                return api_result

        # Fallback local expert si échec API ou hors ligne
        return self._expert_local_fallback(clean_prompt, detected_lang)

    def _detect_language(self, prompt: str, preferred_lang: str = 'fr') -> str:
        """Détecte la langue de la requête : 'ar', 'en' ou 'fr'."""
        if re.search(r'[\u0600-\u06FF]', prompt):
            return 'ar'
        
        # Mots anglais fréquents
        en_words = ['which', 'who', 'show', 'list', 'driver', 'drivers', 'license', 'expire', 'month', 'visit', 'visits', 'summary', 'history', 'available', 'truck']
        prompt_words = prompt.lower().split()
        if any(w in prompt_words for w in en_words) and preferred_lang == 'en':
            return 'en'
        
        return preferred_lang if preferred_lang in ['fr', 'ar', 'en'] else 'fr'

    def _guardrail_response(self, lang: str) -> str:
        """Message de refus poli pour requêtes hors-sujet."""
        if lang == 'ar':
            return (
                "⚠️ بصفتي مساعد الذكاء الاصطناعي المخصص لإدارة **السائقين في CargoLink**، أنا مبرمج للإجابة حصراً "
                "على الأسئلة المتعلقة ببيانات السائقين، رخص القيادة وصلاحيتها، سجل الزيارات، وحالات التوفر والمهمات.\n\n"
                "كيف يمكنني مساعدتك بخصوص سائقي الأسطول ؟"
            )
        elif lang == 'en':
            return (
                "⚠️ As a specialized AI assistant for **CargoLink Driver Management**, I am designed to answer questions "
                "strictly related to drivers, license validity, warehouse visits, truck assignments, and mission statuses.\n\n"
                "How can I assist you with your fleet drivers today?"
            )
        else:
            return (
                "⚠️ En tant qu'assistant IA spécialisé pour la **Gestion des Chauffeurs CargoLink**, je réponds exclusivement "
                "aux questions concernant les fiches chauffeurs, la conformité des permis de conduire, les passages en entrepôt "
                "et les affectations de missions.\n\n"
                "Comment puis-je vous aider sur vos chauffeurs ?"
            )

    def _is_chauffeur_related(self, prompt: str) -> bool:
        """Filtre de pertinence sur les termes liés aux chauffeurs."""
        prompt_lower = prompt.lower()
        words = set(re.findall(r'\b\w+\b', prompt_lower))

        # Mots courts spécifiques qui nécessitent une correspondance exacte de mot entier
        exact_short_words = {'bl', 'cmr', 'cin', 'nom', 'qui'}
        if words.intersection(exact_short_words):
            return True

        keywords = [
            # Français
            'chauffeur', 'conducteur', 'permis', 'expire', 'expiration', 'visite',
            'historique', 'mission', 'camion', 'quai', 'entrepot', 'disponible', 'repos', 'statut',
            'validite', 'valide', 'categorie', 'adr', 'liste', 'combien',
            'khalil', 'hlila', 'cargolink', 'transporteur', 'entreprise', 'fiche', 'résumé', 'resume',
            # Arabe
            'سائق', 'رخصة', 'سياقة', 'تنتهي', 'انتهاء', 'صلاحية', 'زيارة',
            'سجل', 'مهمة', 'شاحنة', 'متاح', 'متوفر', 'تلخيص', 'ملخص', 'مستودع',
            # Anglais
            'driver', 'license', 'expir', 'visit', 'history',
            'truck', 'available', 'mission', 'dock', 'warehouse', 'status', 'summary'
        ]
        return any(k in prompt_lower for k in keywords)

    def _build_database_context(self) -> str:
        """Construit le contexte temps réel structuré pour l'injection RAG."""
        today = date.today()
        chauffeurs = Chauffeur.objects.annotate(visites_count=Count('visites')).order_by('nom')

        lignes = []
        lignes.append(f"DATE DU JOUR DU SYSTÈME : {today.strftime('%d/%m/%Y')} (Mois actuel: {today.strftime('%m/%Y')})")
        lignes.append(f"NOMBRE TOTAL DE CHAUFFEURS ENREGISTRÉS : {chauffeurs.count()}")
        lignes.append("\nLISTE COMPLÈTE DES CHAUFFEURS :")

        for c in chauffeurs:
            exp_date_str = c.date_expiration_permis.strftime('%d/%m/%Y')
            deliv_date_str = c.date_delivrance_permis.strftime('%d/%m/%Y') if c.date_delivrance_permis else "Non renseignée"
            expire_ce_mois = (c.date_expiration_permis.year == today.year and c.date_expiration_permis.month == today.month)
            
            dern_visite = c.visites.order_by('-date_visite').first()
            dern_visite_info = f"{dern_visite.date_visite.strftime('%d/%m/%Y')} ({dern_visite.entrepot.nom if dern_visite.entrepot else 'Site'})" if dern_visite else "Aucune"

            lignes.append(
                f"- Nom: {c.nom_complet} | ID: {c.pk} | Tél: {c.telephone} | Ville: {c.ville_residence} | "
                f"Statut actuel: {c.get_statut_display()} | Permis: {c.numero_permis} (Cat. {c.categorie_permis}) | "
                f"Délivré: {deliv_date_str} | Expiration: {exp_date_str} (Jours restants: {c.jours_avant_expiration}, Expire ce mois-ci: {'OUI' if expire_ce_mois else 'NON'}) | "
                f"État validité permis: {c.statut_validite_permis} | Entreprise: {c.entreprise_transport} | "
                f"Camion habituel: {c.immatriculation_camion or 'Aucun'} ({c.marque_camion}) | "
                f"Total visites effectuées: {c.visites_count} | Dernière visite: {dern_visite_info} | "
                f"Badge portuaire: {'OUI' if c.badge_acces_portuaire else 'NON'}"
            )

        return "\n".join(lignes)

    def _call_gemini_api(self, user_prompt: str, context_data: str, lang: str) -> dict:
        """Appelle l'API Google Gemini avec gestion multi-modèles et fallback."""
        lang_instruction = {
            'ar': "IMPORTANT : Tu DOIS répondre EXCLUSIVEMENT en ARABE classique professionnel (اللغة العربية الفصحى).",
            'en': "IMPORTANT : You MUST answer EXCLUSIVELY in professional ENGLISH.",
            'fr': "IMPORTANT : Tu DOIS répondre EXCLUSIVEMENT en FRANÇAIS professionnel."
        }.get(lang, "Tu DOIS répondre en FRANÇAIS.")

        full_prompt = (
            f"{self.SYSTEM_PROMPT}\n\n"
            f"{lang_instruction}\n\n"
            f"=== DONNÉES RÉELLES EN BASE CARGOLINK ===\n"
            f"{context_data}\n\n"
            f"=== QUESTION DE L'UTILISATEUR ===\n"
            f"{user_prompt}\n\n"
            f"Réponse détaillée, bien structurée avec emojis et liens/noms précis :"
        )

        payload = {
            "contents": [
                {
                    "parts": [{"text": full_prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 800
            }
        }
        headers = {"Content-Type": "application/json"}

        for model in self.models_to_try:
            url = f"{self.base_api_url}/{model}:generateContent?key={self.api_key}"
            try:
                resp = requests.post(url, headers=headers, json=payload, timeout=12)
                if resp.status_code == 200:
                    data = resp.json()
                    candidates = data.get('candidates', [])
                    if candidates and 'parts' in candidates[0].get('content', {}):
                        answer = candidates[0]['content']['parts'][0]['text']
                        return {
                            'success': True,
                            'source': f'gemini_api ({model})',
                            'language': lang,
                            'response': answer
                        }
            except Exception:
                continue

        # En cas d'échec de tous les modèles distants
        return {'success': False}

    def _expert_local_fallback(self, user_prompt: str, lang: str = 'fr') -> dict:
        """
        Moteur d'inférence expert local déterministe.
        Interroge directement l'ORM Django pour fournir une réponse exacte et instantanée
        même sans connexion Internet ou en cas de quota Gemini dépassé.
        """
        prompt_lower = user_prompt.lower()
        today = date.today()
        chauffeurs = Chauffeur.objects.annotate(visites_count=Count('visites')).all()

        # ==============================================================================
        # 1. QUESTION 1 : Permis qui expirent ce mois-ci / bientôt / expirés
        # ==============================================================================
        if any(w in prompt_lower for w in ['expire', 'expiration', 'ce mois', 'mois-ci', 'mois ci', 'perimé', 'valide', 'تنتهي', 'صلاحية', 'هذا الشهر', 'license']):
            expirant_ce_mois = [
                c for c in chauffeurs
                if c.date_expiration_permis.year == today.year and c.date_expiration_permis.month == today.month
            ]
            expires_deja = [c for c in chauffeurs if c.est_permis_expire]
            expirant_30j = [c for c in chauffeurs if 0 <= c.jours_avant_expiration <= 30]

            if lang == 'ar':
                if expirant_ce_mois:
                    items = [
                        f"• **{c.nom_complet}** ({c.entreprise_transport}) : تنتهي رخصته في **{c.date_expiration_permis.strftime('%d/%m/%Y')}** (صنف {c.categorie_permis}) — بقي {c.jours_avant_expiration} يوم."
                        for c in expirant_ce_mois
                    ]
                    resp = (
                        f"🪪 **السائقون الذين تنتهي رخص قيادتهم هذا الشهر ({len(expirant_ce_mois)})** :\n\n"
                        + "\n".join(items)
                        + "\n\n⚠️ *يرجى إشعار السائقين المعنيين لتجديد الفحص الطبي وبطاقة القيادة قبل انتهاء الصلاحية.*"
                    )
                else:
                    resp = (
                        "✅ **لا يوجد أي سائق تنتهي رخصة قيادته خلال هذا الشهر الحالي.**\n\n"
                        f"• عدد السائقين ذوي الرخص الصالحة : **{chauffeurs.filter(statut_validite_permis='VALIDE').count() if hasattr(chauffeurs, 'filter') else len(chauffeurs)}**\n"
                        f"• عدد الرخص المنتهية مسبقاً : **{len(expires_deja)}**"
                    )
            elif lang == 'en':
                if expirant_ce_mois:
                    items = [
                        f"• **{c.nom_complet}** ({c.entreprise_transport}): License expires on **{c.date_expiration_permis.strftime('%d/%m/%Y')}** (Cat. {c.categorie_permis}) — {c.jours_avant_expiration} days left."
                        for c in expirant_ce_mois
                    ]
                    resp = (
                        f"🪪 **Drivers whose license expires this month ({len(expirant_ce_mois)})**:\n\n"
                        + "\n".join(items)
                        + "\n\n⚠️ *Immediate action recommended to renew medical certifications and cards.*"
                    )
                else:
                    resp = (
                        "✅ **No drivers have a driving license expiring during the current month.**\n\n"
                        f"• Total active valid licenses: **{len([c for c in chauffeurs if not c.est_permis_expire])}**\n"
                        f"• Already expired licenses: **{len(expires_deja)}**"
                    )
            else:
                if expirant_ce_mois:
                    items = [
                        f"• **{c.nom_complet}** ({c.entreprise_transport}) : Permis `{c.numero_permis}` expire le **{c.date_expiration_permis.strftime('%d/%m/%Y')}** ({c.get_categorie_permis_display()}) — Reste **{c.jours_avant_expiration} jours**."
                        for c in expirant_ce_mois
                    ]
                    resp = (
                        f"🪪 **Chauffeurs dont le permis expire ce mois-ci ({len(expirant_ce_mois)})** :\n\n"
                        + "\n".join(items)
                        + "\n\n⚠️ *Action requise : programmer le renouvellement de la visite médicale et le recyclage FCO/FIMO.*"
                    )
                elif expirant_30j:
                    items = [
                        f"• **{c.nom_complet}** : expire le **{c.date_expiration_permis.strftime('%d/%m/%Y')}** (dans {c.jours_avant_expiration} jours)."
                        for c in expirant_30j
                    ]
                    resp = (
                        "ℹ️ Aucun permis n'expire strictement durant le mois civil en cours, mais **des permis expirent dans les 30 prochains jours** :\n\n"
                        + "\n".join(items)
                    )
                else:
                    resp = (
                        "✅ **Aucun chauffeur n'a de permis expirant ce mois-ci.**\n\n"
                        f"• Tous les permis sont à jour pour les {chauffeurs.count()} chauffeurs suivis.\n"
                        f"• Chauffeurs avec permis déjà expiré : **{len(expires_deja)}**"
                    )

        # ==============================================================================
        # 2. QUESTION 2 : Chauffeurs ayant effectué le plus de visites
        # ==============================================================================
        elif any(w in prompt_lower for w in ['plus de visite', 'plus de visites', 'classement', 'activité', 'top visite', 'top visites', 'الأكثر زيارة', 'الزيارات', 'most visit', 'most visits']):
            top_chauffeurs = chauffeurs.order_by('-visites_count')[:5]

            if lang == 'ar':
                items = [
                    f"• **{i+1}. {c.nom_complet}** : **{c.nb_visites} زيارة** | الشاحنة : `{c.immatriculation_camion or 'غير محددة'}` | الشركة : {c.entreprise_transport}"
                    for i, c in enumerate(top_chauffeurs)
                ]
                resp = (
                    "📊 **السائقون الأكثر تسجيلاً للزيارات في مستودعات وموانئ CargoLink** :\n\n"
                    + "\n".join(items)
                    + "\n\n💡 *يعكس هذا الترتيب إجمالي عمليات الشحن والتفريغ المسجلة في النظام.*"
                )
            elif lang == 'en':
                items = [
                    f"• **#{i+1} {c.nom_complet}**: **{c.nb_visites} visits** | Truck: `{c.immatriculation_camion or 'N/A'}` | Carrier: {c.entreprise_transport}"
                    for i, c in enumerate(top_chauffeurs)
                ]
                resp = (
                    "📊 **Top drivers by number of warehouse visits performed**:\n\n"
                    + "\n".join(items)
                    + "\n\n💡 *Reflects recorded dock operations (loading & unloading).* "
                )
            else:
                items = [
                    f"• **#{i+1} {c.nom_complet}** : **{c.nb_visites} visite(s)** enregistrée(s) | Camion : `{c.immatriculation_camion or 'N/A'}` | Entreprise : {c.entreprise_transport}"
                    for i, c in enumerate(top_chauffeurs)
                ]
                resp = (
                    "📊 **Classement des chauffeurs ayant effectué le plus de visites** :\n\n"
                    + "\n".join(items)
                    + "\n\n💡 *Ces statistiques regroupent les opérations de chargement, déchargement et contrôles d'accès effectués sur site.*"
                )

        # ==============================================================================
        # 3. QUESTION 3 : Résumé de l'historique d'un chauffeur donné
        # ==============================================================================
        elif any(w in prompt_lower for w in ['résume', 'resume', 'historique', 'fiche', 'لخص', 'سجل', 'summary', 'summarize', 'history']):
            # Recherche si un nom spécifique est mentionné
            cible = None
            for c in chauffeurs:
                if c.nom.lower() in prompt_lower or c.prenom.lower() in prompt_lower:
                    cible = c
                    break

            if not cible:
                cible = chauffeurs.first()

            if cible:
                visites_cible = VisiteChauffeur.objects.filter(chauffeur=cible).order_by('-date_visite')
                total_vis = visites_cible.count()
                dern_vis = visites_cible.first()

                if lang == 'ar':
                    resp = (
                        f"📋 **ملخص السجل الشامل للسائق : {cible.nom_complet}**\n\n"
                        f"• **الهوية والاتصال** : هاتف `{cible.telephone}` • الإقامة : {cible.ville_residence}\n"
                        f"• **الشركة المشغلة** : {cible.entreprise_transport}\n"
                        f"• **رخصة القيادة** : رقم `{cible.numero_permis}` (صنف {cible.categorie_permis}) • تنتهي في : **{cible.date_expiration_permis.strftime('%d/%m/%Y')}** ({cible.jours_avant_expiration} يوم متبقي)\n"
                        f"• **الشاحنة المخصصة** : `{cible.immatriculation_camion or 'لا توجد'}` ({cible.marque_camion})\n"
                        f"• **الحالة التشغيلية** : **{cible.get_statut_display()}**\n"
                        f"• **سجل النشاط** : **{total_vis} زيارة** مسجلة في المستودعات.\n"
                    )
                    if dern_vis:
                        resp += f"• **آخر عملية** : {dern_vis.get_type_operation_display()} في {dern_vis.date_visite.strftime('%d/%m/%Y')} ({dern_vis.entrepot.nom if dern_vis.entrepot else 'موقع'})."
                elif lang == 'en':
                    resp = (
                        f"📋 **Executive History Summary for Driver: {cible.nom_complet}**\n\n"
                        f"• **Contact & City**: `{cible.telephone}` • {cible.ville_residence}\n"
                        f"• **Transport Carrier**: {cible.entreprise_transport}\n"
                        f"• **Driver's License**: `{cible.numero_permis}` (Cat. {cible.categorie_permis}) • Expires on: **{cible.date_expiration_permis.strftime('%d/%m/%Y')}** ({cible.jours_avant_expiration} days left)\n"
                        f"• **Assigned Truck**: `{cible.immatriculation_camion or 'None'}` ({cible.marque_camion})\n"
                        f"• **Current Status**: **{cible.get_statut_display()}**\n"
                        f"• **Operational Track Record**: **{total_vis} total visits** completed.\n"
                    )
                    if dern_vis:
                        resp += f"• **Last Operation**: {dern_vis.get_type_operation_display()} on {dern_vis.date_visite.strftime('%d/%m/%Y')} at {dern_vis.entrepot.nom if dern_vis.entrepot else 'Hub'}."
                else:
                    resp = (
                        f"📋 **Synthèse de l'historique du chauffeur : {cible.nom_complet}**\n\n"
                        f"• **Identité & Contact** : Tél `{cible.telephone}` • Résidence : {cible.ville_residence}\n"
                        f"• **Entreprise** : {cible.entreprise_transport}\n"
                        f"• **Permis de conduire** : N° `{cible.numero_permis}` ({cible.get_categorie_permis_display()}) • Expiration : **{cible.date_expiration_permis.strftime('%d/%m/%Y')}** ({cible.jours_avant_expiration} j. restants)\n"
                        f"• **Véhicule affecté** : `{cible.immatriculation_camion or 'Aucun'}` ({cible.marque_camion} - {cible.get_type_camion_display()})\n"
                        f"• **Statut actuel** : **{cible.get_statut_display()}**\n"
                        f"• **Activité logistique** : **{total_vis} visite(s)** enregistrée(s).\n"
                    )
                    if dern_vis:
                        resp += f"• **Dernier passage** : {dern_vis.get_type_operation_display()} le {dern_vis.date_visite.strftime('%d/%m/%Y')} ({dern_vis.entrepot.nom if dern_vis.entrepot else 'Entrepôt'}, Quai {dern_vis.quai_numero})."
            else:
                resp = "Aucun chauffeur trouvé dans la base de données pour résumer son historique."

        # ==============================================================================
        # 4. Chauffeurs disponibles / prêts pour mission
        # ==============================================================================
        elif any(w in prompt_lower for w in ['disponible', 'disponibles', 'libre', 'libres', 'متاح', 'المتاحين', 'available']):
            dispos = chauffeurs.filter(statut='DISPONIBLE')
            if lang == 'ar':
                items = [f"• **{c.nom_complet}** ({c.telephone}) - شاحنة : `{c.immatriculation_camion or 'غير مخصصة'}`" for c in dispos]
                resp = f"🟢 **السائقون المتاحون حالياً للمهمات ({dispos.count()})** :\n\n" + ("\n".join(items) if items else "لا يوجد سائق متاح حالياً.")
            elif lang == 'en':
                items = [f"• **{c.nom_complet}** ({c.telephone}) - Truck: `{c.immatriculation_camion or 'Unassigned'}`" for c in dispos]
                resp = f"🟢 **Currently Available Drivers ({dispos.count()})**:\n\n" + ("\n".join(items) if items else "No drivers currently available.")
            else:
                items = [f"• **{c.nom_complet}** ({c.telephone}) — Camion : `{c.immatriculation_camion or 'Non attitré'}`" for c in dispos]
                resp = f"🟢 **Chauffeurs actuellement disponibles ({dispos.count()})** :\n\n" + ("\n".join(items) if items else "Aucun chauffeur disponible pour le moment.")

        # ==============================================================================
        # 5. Synthèse générale par défaut
        # ==============================================================================
        else:
            total = chauffeurs.count()
            dispos = chauffeurs.filter(statut='DISPONIBLE').count()
            en_mission = chauffeurs.filter(statut='EN_MISSION').count()
            expires = len([c for c in chauffeurs if c.est_permis_expire])

            if lang == 'ar':
                resp = (
                    f"🚚 **ملخص عام لأسطول السائقين (CargoLink AI)** :\n\n"
                    f"• إجمالي السائقين المسجلين : **{total}**\n"
                    f"• السائقون المتاحون للمهمات : **{dispos}** 🟢\n"
                    f"• السائقون في مهمة حالياً : **{en_mission}** 🚚\n"
                    f"• الرخص المنتهية الصلاحية : **{expires}** ⚠️\n\n"
                    f"يمكنك سؤالي باللغة العربية، الفرنسية أو الإنجليزية حول انتهاء الرخص، السائق الأكثر نشاطاً، أو ملخص أي سائق !"
                )
            elif lang == 'en':
                resp = (
                    f"🚚 **Driver Fleet Overview (CargoLink AI)**:\n\n"
                    f"• Total registered drivers: **{total}**\n"
                    f"• Available drivers: **{dispos}** 🟢\n"
                    f"• Drivers currently on mission: **{en_mission}** 🚚\n"
                    f"• Expired licenses: **{expires}** ⚠️\n\n"
                    f"Ask me anytime about expiring licenses, top visited drivers, or individual driver summaries!"
                )
            else:
                resp = (
                    f"🚚 **Vue d'ensemble de la flotte chauffeurs (CargoLink AI)** :\n\n"
                    f"• Total chauffeurs enregistrés : **{total}**\n"
                    f"• Chauffeurs disponibles : **{dispos}** 🟢\n"
                    f"• Chauffeurs en mission : **{en_mission}** 🚚\n"
                    f"• Permis expirés ou critiques : **{expires}** ⚠️\n\n"
                    f"Vous pouvez me poser une question en langage naturel (français, arabe ou anglais) "
                    f"sur l'expiration des permis, les statistiques de visites ou le dossier d'un chauffeur précis."
                )

        footer = {
            'ar': "\n\n*(⚡ تم إنشاء الإجابة بواسطة محرك الذكاء الاصطناعي المساعد للسائقين)*",
            'en': "\n\n*(⚡ Generated by CargoLink Driver AI Copilot)*",
            'fr': "\n\n*(⚡ Analyse générée par le Copilot IA Spécialisé Chauffeurs)*"
        }.get(lang, "\n\n*(⚡ Analyse générée par le Copilot IA Spécialisé Chauffeurs)*")

        return {
            'success': True,
            'source': 'expert_fallback',
            'language': lang,
            'response': resp + footer
        }
