/**
 * CargoLink - Système International d'Internationalisation (i18n)
 * Support complet : Français (FR) | English (EN) | العربية (AR - RTL)
 * Spécifiquement calibré pour la session Planificateur & le module Créneaux.
 */

(function () {
    'use strict';

    const TRANSLATIONS = {
        fr: {
            // Langue
            lang_name: "Français",
            lang_code: "fr",
            lang_dir: "ltr",

            // Navigation globale
            nav_warehouses: "Entrepôts & Quais",
            nav_slots: "Planning & Créneaux",
            nav_fleet: "Flotte & Camions",
            nav_drivers: "Chauffeurs",
            nav_login: "Connexion",
            nav_signup: "Créer un compte →",
            nav_profile: "Mon Profil",
            nav_profile_sub: "Modifier mes coordonnées & sécurité",
            nav_admin_dash: "Dashboard Admin",
            nav_admin_dash_sub: "Accéder au panneau d'administration",
            nav_logout: "Se Déconnecter",
            nav_logout_sub: "Fermer la session en cours",
            nav_role_admin: "Administrateur Système",
            nav_role_planner: "Planificateur de Créneaux",
            nav_role_wh_manager: "Gestionnaire d'Entrepôt",
            nav_role_carrier: "Transporteur / Chauffeur",
            nav_role_connected: "Connecté",
            nav_a11y_btn: "Mode Grand Texte (Accessibilité Ouvriers / Malvoyants)",
            nav_theme_btn: "Basculer Mode Clair / Sombre",
            nav_lang_btn: "Changer de langue",

            // Footer
            footer_desc: "Plateforme intelligente de coordination logistique : régulation des quais de chargement, synchronisation de flotte et optimisation des créneaux en temps réel.",
            footer_platform_title: "Plateforme & Services",
            footer_account_title: "Compte & Accès",
            footer_rights: "© 2026 CargoLink Technologies. Tous droits réservés.",

            // Page: Liste des créneaux
            slots_page_title: "Régulation & Créneaux des Quais",
            slots_page_sub: "Planification horaire des réceptions et expéditions, vérification des disponibilités et prévention des conflits.",
            btn_planning_view: "Vue Planning Graphique",
            btn_export_csv: "Export CSV",
            btn_slot_request: "📋 Demande de Créneau",
            btn_copilot_ai: "✨ Copilot IA Gemini",
            btn_new_slot: "Planifier un Créneau",
            
            // KPI Metrics
            kpi_total_slots: "Total Créneaux Enregistrés",
            kpi_today_slots: "Prévus Aujourd'hui",
            kpi_pending_slots: "En Attente de Validation",
            kpi_at_dock_slots: "À Quai (Opérations en cours)",
            kpi_completed_slots: "Opérations Terminées",

            // Filtres
            filter_search_ph: "Réf, transporteur, immatriculation, chauffeur...",
            filter_all_wh: "Tous les entrepôts",
            filter_all_status: "Tous les statuts",
            filter_all_types: "Tous types",
            filter_btn: "Filtrer",
            filter_reset: "Réinitialiser",

            // Tableau des créneaux
            th_ref_date: "Référence & Date",
            th_time_range: "Plage Horaire",
            th_wh_dock: "Entrepôt & Quai",
            th_operation: "Opération",
            th_carrier_truck: "Transporteur & Véhicule",
            th_driver: "Chauffeur",
            th_status: "Statut",
            th_actions: "Action",
            tb_no_driver: "Non assigné",
            tb_no_carrier: "Non assigné",
            tb_quai: "Quai",
            tb_details_btn: "Détails →",
            tb_empty_state: "Aucun créneau ne correspond à vos critères de recherche.",

            // Statuts
            status_en_attente: "En attente",
            status_confirme: "Confirmé",
            status_en_cours: "À quai / En cours",
            status_termine: "Terminé",
            status_annule: "Annulé",
            status_retard: "En retard",

            // Types d'opération
            type_chargement: "Chargement",
            type_dechargement: "Déchargement",
            type_mixte: "Mixte (Charge/Décharge)",

            // Priorités
            prio_normal: "Normal",
            prio_urgent: "Urgent",
            prio_tres_urgent: "Très Urgent",
            prio_faible: "Faible",

            // Page: Planning graphique
            planning_page_title: "Planning Graphique d'Occupation des Quais",
            planning_page_sub: "Vue temporelle synchronisée pour superviser l'occupation des quais, éviter les goulots d'étranglement et détecter les conflits.",
            btn_table_view: "Vue Tableau / Liste",
            planning_site_label: "Site Logistique :",
            nav_yesterday: "◀ Hier",
            nav_tomorrow: "Demain ▶",
            nav_today: "Aujourd'hui",
            th_dock_access: "QUAI D'ACCÈS",
            badge_free: "Libre",

            // Page: Formulaire Créneau (Create & Edit)
            form_back_link: "◀ Retour au planning des créneaux",
            form_create_title: "Planifier un Nouveau Créneau",
            form_edit_title: "Modifier le Créneau",
            form_create_sub: "Programmer une réservation de quai avec vérification des conflits et optimisation IA.",
            form_edit_sub: "Ajustez les détails opérationnels, les horaires ou les ressources de transport.",
            form_sec1_title: "🏭 1. Infrastructure & Plage Horaire",
            form_sec2_title: "🚛 2. Opération & Transport",
            form_sec3_title: "🚚 3. Véhicule & Chauffeur",
            form_sec4_title: "📦 4. Marchandises & Consignes",
            lbl_target_wh: "Entrepôt cible *",
            lbl_target_dock: "Quai de chargement / déchargement *",
            btn_ai_dock_opt: "✨ Optimisation Quai (IA)",
            lbl_dock_help: "Sélectionnez un quai ou utilisez l'IA pour attribuer le quai optimal",
            lbl_op_date: "Date d'opération *",
            lbl_start_time: "Heure de début *",
            lbl_end_time: "Heure de fin *",
            lbl_op_type: "Type d'opération *",
            lbl_priority: "Priorité logistique *",
            lbl_carrier_co: "Société de transport / Transporteur",
            lbl_carrier_co_help: "Ex: DHL Logistics, Gefco, XPO...",
            lbl_truck_opt: "Camion / Véhicule",
            lbl_driver_opt: "Chauffeur assigné",
            lbl_goods_type: "Nature des marchandises",
            lbl_goods_type_help: "Ex: Palettes alimentaires, pièces industrielles...",
            lbl_weight: "Poids estimé (kg)",
            lbl_volume: "Volume estimé (m³)",
            lbl_notes: "Instructions / Remarques pour les caristes",
            lbl_status_field: "Statut du créneau *",
            btn_save_slot: "Enregistrer le créneau",
            btn_cancel_link: "Annuler",

            // Page: Demande de créneau
            demand_page_title: "Demande de Réservation de Créneau",
            demand_page_sub: "Soumettez votre demande d'accès à quai. Elle sera examinée par le responsable d'entrepôt.",
            demand_sec_smart: "✨ Recommandation de Quai Intelligente",
            btn_submit_demand: "Soumettre la demande de créneau",

            // Page: Détail Créneau
            detail_voucher_tag: "Bon de passage à quai",
            detail_back_link: "◀ Retour à la liste des créneaux",
            btn_print_voucher: "🖨️ Imprimer Bon de Passage",
            btn_edit_slot: "✏️ Modifier",
            btn_cancel_slot: "❌ Annuler ce créneau",
            btn_action_confirm: "✅ Valider ce créneau",
            btn_action_start: "🚚 Démarrer l'opération (À quai)",
            btn_action_complete: "🏁 Clôturer l'opération (Terminé)",
            lbl_priority_label: "Priorité :",
            detail_sec_infra: "🏭 Infrastructure Logistique",
            detail_sec_transport: "🚛 Transport & Véhicule",
            detail_sec_goods: "📦 Marchandises & Consignes",
            detail_sec_timeline: "⏱️ Chronologie & Suivi des Opérations",
            detail_lbl_wh: "Entrepôt :",
            detail_lbl_dock: "Quai assigné :",
            detail_lbl_slot_time: "Créneau horaire :",
            detail_lbl_carrier: "Transporteur :",
            detail_lbl_truck: "Camion :",
            detail_lbl_driver: "Chauffeur :",
            detail_lbl_phone: "Téléphone chauffeur :",
            detail_lbl_weight: "Poids estimé :",
            detail_lbl_volume: "Volume estimé :",
            detail_lbl_goods_nature: "Type de fret :",
            detail_lbl_instructions: "Consignes caristes :",
            detail_lbl_created_by: "Créé par :",
            detail_lbl_created_at: "Créé le :",

            // Page: Confirmation d'annulation
            cancel_page_title: "Confirmation d'Annulation de Créneau",
            cancel_page_sub: "Cette action libérera immédiatement la réservation du quai pour les autres transporteurs.",
            cancel_warning_box: "⚠️ Êtes-vous certain de vouloir annuler le créneau référence",
            cancel_reason_lbl: "Motif d'annulation :",
            btn_confirm_cancel: "Confirmer l'annulation définitive",
            btn_back_to_slot: "Non, retourner au créneau",

            // Page: Assistant IA Gemini
            ai_page_title: "Assistant IA Gemini • Copilot Créneaux",
            ai_badge_live: "IA EN DIRECT",
            ai_quick_questions_title: "💡 Suggestions de questions rapides pour le planificateur :",
            ai_q1: "Quels sont les créneaux prévus aujourd'hui ?",
            ai_q2: "Y a-t-il des retards ou des conflits de quais ?",
            ai_q3: "Quels quais sont actuellement disponibles ?",
            ai_q4: "Comment optimiser le planning de demain ?",
            ai_chat_ph: "Posez votre question sur les créneaux, les quais, les retards ou l'optimisation...",
            ai_btn_send: "Envoyer",
            ai_welcome_title: "Bonjour ! Je suis votre Copilot IA dédié au planning des quais.",
            ai_welcome_desc: "Interrogez-moi pour vérifier les disponibilités, auditer les conflits horaires, ou obtenir des recommandations d'allocation de quais.",
            ai_thinking: "L'assistant analyse les données du planning...",

            // Module Chauffeurs & Flotte
            page_title: "Gestion des Chauffeurs",
            page_subtitle: "Supervisez les conducteurs de fret, contrôlez la conformité des permis (C, CE, ADR) et suivez l'historique de passage sur vos sites logistiques.",
            btn_ai: "Assistant IA Chauffeurs",
            btn_mobile: "Portail Mobile",
            btn_export: "Export CSV",
            btn_add: "Ajouter un Chauffeur",
            kpi_total: "Total Chauffeurs",
            kpi_total_sub: "enregistrés dans la flotte",
            kpi_dispo: "Disponibles",
            kpi_dispo_sub: "prêts pour affectation",
            kpi_mission: "En Mission",
            kpi_mission_sub: "en transit sur le réseau",
            kpi_aquai: "À Quai",
            kpi_aquai_sub: "sur site logistique",
            kpi_repos: "En Repos",
            kpi_repos_sub: "indisponibles temporairement",
            kpi_alertes: "Alertes Permis",
            kpi_alertes_sub: "expirés ou à renouveler (< 30j)",
            kpi_visites: "Total Visites",
            kpi_visites_sub: "passages aux entrepôts",
            filter_search_placeholder: "Rechercher par nom, prénom, CIN, entreprise...",
            filter_status_all: "Tous les statuts opérationnels",
            filter_cat_all: "Toutes les catégories de permis",
            filter_alert_all: "Toutes les alertes permis",
            filter_alert_expire: "⚠️ Permis expirés uniquement",
            filter_alert_bientot: "⏳ Expire dans moins de 30 jours",
            filter_alert_valide: "✅ Permis valides (> 30 jours)",
            filter_submit: "Filtrer",
            filter_reset: "Réinitialiser",
            spec_truck: "Camion attitré",
            spec_company: "Entreprise",
            spec_city: "Résidence",
            spec_phone: "Téléphone",
            spec_license: "Permis & Validité",
            spec_visits: "Visites & Passages",
            badge_expire: "Expiré",
            badge_soon_prefix: "Expire dans ",
            badge_soon_suffix: " jours",
            badge_valid: "Permis Valide",
            visits_suffix: "visite",
            visits_plural_suffix: "visites",
            btn_full_profile: "Fiche Complète",
            btn_edit_tooltip: "Modifier le chauffeur",
            no_driver_title: "Aucun chauffeur trouvé",
            no_driver_desc: "Aucun profil de conducteur ne correspond à vos critères de recherche ou filtres.",
            btn_add_first: "Ajouter le premier chauffeur",
            breadcrumb_back: "Retour à la liste des chauffeurs",
            badge_portuaire: "🛡️ Badge Portuaire Actif",
            statut_btn_disponible: "Disponible",
            statut_btn_mission: "En Mission",
            statut_btn_aquai: "À Quai",
            statut_btn_repos: "En Repos",
            btn_edit: "Modifier Fiche",
            btn_add_visit: "Enregistrer Visite",
            btn_delete_title: "Supprimer ce chauffeur",
            panel_identity_title: "Identité & Coordonnées",
            label_fullname: "Prénom & Nom",
            label_cin: "Numéro CIN / Passeport",
            label_phone: "Téléphone principal",
            label_emergency_phone: "Contact d'urgence",
            label_email: "Adresse Email",
            label_residence: "Résidence",
            label_hire_date: "Date d'embauche",
            not_provided: "Non renseigné",
            not_specified: "Non spécifié",
            panel_license_title: "Permis de Conduire & Conformité",
            label_license_num: "Numéro de permis",
            label_license_cat: "Catégorie",
            label_license_issued: "Délivré le",
            label_license_expiry: "Date d'expiration",
            panel_truck_title: "Camion Habituel & Fret",
            label_truck_plate: "Immatriculation",
            no_truck_assigned: "Aucun véhicule attitré",
            label_truck_model: "Modèle / Marque",
            label_truck_type: "Gabarit / Type",
            label_truck_capacity: "Capacité de charge",
            unit_tonnes: "Tonnes",
            label_company: "Entreprise",
            label_remarks: "Remarques :",
            op_badge_title: "⚡ Régulation Logistique & Flotte",
            op_mission_active: "🟢 Mission Active",
            op_awaiting_assignment: "⚪ En Attente d'Affectation",
            op_section_title: "Affectation Camion, Créneau & Quai Disponibles",
            op_section_desc: "Règle de régulation CargoLink : un chauffeur doit être affecté à un camion disponible et à un créneau sur quai disponible.",
            op_btn_release: "Libérer la mission & Rendre disponible",
            op_current_title: "📋 État de l'Affectation Actuelle",
            op_current_truck: "Camion assigné",
            op_no_truck: "Aucun camion",
            op_current_availability: "Disponibilité du véhicule",
            op_not_central_fleet: "Non rattaché à la flotte centrale",
            op_current_slot: "Mission / Créneau actif",
            op_awaiting_mission: "En attente de mission",
            op_new_title: "⚡ Affecter une Nouvelle Mission",
            op_label_truck: "Camion disponible",
            op_count_free: "libres",
            op_select_truck: "-- Sélectionner un camion disponible --",
            op_label_dock: "Entrepôt & Quai disponible",
            op_select_dock: "-- Sélectionner un quai disponible --",
            op_label_slot: "Créneau Quai disponible :",
            op_select_slot_auto: "-- Génération automatique d'un créneau immédiat --",
            op_btn_submit: "Valider l'Affectation Mission",
            visits_section_title: "Historique des Visites & Passages aux Entrepôts",
            visits_section_desc: "Traçabilité complète des déchargements, chargements et contrôles effectués par ce conducteur.",
            visits_btn_add: "Ajouter une Visite",
            th_date_time: "Date & Horaires",
            th_dock: "Entrepôt & Quai",
            th_cmr: "N° Bon / CMR",
            th_operation: "Opération",
            th_duration: "Durée",
            th_status: "Statut",
            th_signoff: "Émargement",
            site_external: "Site Externe",
            unit_min: "min",
            signoff_validated: "✅ Validé",
            signoff_pending: "⏳ En attente",
            no_visits_msg: "Aucune visite ni passage enregistré pour l'instant pour ce chauffeur.",
            btn_record_first_visit: "Enregistrer la première visite",
            slots_section_title: "Créneaux & Réservations Récentes Associées",
            slots_section_desc: "Synchronisé en temps réel avec le module Créneaux & Régulation des Quais.",
            btn_view_all_slots: "Voir tous les créneaux →",
            th_slot_ref: "Référence",
            th_slot_datetime: "Date & Créneau",
            th_slot_dock: "Quai & Entrepôt",
            th_action: "Action",
            btn_details: "Détails",
            alert_expired_strong: "Permis Expiré !",
            alert_expired_text: "Ce chauffeur n'est plus autorisé à circuler. Renouvellement urgent requis.",
            alert_soon_strong: "Expiration proche ({days} jours) !",
            alert_soon_text: "Penser au renouvellement de la visite médicale et de la carte conducteur.",
            alert_valid_strong: "Permis en règle.",
            alert_valid_text: "Valide pour encore {days} jours.",
            btn_cancel_back: "Annuler et retourner",
            form_subtitle: "Renseignez les données administratives, les catégories de permis et le véhicule attitré du conducteur.",
            form_errors_title: "Erreurs détectées :",
            sec1_title: "1. Informations Personnelles & Contact",
            lbl_prenom: "Prénom *",
            lbl_nom: "Nom de famille *",
            lbl_cin: "Numéro CIN / Passeport",
            lbl_email: "Adresse Email",
            lbl_phone: "Téléphone principal *",
            lbl_emergency_phone: "Téléphone d'urgence",
            lbl_birthdate: "Date de naissance",
            lbl_hiredate: "Date d'embauche",
            lbl_residence: "Ville de résidence",
            lbl_photo: "Photo du chauffeur",
            sec2_title: "2. Permis de Conduire & Validité",
            lbl_license_num: "Numéro de Permis *",
            lbl_license_cat: "Catégorie de Permis *",
            lbl_license_issued: "Date de délivrance",
            lbl_license_expiry: "Date d'expiration / Validité *",
            sec3_title: "3. Entreprise de Transport & Véhicule Associé",
            lbl_company: "Société / Entreprise de Transport *",
            lbl_carrier_account: "Compte Utilisateur Transporteur",
            lbl_truck_plate: "Immatriculation du Camion",
            lbl_truck_model: "Marque / Modèle",
            lbl_truck_type: "Type de gabarit",
            lbl_truck_capacity: "Capacité (Tonnes)",
            sec4_title: "4. Statut Opérationnel & Sécurité",
            lbl_statut: "Statut Opérationnel *",
            lbl_badge_portuaire: "Badge d'accès portuaire / sécurisé actif",
            lbl_remarks: "Remarques & Habilitations particulières",
            btn_cancel: "Annuler",
            btn_submit_create: "Enregistrer le Chauffeur",
            btn_submit_update: "Enregistrer les Modifications",
            title_create: "Nouveau Chauffeur",
            title_update_prefix: "Modifier ",

            // Module Entrepôts & Quais
            wh_page_title: "Entrepôts & Régulation des Quais",
            wh_page_sub: "Supervisez vos infrastructures de stockage, surveillez l'état d'occupation des quais et optimisez les flux entrants.",
            wh_btn_optimizer: "Optimiseur IA",
            wh_btn_all_quais: "Voir tous les Quais",
            wh_btn_add_warehouse: "Ajouter un Entrepôt",
            wh_btn_add_quai: "Ajouter un Quai",
            wh_kpi_operational: "Entrepôts Opérationnels",
            wh_kpi_active_quais: "Quais de Chargement",
            wh_kpi_available_quais: "Quais Disponibles",
            wh_kpi_occupied_quais: "Quais Occupés",
            wh_kpi_total_capacity: "Capacité Totale (Palettes)",
            wh_search_placeholder: "Rechercher par nom, code, ville...",
            wh_filter_status_all: "Tous les statuts",
            wh_filter_city_all: "Toutes les villes",
            wh_filter_type_all: "Tous types de quais",
            wh_status_actif: "Opérationnel / Actif",
            wh_status_maintenance: "En maintenance",
            wh_status_ferme: "Fermé temporairement",
            wh_status_disponible: "Disponible",
            wh_status_occupe: "En cours / Occupé",
            wh_status_reserve: "Réservé (Planifié)",
            wh_stat_capacity: "Capacité",
            wh_stat_area: "Superficie",
            wh_stat_quais: "Quais Actifs",
            wh_stat_avail: "Disponibilité",
            wh_btn_details: "Détails & Quais →",
            wh_empty_title: "Aucun entrepôt trouvé",
            wh_empty_desc: "Aucun site de stockage ne correspond à vos critères de recherche actuels.",
            wh_btn_add_first: "Ajouter le premier entrepôt",
            wh_back_list: "Annuler et retourner",
            wh_meta_code: "Code Identification",
            wh_meta_city: "Localisation",
            wh_meta_manager: "Responsable du Site",
            wh_meta_phone: "Téléphone",
            wh_meta_email: "Email de Contact",
            wh_meta_hours: "Horaires d'Ouverture",
            wh_sec_quais_title: "Quais de Chargement & Déchargement",
            wh_sec_quais_sub: "Surveillance en temps réel et régulation des accès pour les transporteurs.",
            quai_feature_leveler: "Niveleur hydraulique",
            quai_feature_seal: "Sas isotherme",
            quai_spec_flow: "Débit moyen :",
            quai_spec_simultaneous: "Camions max :",
            quai_spec_truck_type: "Gabarit :",
            quai_btn_occupy: "Marquer Occupé",
            quai_btn_release: "Libérer le Quai",
            wh_form_sub: "Renseignez les caractéristiques techniques, la localisation et les capacités de stockage de l'entrepôt.",
            quai_form_sub: "Définissez les spécifications techniques du quai, sa capacité horaire et ses équipements.",
            wh_lbl_nom: "Nom de l'Entrepôt *",
            wh_lbl_code: "Code d'Identification Unique *",
            wh_lbl_adresse: "Adresse Postale Complète *",
            wh_lbl_ville: "Ville *",
            wh_lbl_code_postal: "Code Postal *",
            wh_lbl_telephone: "Téléphone de Contact",
            wh_lbl_email: "Email de Contact",
            wh_lbl_statut: "Statut d'Exploitation",
            wh_lbl_gestionnaire: "Responsable / Gestionnaire",
            wh_lbl_capacite: "Capacité de Stockage (Palettes) *",
            wh_lbl_superficie: "Superficie en m²",
            wh_lbl_ouverture: "Heure d'Ouverture (Format HH:MM) *",
            wh_lbl_fermeture: "Heure de Fermeture (Format HH:MM) *",
            wh_lbl_jours: "Jours d'Ouverture",
            quai_lbl_entrepot: "Entrepôt Rattaché *",
            quai_lbl_numero: "Numéro / Identifiant du Quai *",
            quai_lbl_type: "Type de Quai *",
            quai_lbl_statut: "Statut Initial *",
            quai_lbl_gabarit: "Gabarit Camion Admis",
            quai_lbl_simultaneous: "Camions Simultanés (1 à 5)",
            quai_lbl_flow: "Débit Moyen (Palettes / Heure) *",
            quai_lbl_equipments: "Équipements Techniques & Sécurité",
            quai_lbl_remarks: "Consignes Particulières / Remarques",
            btn_save_warehouse: "Enregistrer l'entrepôt",
            btn_save_quai: "Créer le quai",

            // Module Flotte & Camions
            truck_page_title: "Gestion de la Flotte • Camions",
            truck_page_sub: "Supervision des véhicules de transport, disponibilités opérationnelles, charges utiles et maintenance prédictive",
            truck_btn_add: "Ajouter un Camion",
            truck_kpi_total: "Total Véhicules",
            truck_kpi_available: "Disponibles / Prêts",
            truck_kpi_transit: "En Transit / Route",
            truck_kpi_dock: "À Quai (En cours)",
            truck_kpi_maintenance: "En Maintenance",
            truck_kpi_urgent_ct: "Contrôles Urgents (≤15j)",
            truck_search_placeholder: "Recherche par immatriculation, marque, modèle, transporteur...",
            truck_filter_all_status: "Tous les états",
            truck_filter_all_types: "Tous les gabarits",
            truck_filter_all_norms: "Toutes les normes",
            truck_spec_type: "Type / Gabarit",
            truck_spec_payload: "Charge Utile",
            truck_spec_pallets: "Capacité palettes",
            truck_spec_mileage: "Kilométrage",
            truck_spec_carrier_default: "Transporteur Indépendant",
            truck_btn_view_ai: "Fiche Véhicule • IA",
            truck_empty_title: "Aucun camion ne correspond à vos critères",
            truck_empty_desc: "Vérifiez les filtres de recherche ou enregistrez un premier véhicule pour commencer la gestion de votre flotte.",
            truck_btn_add_first: "Ajouter un Camion",
            truck_back_list: "Retour au catalogue de la flotte",
            truck_btn_quick_status: "Modifier État",
            truck_sec_specs_title: "Caractéristiques Techniques & Logistiques",
            truck_spec_max_payload: "Charge Utile Max",
            truck_spec_norm: "Norme Antipollution",
            truck_spec_last_ct: "Dernier Contrôle Technique",
            truck_spec_next_ct: "Prochain Contrôle Exigé",
            truck_ai_diag_title: "Diagnostic de Maintenance Prédictive (IA)",
            truck_ai_health_score: "Indice de Santé Global",
            truck_ai_recommendations: "Recommandations & Alertes Préventives",
            truck_sec_passages_title: "Historique Récent des Passages & Créneaux",
            truck_form_back: "Retour à la liste des camions",
            truck_form_sub: "Renseignez les spécifications techniques et l'état opérationnel du véhicule.",
            truck_sec_id: "1. Identification & Gabarit",
            truck_sec_capacities: "2. Capacités & Motorisation",
            truck_sec_maintenance: "3. Contrôle Technique & Exploitation",
            truck_lbl_immat: "Immatriculation",
            truck_lbl_marque: "Marque",
            truck_lbl_modele: "Modèle",
            truck_lbl_year: "Année de mise en service",
            truck_lbl_type: "Type / Gabarit du véhicule",
            truck_lbl_tonnage: "Charge utile maximale (Tonnes)",
            truck_lbl_palettes: "Capacité de stockage (Palettes)",
            truck_lbl_km: "Kilométrage actuel (km)",
            truck_lbl_norm: "Norme environnementale",
            truck_lbl_societe: "Entreprise / Société de transport",
            truck_lbl_last_ct: "Dernier contrôle technique",
            truck_lbl_next_ct: "Date limite du prochain contrôle",
            truck_lbl_etat: "État opérationnel initial",
            truck_lbl_notes: "Observations & Carnet d'entretien",
            truck_btn_save: "Enregistrer le Camion",
            btn_filter: "Filtrer",
            btn_reset: "Réinitialiser",
            btn_edit: "Modifier",
            btn_delete: "Supprimer",

            // Toasts & feedback
            toast_lang_changed: "🌐 Langue basculée en Français",
                    quai_btn_add_first: "Ajouter un Nouveau Quai",
            quai_btn_manage_wh: "Gérer les Entrepôts",
            quai_empty_desc: "Aucun quai ne correspond aux critères de filtre sélectionnés.",
            quai_empty_title: "Aucun quai trouvé",
            quai_filter_status_all: "Tous les statuts de quai",
            quai_filter_wh_all: "Tous les entrepôts",
            quai_meta_capacity: "Capacité de Traitement",
            quai_meta_equipments: "Équipements de Sécurité",
            quai_meta_gabarit: "Gabarit Véhicules Admis",
            quai_meta_notes: "Consignes d'accès :",
            quai_meta_type: "Type de Quai",
            quai_page_sub: "Vue d'ensemble et contrôle en temps réel de tous les quais du réseau logistique.",
            quai_page_title: "Régulation des Quais de Chargement",
            wh_btn_add_quai_this: "Ajouter un Quai à cet Entrepôt",
            wh_meta_capacity: "Capacité de Stockage",
            wh_meta_contact: "Contact & Responsable",
            wh_meta_quais: "Quais & Disponibilité",
            truck_ai_badge: "Google Gemini IA",
            truck_ai_btn_refresh: "Actualiser IA",
            truck_ai_carbon_label: "Indice d'Émission Carbone (ODD 12) :",
            truck_ai_critical_comps: "Composants Mécaniques Surveillés",
            truck_ai_risk_lvl: "Niveau de Risque",
            truck_ai_sub: "Diagnostic de fiabilité mécanique et prédiction d'usure calculés par intelligence artificielle.",
            truck_ai_synthesis: "SYNTHÈSE DE L'ÉTAT DU VÉHICULE",
            truck_ai_tip_label: "Conseil Prédictif :",
            truck_ai_title: "Score de Santé & Maintenance Prédictive",
            truck_btn_add_passage: "+ Enregistrer Passage",
            truck_btn_submit_pass: "Valider le Passage",
            truck_empty_passages: "Aucun passage en entrepôt n'a encore été consigné pour ce véhicule.",
            truck_form_new_passage: "Nouveau Passage en Entrepôt",
            truck_lbl_pass_cmr: "N° Bon de Livraison / CMR",
            truck_lbl_pass_dock: "Quai d'accueil",
            truck_lbl_pass_notes: "Observations de quai",
            truck_lbl_pass_op: "Opération",
            truck_lbl_pass_status: "Statut",
            truck_lbl_pass_weight: "Poids mesuré au pont-bascule (kg)",
            truck_lbl_pass_wh: "Entrepôt de transit",
            truck_lbl_volume: "Volume utile (m³)",
            truck_spec_carrier: "Société de Transport",
            truck_spec_last_maint: "Dernière Maintenance",
            truck_spec_odometer: "Compteur Kilométrique",
            truck_spec_pallets_euro: "Capacité Palettes",
            truck_spec_volume: "Volume de Fret",
        },

        en: {
            // Language
            lang_name: "English",
            lang_code: "en",
            lang_dir: "ltr",

            // Global Navigation
            nav_warehouses: "Warehouses & Docks",
            nav_slots: "Schedule & Slots",
            nav_fleet: "Fleet & Trucks",
            nav_drivers: "Drivers",
            nav_login: "Login",
            nav_signup: "Create Account →",
            nav_profile: "My Profile",
            nav_profile_sub: "Edit personal details & security",
            nav_admin_dash: "Admin Dashboard",
            nav_admin_dash_sub: "Access administrative control panel",
            nav_logout: "Log Out",
            nav_logout_sub: "End current active session",
            nav_role_admin: "System Administrator",
            nav_role_planner: "Slot Planner",
            nav_role_wh_manager: "Warehouse Manager",
            nav_role_carrier: "Carrier / Driver",
            nav_role_connected: "Connected",
            nav_a11y_btn: "Large Text Mode (Workers / Low-Vision Accessibility)",
            nav_theme_btn: "Toggle Light / Dark Mode",
            nav_lang_btn: "Switch language",

            // Footer
            footer_desc: "Smart logistics coordination platform: dock regulation, fleet synchronization, and real-time slot optimization.",
            footer_platform_title: "Platform & Services",
            footer_account_title: "Account & Access",
            footer_rights: "© 2026 CargoLink Technologies. All rights reserved.",

            // Page: Slots List
            slots_page_title: "Dock Scheduling & Time Slots",
            slots_page_sub: "Hourly scheduling for arrivals and departures, availability validation, and conflict prevention.",
            btn_planning_view: "Visual Timeline View",
            btn_export_csv: "Export CSV",
            btn_slot_request: "📋 Request Slot",
            btn_copilot_ai: "✨ Gemini AI Copilot",
            btn_new_slot: "Schedule a Slot",

            // KPI Metrics
            kpi_total_slots: "Total Registered Slots",
            kpi_today_slots: "Scheduled Today",
            kpi_pending_slots: "Pending Approval",
            kpi_at_dock_slots: "At Dock (Ongoing Operations)",
            kpi_completed_slots: "Completed Operations",

            // Filters
            filter_search_ph: "Ref, carrier, plate number, driver...",
            filter_all_wh: "All warehouses",
            filter_all_status: "All statuses",
            filter_all_types: "All types",
            filter_btn: "Filter",
            filter_reset: "Reset",

            // Table
            th_ref_date: "Reference & Date",
            th_time_range: "Time Range",
            th_wh_dock: "Warehouse & Dock",
            th_operation: "Operation",
            th_carrier_truck: "Carrier & Vehicle",
            th_driver: "Driver",
            th_status: "Status",
            th_actions: "Action",
            tb_no_driver: "Unassigned",
            tb_no_carrier: "Unassigned",
            tb_quai: "Dock",
            tb_details_btn: "Details →",
            tb_empty_state: "No time slots match your search criteria.",

            // Statuses
            status_en_attente: "Pending",
            status_confirme: "Confirmed",
            status_en_cours: "At Dock / In Progress",
            status_termine: "Completed",
            status_annule: "Cancelled",
            status_retard: "Delayed",

            // Operation Types
            type_chargement: "Loading",
            type_dechargement: "Unloading",
            type_mixte: "Mixed (Load/Unload)",

            // Priorities
            prio_normal: "Normal",
            prio_urgent: "Urgent",
            prio_tres_urgent: "High Urgent",
            prio_faible: "Low",

            // Page: Graphical Planning
            planning_page_title: "Visual Dock Occupancy Schedule",
            planning_page_sub: "Synchronized timeline to monitor dock usage, avoid bottlenecks, and detect schedule conflicts.",
            btn_table_view: "Table / List View",
            planning_site_label: "Logistics Facility:",
            nav_yesterday: "◀ Yesterday",
            nav_tomorrow: "Tomorrow ▶",
            nav_today: "Today",
            th_dock_access: "ACCESS DOCK",
            badge_free: "Available",

            // Page: Slot Form
            form_back_link: "◀ Back to slots schedule",
            form_create_title: "Schedule a New Time Slot",
            form_edit_title: "Edit Time Slot",
            form_create_sub: "Book a loading dock with real-time conflict checking and AI optimization.",
            form_edit_sub: "Adjust operational details, time ranges, or assigned transport equipment.",
            form_sec1_title: "🏭 1. Facility & Time Schedule",
            form_sec2_title: "🚛 2. Operation & Carrier",
            form_sec3_title: "🚚 3. Vehicle & Driver",
            form_sec4_title: "📦 4. Freight & Instructions",
            lbl_target_wh: "Target Warehouse *",
            lbl_target_dock: "Loading / Unloading Dock *",
            btn_ai_dock_opt: "✨ AI Dock Optimizer",
            lbl_dock_help: "Select a dock or let AI suggest the optimal allocation",
            lbl_op_date: "Operation Date *",
            lbl_start_time: "Start Time *",
            lbl_end_time: "End Time *",
            lbl_op_type: "Operation Type *",
            lbl_priority: "Logistics Priority *",
            lbl_carrier_co: "Transport Company / Carrier",
            lbl_carrier_co_help: "e.g. DHL Logistics, Gefco, XPO...",
            lbl_truck_opt: "Truck / Vehicle",
            lbl_driver_opt: "Assigned Driver",
            lbl_goods_type: "Nature of Goods",
            lbl_goods_type_help: "e.g. Palletized food, machinery parts...",
            lbl_weight: "Estimated Weight (kg)",
            lbl_volume: "Estimated Volume (m³)",
            lbl_notes: "Instructions / Notes for forklift operators",
            lbl_status_field: "Slot Status *",
            btn_save_slot: "Save Time Slot",
            btn_cancel_link: "Cancel",

            // Page: Slot Request
            demand_page_title: "Dock Slot Booking Request",
            demand_page_sub: "Submit a dock reservation request. It will be reviewed by the warehouse supervisor.",
            demand_sec_smart: "✨ Smart Dock Allocation Recommendation",
            btn_submit_demand: "Submit Slot Request",

            // Page: Slot Detail
            detail_voucher_tag: "Dock Pass Voucher",
            detail_back_link: "◀ Back to slots list",
            btn_print_voucher: "🖨️ Print Pass Voucher",
            btn_edit_slot: "✏️ Edit",
            btn_cancel_slot: "❌ Cancel Slot",
            btn_action_confirm: "✅ Confirm Slot",
            btn_action_start: "🚚 Start Operation (At Dock)",
            btn_action_complete: "🏁 Finish Operation (Completed)",
            lbl_priority_label: "Priority:",
            detail_sec_infra: "🏭 Logistics Infrastructure",
            detail_sec_transport: "🚛 Transport & Vehicle",
            detail_sec_goods: "📦 Goods & Handling Notes",
            detail_sec_timeline: "⏱️ Milestones & Operational Timeline",
            detail_lbl_wh: "Warehouse:",
            detail_lbl_dock: "Assigned Dock:",
            detail_lbl_slot_time: "Time Window:",
            detail_lbl_carrier: "Carrier:",
            detail_lbl_truck: "Truck:",
            detail_lbl_driver: "Driver:",
            detail_lbl_phone: "Driver Phone:",
            detail_lbl_weight: "Est. Weight:",
            detail_lbl_volume: "Est. Volume:",
            detail_lbl_goods_nature: "Freight Type:",
            detail_lbl_instructions: "Handler Notes:",
            detail_lbl_created_by: "Created By:",
            detail_lbl_created_at: "Created At:",

            // Page: Cancellation Confirmation
            cancel_page_title: "Confirm Time Slot Cancellation",
            cancel_page_sub: "This will instantly release the reserved dock space for other carriers.",
            cancel_warning_box: "⚠️ Are you sure you want to cancel the time slot reference",
            cancel_reason_lbl: "Cancellation Reason:",
            btn_confirm_cancel: "Confirm Permanent Cancellation",
            btn_back_to_slot: "No, Return to Slot",

            // Page: Gemini AI Assistant
            ai_page_title: "Gemini AI Assistant • Slots Copilot",
            ai_badge_live: "AI LIVE",
            ai_quick_questions_title: "💡 Quick prompt suggestions for the planner:",
            ai_q1: "What slots are scheduled for today?",
            ai_q2: "Are there any delays or dock conflicts?",
            ai_q3: "Which docks are currently available?",
            ai_q4: "How can we optimize tomorrow's schedule?",
            ai_chat_ph: "Ask questions regarding slots, docks, delays or schedule optimization...",
            ai_btn_send: "Send",
            ai_welcome_title: "Hello! I am your AI Copilot for dock scheduling.",
            ai_welcome_desc: "Ask me to check availability, audit schedule conflicts, or get intelligent dock allocation recommendations.",
            ai_thinking: "The assistant is analyzing schedule data...",

            // Chauffeurs & Fleet Module
            page_title: "Drivers Management",
            page_subtitle: "Supervise freight drivers, monitor license compliance (C, CE, ADR), and track warehouse gate log history.",
            btn_ai: "Driver AI Assistant",
            btn_mobile: "Mobile Portal",
            btn_export: "Export CSV",
            btn_add: "Add Driver",
            kpi_total: "Total Drivers",
            kpi_total_sub: "registered in fleet",
            kpi_dispo: "Available",
            kpi_dispo_sub: "ready for dispatch",
            kpi_mission: "On Mission",
            kpi_mission_sub: "in transit on road",
            kpi_aquai: "At Dock",
            kpi_aquai_sub: "on facility premises",
            kpi_repos: "On Rest",
            kpi_repos_sub: "off-duty / resting",
            kpi_alertes: "License Alerts",
            kpi_alertes_sub: "expired or renewing (< 30d)",
            kpi_visites: "Total Visits",
            kpi_visites_sub: "logged warehouse passes",
            filter_search_placeholder: "Search by first name, last name, ID, company...",
            filter_status_all: "All operational statuses",
            filter_cat_all: "All license categories",
            filter_alert_all: "All license alerts",
            filter_alert_expire: "⚠️ Expired licenses only",
            filter_alert_bientot: "⏳ Expiring in under 30 days",
            filter_alert_valide: "✅ Valid licenses (> 30 days)",
            filter_submit: "Filter",
            filter_reset: "Reset",
            spec_truck: "Assigned Truck",
            spec_company: "Company",
            spec_city: "City",
            spec_phone: "Phone",
            spec_license: "License & Validity",
            spec_visits: "Visits & Passes",
            badge_expire: "Expired",
            badge_soon_prefix: "Expires in ",
            badge_soon_suffix: " days",
            badge_valid: "Valid License",
            visits_suffix: "visit",
            visits_plural_suffix: "visits",
            btn_full_profile: "Full Profile",
            btn_edit_tooltip: "Edit Driver",
            no_driver_title: "No drivers found",
            no_driver_desc: "No driver profile matches your current search criteria or filter options.",
            btn_add_first: "Register First Driver",
            breadcrumb_back: "Back to drivers list",
            badge_portuaire: "🛡️ Active Port Badge",
            statut_btn_disponible: "Available",
            statut_btn_mission: "On Mission",
            statut_btn_aquai: "At Dock",
            statut_btn_repos: "On Rest",
            btn_edit: "Edit Profile",
            btn_add_visit: "Record Visit",
            btn_delete_title: "Delete this driver",
            panel_identity_title: "Identity & Contact Info",
            label_fullname: "Full Name",
            label_cin: "National ID / Passport",
            label_phone: "Primary Phone",
            label_emergency_phone: "Emergency Contact",
            label_email: "Email Address",
            label_residence: "Residence / City",
            label_hire_date: "Hire Date",
            not_provided: "Not provided",
            not_specified: "Not specified",
            panel_license_title: "Driving License & Compliance",
            label_license_num: "License Number",
            label_license_cat: "Category",
            label_license_issued: "Issued On",
            label_license_expiry: "Expiration Date",
            panel_truck_title: "Assigned Truck & Freight",
            label_truck_plate: "License Plate",
            no_truck_assigned: "No assigned truck",
            label_truck_model: "Model / Make",
            label_truck_type: "Type / Size",
            label_truck_capacity: "Load Capacity",
            unit_tonnes: "Tons",
            label_company: "Transport Company",
            label_remarks: "Remarks:",
            op_badge_title: "⚡ Fleet & Logistics Regulation",
            op_mission_active: "🟢 Active Mission",
            op_awaiting_assignment: "⚪ Awaiting Assignment",
            op_section_title: "Available Truck, Slot & Dock Assignment",
            op_section_desc: "CargoLink regulation rule: a driver must be assigned to an available truck and an available dock slot.",
            op_btn_release: "Release mission & Mark available",
            op_current_title: "📋 Current Assignment Status",
            op_current_truck: "Assigned Truck",
            op_no_truck: "No truck",
            op_current_availability: "Vehicle Availability",
            op_not_central_fleet: "Not attached to central fleet",
            op_current_slot: "Active Mission / Slot",
            op_awaiting_mission: "Awaiting mission",
            op_new_title: "⚡ Assign New Mission",
            op_label_truck: "Available truck",
            op_count_free: "free",
            op_select_truck: "-- Select an available truck --",
            op_label_dock: "Available Warehouse & Dock",
            op_select_dock: "-- Select an available dock --",
            op_label_slot: "Available Dock Time Slot:",
            op_select_slot_auto: "-- Auto-generate immediate time slot --",
            op_btn_submit: "Confirm Mission Assignment",
            visits_section_title: "Warehouse Visits & Checkpoints History",
            visits_section_desc: "Full traceability of loadings, unloadings and inspections performed by this driver.",
            visits_btn_add: "Add Visit",
            th_date_time: "Date & Time",
            th_dock: "Warehouse & Dock",
            th_cmr: "Bill / CMR No.",
            th_operation: "Operation",
            th_duration: "Duration",
            th_status: "Status",
            th_signoff: "Sign-off",
            site_external: "External Site",
            unit_min: "min",
            signoff_validated: "✅ Validated",
            signoff_pending: "⏳ Pending",
            no_visits_msg: "No visits or check-ins recorded yet for this driver.",
            btn_record_first_visit: "Record first visit",
            slots_section_title: "Associated Recent Time Slots & Bookings",
            slots_section_desc: "Synchronized in real-time with the Docks & Slots Regulation module.",
            btn_view_all_slots: "View all slots →",
            th_slot_ref: "Reference",
            th_slot_datetime: "Date & Slot",
            th_slot_dock: "Dock & Warehouse",
            th_action: "Action",
            btn_details: "Details",
            alert_expired_strong: "License Expired!",
            alert_expired_text: "This driver is no longer authorized to drive. Urgent renewal required.",
            alert_soon_strong: "Expiring soon ({days} days)!",
            alert_soon_text: "Please renew medical checkup and professional driver card.",
            alert_valid_strong: "License in good standing.",
            alert_valid_text: "Valid for another {days} days.",
            btn_cancel_back: "Cancel and return",
            form_subtitle: "Fill in administrative data, license categories, and the driver's assigned vehicle.",
            form_errors_title: "Errors detected:",
            sec1_title: "1. Personal & Contact Information",
            lbl_prenom: "First Name *",
            lbl_nom: "Last Name *",
            lbl_cin: "National ID / Passport",
            lbl_email: "Email Address",
            lbl_phone: "Primary Phone *",
            lbl_emergency_phone: "Emergency Phone",
            lbl_birthdate: "Date of Birth",
            lbl_hiredate: "Hire Date",
            lbl_residence: "City of Residence",
            lbl_photo: "Driver Photo",
            sec2_title: "2. Driving License & Validity",
            lbl_license_num: "License Number *",
            lbl_license_cat: "License Category *",
            lbl_license_issued: "Issue Date",
            lbl_license_expiry: "Expiration Date / Validity *",
            sec3_title: "3. Transport Company & Assigned Vehicle",
            lbl_company: "Transport / Logistics Company *",
            lbl_carrier_account: "Carrier User Account",
            lbl_truck_plate: "Truck License Plate",
            lbl_truck_model: "Make / Model",
            lbl_truck_type: "Vehicle Type / Size",
            lbl_truck_capacity: "Capacity (Tons)",
            sec4_title: "4. Operational Status & Security",
            lbl_statut: "Operational Status *",
            lbl_badge_portuaire: "Active port / secure access badge",
            lbl_remarks: "Remarks & Special Authorizations",
            btn_cancel: "Cancel",
            btn_submit_create: "Save Driver",
            btn_submit_update: "Save Changes",
            title_create: "New Driver",
            title_update_prefix: "Edit ",

            // Module Warehouses & Docks
            wh_page_title: "Warehouses & Dock Regulation",
            wh_page_sub: "Supervise storage facilities, monitor dock occupancy status, and optimize inbound logistics flows.",
            wh_btn_optimizer: "AI Optimizer",
            wh_btn_all_quais: "View All Docks",
            wh_btn_add_warehouse: "Add Warehouse",
            wh_btn_add_quai: "Add Dock",
            wh_kpi_operational: "Operational Warehouses",
            wh_kpi_active_quais: "Loading Docks",
            wh_kpi_available_quais: "Available Docks",
            wh_kpi_occupied_quais: "Occupied Docks",
            wh_kpi_total_capacity: "Total Capacity (Pallets)",
            wh_search_placeholder: "Search by name, code, city...",
            wh_filter_status_all: "All statuses",
            wh_filter_city_all: "All cities",
            wh_filter_type_all: "All dock types",
            wh_status_actif: "Operational / Active",
            wh_status_maintenance: "In maintenance",
            wh_status_ferme: "Temporarily closed",
            wh_status_disponible: "Available",
            wh_status_occupe: "Occupied / In progress",
            wh_status_reserve: "Reserved (Scheduled)",
            wh_stat_capacity: "Capacity",
            wh_stat_area: "Area",
            wh_stat_quais: "Active Docks",
            wh_stat_avail: "Availability",
            wh_btn_details: "Details & Docks →",
            wh_empty_title: "No warehouse found",
            wh_empty_desc: "No storage facility matches your current search criteria.",
            wh_btn_add_first: "Add first warehouse",
            wh_back_list: "Cancel and return",
            wh_meta_code: "Identification Code",
            wh_meta_city: "Location",
            wh_meta_manager: "Site Manager",
            wh_meta_phone: "Phone",
            wh_meta_email: "Contact Email",
            wh_meta_hours: "Opening Hours",
            wh_sec_quais_title: "Loading & Unloading Docks",
            wh_sec_quais_sub: "Real-time monitoring and dock access regulation for carriers.",
            quai_feature_leveler: "Hydraulic leveler",
            quai_feature_seal: "Dock shelter seal",
            quai_spec_flow: "Average throughput:",
            quai_spec_simultaneous: "Max trucks:",
            quai_spec_truck_type: "Size:",
            quai_btn_occupy: "Mark Occupied",
            quai_btn_release: "Free Dock",
            wh_form_sub: "Specify technical characteristics, location, and storage capacity of the warehouse.",
            quai_form_sub: "Define technical specifications, hourly throughput, and equipment of the dock.",
            wh_lbl_nom: "Warehouse Name *",
            wh_lbl_code: "Unique Identification Code *",
            wh_lbl_adresse: "Full Postal Address *",
            wh_lbl_ville: "City *",
            wh_lbl_code_postal: "Postal Code *",
            wh_lbl_telephone: "Contact Phone",
            wh_lbl_email: "Contact Email",
            wh_lbl_statut: "Operational Status",
            wh_lbl_gestionnaire: "Manager / Supervisor",
            wh_lbl_capacite: "Storage Capacity (Pallets) *",
            wh_lbl_superficie: "Area in m²",
            wh_lbl_ouverture: "Opening Time (HH:MM) *",
            wh_lbl_fermeture: "Closing Time (HH:MM) *",
            wh_lbl_jours: "Opening Days",
            quai_lbl_entrepot: "Assigned Warehouse *",
            quai_lbl_numero: "Dock Number / Identifier *",
            quai_lbl_type: "Dock Type *",
            quai_lbl_statut: "Initial Status *",
            quai_lbl_gabarit: "Accepted Truck Size",
            quai_lbl_simultaneous: "Simultaneous Trucks (1 to 5)",
            quai_lbl_flow: "Average Flow (Pallets / Hour) *",
            quai_lbl_equipments: "Technical Equipment & Safety",
            quai_lbl_remarks: "Special Instructions / Remarks",
            btn_save_warehouse: "Save Warehouse",
            btn_save_quai: "Create Dock",

            // Module Fleet & Trucks
            truck_page_title: "Fleet Management • Trucks",
            truck_page_sub: "Supervision of transport vehicles, operational availability, payloads, and predictive maintenance",
            truck_btn_add: "Add a Truck",
            truck_kpi_total: "Total Vehicles",
            truck_kpi_available: "Available / Ready",
            truck_kpi_transit: "In Transit / Route",
            truck_kpi_dock: "At Dock (In progress)",
            truck_kpi_maintenance: "Under Maintenance",
            truck_kpi_urgent_ct: "Urgent Inspections (≤15d)",
            truck_search_placeholder: "Search by license plate, make, model, carrier...",
            truck_filter_all_status: "All statuses",
            truck_filter_all_types: "All sizes",
            truck_filter_all_norms: "All emission standards",
            truck_spec_type: "Type / Size",
            truck_spec_payload: "Payload",
            truck_spec_pallets: "Pallet capacity",
            truck_spec_mileage: "Mileage",
            truck_spec_carrier_default: "Independent Carrier",
            truck_btn_view_ai: "Vehicle File • AI",
            truck_empty_title: "No truck matches your criteria",
            truck_empty_desc: "Check your search filters or register a first vehicle to start managing your fleet.",
            truck_btn_add_first: "Add a Truck",
            truck_back_list: "Back to fleet catalog",
            truck_btn_quick_status: "Change Status",
            truck_sec_specs_title: "Technical & Logistic Specifications",
            truck_spec_max_payload: "Max Payload",
            truck_spec_norm: "Emission Standard",
            truck_spec_last_ct: "Last Technical Inspection",
            truck_spec_next_ct: "Next Inspection Due Date",
            truck_ai_diag_title: "Predictive Maintenance Diagnostic (AI)",
            truck_ai_health_score: "Overall Health Score",
            truck_ai_recommendations: "Recommendations & Preventive Alerts",
            truck_sec_passages_title: "Recent Passages & Slots History",
            truck_form_back: "Back to trucks list",
            truck_form_sub: "Enter technical specifications and operational status of the vehicle.",
            truck_sec_id: "1. Identification & Size",
            truck_sec_capacities: "2. Capacities & Engine",
            truck_sec_maintenance: "3. Technical Inspection & Operations",
            truck_lbl_immat: "License Plate",
            truck_lbl_marque: "Make",
            truck_lbl_modele: "Model",
            truck_lbl_year: "Year of manufacture",
            truck_lbl_type: "Vehicle type / Size",
            truck_lbl_tonnage: "Maximum payload (Tons)",
            truck_lbl_palettes: "Pallet storage capacity",
            truck_lbl_km: "Current mileage (km)",
            truck_lbl_norm: "Environmental standard",
            truck_lbl_societe: "Transport company / Carrier",
            truck_lbl_last_ct: "Last technical inspection",
            truck_lbl_next_ct: "Next inspection due date",
            truck_lbl_etat: "Initial operational status",
            truck_lbl_notes: "Observations & Maintenance log",
            truck_btn_save: "Save Truck",
            btn_filter: "Filter",
            btn_reset: "Reset",
            btn_edit: "Edit",
            btn_delete: "Delete",

            // Toasts & feedback
            toast_lang_changed: "🌐 Language switched to English",
                    quai_btn_add_first: "Add a New Dock",
            quai_btn_manage_wh: "Manage Warehouses",
            quai_empty_desc: "No docks match the selected filter criteria.",
            quai_empty_title: "No dock found",
            quai_filter_status_all: "All dock statuses",
            quai_filter_wh_all: "All warehouses",
            quai_meta_capacity: "Processing Capacity",
            quai_meta_equipments: "Safety Equipment",
            quai_meta_gabarit: "Accepted Vehicle Sizes",
            quai_meta_notes: "Access instructions:",
            quai_meta_type: "Dock Type",
            quai_page_sub: "Overview and real-time control of all docks across the logistics network.",
            quai_page_title: "Loading Dock Regulation",
            wh_btn_add_quai_this: "Add Dock to this Warehouse",
            wh_meta_capacity: "Storage Capacity",
            wh_meta_contact: "Contact & Manager",
            wh_meta_quais: "Docks & Availability",
            truck_ai_badge: "Google Gemini AI",
            truck_ai_btn_refresh: "Refresh AI",
            truck_ai_carbon_label: "Carbon Emission Index (SDG 12):",
            truck_ai_critical_comps: "Monitored Mechanical Components",
            truck_ai_risk_lvl: "Risk Level",
            truck_ai_sub: "Mechanical reliability diagnosis and wear prediction calculated by AI.",
            truck_ai_synthesis: "VEHICLE STATUS SYNTHESIS",
            truck_ai_tip_label: "Predictive Tip:",
            truck_ai_title: "Health Score & Predictive Maintenance",
            truck_btn_add_passage: "+ Record Passage",
            truck_btn_submit_pass: "Validate Passage",
            truck_empty_passages: "No warehouse passages recorded for this vehicle yet.",
            truck_form_new_passage: "New Warehouse Passage",
            truck_lbl_pass_cmr: "Delivery Note / CMR No.",
            truck_lbl_pass_dock: "Reception Dock",
            truck_lbl_pass_notes: "Dock Observations",
            truck_lbl_pass_op: "Operation",
            truck_lbl_pass_status: "Status",
            truck_lbl_pass_weight: "Scale measured weight (kg)",
            truck_lbl_pass_wh: "Transit Warehouse",
            truck_lbl_volume: "Usable Volume (m³)",
            truck_spec_carrier: "Transport Company",
            truck_spec_last_maint: "Last Maintenance",
            truck_spec_odometer: "Odometer",
            truck_spec_pallets_euro: "Pallet Capacity",
            truck_spec_volume: "Freight Volume",
        },

        ar: {
            // Language
            lang_name: "العربية",
            lang_code: "ar",
            lang_dir: "rtl",

            // Global Navigation
            nav_warehouses: "المستودعات والأرصفة",
            nav_slots: "الجدول الزمني والمواعيد",
            nav_fleet: "الأسطول والشاحنات",
            nav_drivers: "السائقون",
            nav_login: "تسجيل الدخول",
            nav_signup: "إنشاء حساب ←",
            nav_profile: "ملفي الشخصي",
            nav_profile_sub: "تعديل البيانات الشخصية والأمان",
            nav_admin_dash: "لوحة تحكم المسؤول",
            nav_admin_dash_sub: "الوصول إلى لوحة الإدارة",
            nav_logout: "تسجيل الخروج",
            nav_logout_sub: "إنهاء الجلسة الحالية",
            nav_role_admin: "مسؤول النظام",
            nav_role_planner: "مخطط المواعيد",
            nav_role_wh_manager: "مدير المستودع",
            nav_role_carrier: "ناقل / سائق",
            nav_role_connected: "متصل",
            nav_a11y_btn: "وضع النص الكبير (إمكانية الوصول لضعاف البصر)",
            nav_theme_btn: "تبديل الوضع الفاتح / الداكن",
            nav_lang_btn: "تغيير اللغة",

            // Footer
            footer_desc: "منصة ذكية لتنسيق اللوجستيات: تنظيم أرصفة الشحن، ومزامنة الأسطول، وتحسين المواعيد في الوقت الفعلي.",
            footer_platform_title: "المنصة والخدمات",
            footer_account_title: "الحساب والوصول",
            footer_rights: "© 2026 كارجولينك للتكنولوجيا. جميع الحقوق محفوظة.",

            // Page: Slots List
            slots_page_title: "تنظيم ومواعيد أرصفة الشحن",
            slots_page_sub: "جدولة مواعيد الاستلام والشحن بالساعة، والتحقق من التوفر، وتجنب تعارض العمليات.",
            btn_planning_view: "عرض المخطط البياني",
            btn_export_csv: "تصدير CSV",
            btn_slot_request: "📋 طلب موعد",
            btn_copilot_ai: "✨ المساعد الذكي Gemini",
            btn_new_slot: "جدولة موعد جديد",

            // KPI Metrics
            kpi_total_slots: "إجمالي المواعيد المسجلة",
            kpi_today_slots: "المجدولة لليوم",
            kpi_pending_slots: "قيد انتظار الموافقة",
            kpi_at_dock_slots: "على الرصيف (عمليات جارية)",
            kpi_completed_slots: "العمليات المكتملة",

            // Filters
            filter_search_ph: "المرجع، الناقل، رقم اللوحة، السائق...",
            filter_all_wh: "جميع المستودعات",
            filter_all_status: "جميع الحالات",
            filter_all_types: "جميع العمليات",
            filter_btn: "تصفية",
            filter_reset: "إعادة تعيين",

            // Table
            th_ref_date: "المرجع والتاريخ",
            th_time_range: "الفترة الزمنية",
            th_wh_dock: "المستودع والرصيف",
            th_operation: "نوع العملية",
            th_carrier_truck: "الناقل والمركبة",
            th_driver: "السائق",
            th_status: "الحالة",
            th_actions: "الإجراء",
            tb_no_driver: "غير معين",
            tb_no_carrier: "غير معين",
            tb_quai: "رصيف",
            tb_details_btn: "التفاصيل ←",
            tb_empty_state: "لا توجد مواعيد تطابق معايير البحث الخاصة بك.",

            // Statuses
            status_en_attente: "قيد الانتظار",
            status_confirme: "مؤكد",
            status_en_cours: "على الرصيف / قيد التنفيذ",
            status_termine: "مكتمل",
            status_annule: "ملغى",
            status_retard: "متأخر",

            // Operation Types
            type_chargement: "شحن (تحميل)",
            type_dechargement: "تفريغ",
            type_mixte: "مختلط (شحن وتفريغ)",

            // Priorities
            prio_normal: "عادي",
            prio_urgent: "عاجل",
            prio_tres_urgent: "عاجل جداً",
            prio_faible: "منخفض",

            // Page: Graphical Planning
            planning_page_title: "المخطط البياني لإشغال الأرصفة",
            planning_page_sub: "جدول زمني متزامن لمراقبة إشغال الأرصفة، وتفادي الاختناقات، واكتشاف التعارضات.",
            btn_table_view: "عرض الجدول / القائمة",
            planning_site_label: "الموقع اللوجستي:",
            nav_yesterday: "◀ أمس",
            nav_tomorrow: "غداً ▶",
            nav_today: "اليوم",
            th_dock_access: "رصيف الوصول",
            badge_free: "متاح",

            // Page: Slot Form
            form_back_link: "◀ العودة إلى جدول المواعيد",
            form_create_title: "جدولة موعد جديد",
            form_edit_title: "تعديل الموعد",
            form_create_sub: "حجز رصيف شحن مع فحص التعارضات في الوقت الفعلي ومساعدة الذكاء الاصطناعي.",
            form_edit_sub: "تعديل التفاصيل التشغيلية أو التوقيتات أو مركبات النقل المعينة.",
            form_sec1_title: "🏭 1. المنشأة والجدول الزمني",
            form_sec2_title: "🚛 2. العملية والناقل",
            form_sec3_title: "🚚 3. المركبة والسائق",
            form_sec4_title: "📦 4. البضائع والتعليمات",
            lbl_target_wh: "المستودع المستهدف *",
            lbl_target_dock: "رصيف الشحن / التفريغ *",
            btn_ai_dock_opt: "✨ تحسين الرصيف (ذكاء اصطناعي)",
            lbl_dock_help: "اختر رصيفاً أو استعن بالذكاء الاصطناعي لتخصيص الرصيف الأمثل",
            lbl_op_date: "تاريخ العملية *",
            lbl_start_time: "وقت البدء *",
            lbl_end_time: "وقت الانتهاء *",
            lbl_op_type: "نوع العملية *",
            lbl_priority: "الأولوية اللوجستية *",
            lbl_carrier_co: "شركة النقل / الناقل",
            lbl_carrier_co_help: "مثال: دي إتش إل، خبير اللوجستيات...",
            lbl_truck_opt: "الشاحنة / المركبة",
            lbl_driver_opt: "السائق المعين",
            lbl_goods_type: "طبيعة البضائع",
            lbl_goods_type_help: "مثال: منصات أغذية، قطع صناعية...",
            lbl_weight: "الوزن التقديري (كغ)",
            lbl_volume: "الحجم التقديري (م³)",
            lbl_notes: "تعليمات / ملاحظات لمشغلي الرافعات",
            lbl_status_field: "حالة الموعد *",
            btn_save_slot: "حفظ الموعد",
            btn_cancel_link: "إلغاء",

            // Page: Slot Request
            demand_page_title: "طلب حجز موعد رصيف",
            demand_page_sub: "أرسل طلب حجز رصيف وصول. سيقوم مسؤول المستودع بمراجعته والموافقة عليه.",
            demand_sec_smart: "✨ التوصية الذكية بالأرصفة",
            btn_submit_demand: "إرسال طلب الموعد",

            // Page: Slot Detail
            detail_voucher_tag: "إذن المرور إلى الرصيف",
            detail_back_link: "◀ العودة لقائمة المواعيد",
            btn_print_voucher: "🖨️ طباعة إذن المرور",
            btn_edit_slot: "✏️ تعديل",
            btn_cancel_slot: "❌ إلغاء الموعد",
            btn_action_confirm: "✅ تأكيد الموعد",
            btn_action_start: "🚚 بدء العملية (على الرصيف)",
            btn_action_complete: "🏁 إنهاء العملية (مكتمل)",
            lbl_priority_label: "الأولوية:",
            detail_sec_infra: "🏭 البنية التحتية اللوجستية",
            detail_sec_transport: "🚛 النقل والمركبة",
            detail_sec_goods: "📦 البضائع وتعليمات المناولة",
            detail_sec_timeline: "⏱️ مسار وتتبع العمليات",
            detail_lbl_wh: "المستودع:",
            detail_lbl_dock: "الرصيف المعين:",
            detail_lbl_slot_time: "الفترة الزمنية:",
            detail_lbl_carrier: "الناقل:",
            detail_lbl_truck: "الشاحنة:",
            detail_lbl_driver: "السائق:",
            detail_lbl_phone: "هاتف السائق:",
            detail_lbl_weight: "الوزن التقديري:",
            detail_lbl_volume: "الحجم التقديري:",
            detail_lbl_goods_nature: "نوع الشحنة:",
            detail_lbl_instructions: "تعليمات المشغلين:",
            detail_lbl_created_by: "تم الإنشاء بواسطة:",
            detail_lbl_created_at: "تاريخ الإنشاء:",

            // Page: Cancellation Confirmation
            cancel_page_title: "تأكيد إلغاء موعد الرصيف",
            cancel_page_sub: "سيؤدي هذا الإجراء إلى إتاحة الرصيف المحجوز فوراً للناقلين الآخرين.",
            cancel_warning_box: "⚠️ هل أنت متأكد من رغبتك في إلغاء الموعد بالمرجع",
            cancel_reason_lbl: "سبب الإلغاء:",
            btn_confirm_cancel: "تأكيد الإلغاء النهائي",
            btn_back_to_slot: "لا، العودة إلى الموعد",

            // Page: Gemini AI Assistant
            ai_page_title: "مساعد الذكاء الاصطناعي Gemini • وحدة المواعيد",
            ai_badge_live: "ذكاء اصطناعي مباشر",
            ai_quick_questions_title: "💡 اقتراحات أسئلة سريعة للمخطط اللوجستي:",
            ai_q1: "ما هي المواعيد المجدولة لليوم؟",
            ai_q2: "هل توجد أي تأخيرات أو تعارضات في الأرصفة؟",
            ai_q3: "ما هي الأرصفة المتاحة حالياً؟",
            ai_q4: "كيف يمكننا تحسين جدول مواعيد الغد؟",
            ai_chat_ph: "اطرح سؤالك حول المواعيد، الأرصفة، التأخيرات أو تحسين الجدولة...",
            ai_btn_send: "إرسال",
            ai_welcome_title: "مرحباً بك! أنا مساعدك الذكي المخصص لجدولة أرصفة الشحن.",
            ai_welcome_desc: "اسألني للتحقق من التوفر، أو تدقيق التعارضات الزمنية، أو الحصول على توصيات ذكية لتخصيص الأرصفة.",
            ai_thinking: "المساعد يحلل بيانات الجدولة حالياً...",

            // وحدة السائقين والأسطول
            page_title: "إدارة السائقين",
            page_subtitle: "متابعة سائقي الشحن، ومراقبة مطابقة رخص القيادة (C, CE, ADR) وتتبع سجل العبور بمواقعكم اللوجستية.",
            btn_ai: "مساعد الذكاء الاصطناعي",
            btn_mobile: "بوابة الجوال",
            btn_export: "تصدير CSV",
            btn_add: "إضافة سائق",
            kpi_total: "إجمالي السائقين",
            kpi_total_sub: "المسجلين في الأسطول",
            kpi_dispo: "المتاحون",
            kpi_dispo_sub: "جاهزون للتعيين",
            kpi_mission: "في مهمة",
            kpi_mission_sub: "في مسار على الشبكة",
            kpi_aquai: "على الرصيف",
            kpi_aquai_sub: "بالموقع اللوجستي",
            kpi_repos: "في راحة",
            kpi_repos_sub: "غير متاحين مؤقتاً",
            kpi_alertes: "تنبيهات الرخص",
            kpi_alertes_sub: "منتهية أو للتجديد (< 30 يوم)",
            kpi_visites: "إجمالي الزيارات",
            kpi_visites_sub: "عمليات العبور بالمستودعات",
            filter_search_placeholder: "بحث بالاسم، اللقب، ب.ت.و، الشركة...",
            filter_status_all: "جميع الحالات التشغيلية",
            filter_cat_all: "جميع أصناف الرخص",
            filter_alert_all: "جميع تنبيهات الرخص",
            filter_alert_expire: "⚠️ الرخص منتهية الصلاحية فقط",
            filter_alert_bientot: "⏳ تنتهي في أقل من 30 يوماً",
            filter_alert_valide: "✅ رخص سارية (> 30 يوماً)",
            filter_submit: "تصفية",
            filter_reset: "إعادة تعيين",
            spec_truck: "الشاحنة المخصصة",
            spec_company: "الشركة",
            spec_city: "مكان الإقامة",
            spec_phone: "الهاتف",
            spec_license: "الرخصة وصلاحيتها",
            spec_visits: "الزيارات والعمليات",
            badge_expire: "منتهية",
            badge_soon_prefix: "تنتهي خلال ",
            badge_soon_suffix: " يوم",
            badge_valid: "رخصة سارية",
            visits_suffix: "زيارة",
            visits_plural_suffix: "زيارة",
            btn_full_profile: "الملف الكامل",
            btn_edit_tooltip: "تعديل بيانات السائق",
            no_driver_title: "لم يتم العثور على أي سائق",
            no_driver_desc: "لا يوجد أي ملف سائق يطابق معايير البحث أو التصفية المحددة.",
            btn_add_first: "تسجيل أول سائق",
            breadcrumb_back: "العودة إلى قائمة السائقين",
            badge_portuaire: "🛡️ شارة الميناء نشطة",
            statut_btn_disponible: "متاح",
            statut_btn_mission: "في مهمة",
            statut_btn_aquai: "على الرصيف",
            statut_btn_repos: "في راحة",
            btn_edit: "تعديل الملف",
            btn_add_visit: "تسجيل زيارة",
            btn_delete_title: "حذف هذا السائق",
            panel_identity_title: "الهوية وبيانات الاتصال",
            label_fullname: "الاسم واللقب",
            label_cin: "رقم ب.ت.و / جواز السفر",
            label_phone: "الهاتف الرئيسي",
            label_emergency_phone: "جهة اتصال الطوارئ",
            label_email: "البريد الإلكتروني",
            label_residence: "مكان الإقامة",
            label_hire_date: "تاريخ الانتداب",
            not_provided: "غير مسجل",
            not_specified: "غير محدد",
            panel_license_title: "رخصة القيادة والمطابقة",
            label_license_num: "رقم الرخصة",
            label_license_cat: "الصنف",
            label_license_issued: "تاريخ الإصدار",
            label_license_expiry: "تاريخ انتهاء الصلاحية",
            panel_truck_title: "الشاحنة المعتادة ونقل البضائع",
            label_truck_plate: "رقم اللوحة",
            no_truck_assigned: "لا توجد شاحنة مخصصة",
            label_truck_model: "الطراز / العلامة",
            label_truck_type: "الحجم / الصنف",
            label_truck_capacity: "حمولة الشاحنة",
            unit_tonnes: "أطنان",
            label_company: "الشركة الناقلة",
            label_remarks: "ملاحظات :",
            op_badge_title: "⚡ تنظيم الأسطول واللوجستيات",
            op_mission_active: "🟢 مهمة نشطة",
            op_awaiting_assignment: "⚪ في انتظار التعيين",
            op_section_title: "تعيين الشاحنة والرصيف والموعد المتاح",
            op_section_desc: "قاعدة تنظيم CargoLink: يجب تعيين السائق لشاحنة متاحة وموعد رصيف متاح.",
            op_btn_release: "إنهاء المهمة وجعله متاحاً",
            op_current_title: "📋 حالة التعيين الحالي",
            op_current_truck: "الشاحنة المعينة",
            op_no_truck: "لا توجد شاحنة",
            op_current_availability: "حالة توفر الشاحنة",
            op_not_central_fleet: "غير مرتبط بالأسطول المركزي",
            op_current_slot: "المهمة / الموعد النشط",
            op_awaiting_mission: "في انتظار مهمة",
            op_new_title: "⚡ تعيين مهمة جديدة",
            op_label_truck: "الشاحنة المتاحة",
            op_count_free: "متاح",
            op_select_truck: "-- اختر شاحنة متاحة --",
            op_label_dock: "المستودع والرصيف المتاح",
            op_select_dock: "-- اختر رصيفاً متاحاً --",
            op_label_slot: "الموعد الزمني المتاح على الرصيف :",
            op_select_slot_auto: "-- إنشاء موعد فوري تلقائياً --",
            op_btn_submit: "تأكيد تعيين المهمة",
            visits_section_title: "سجل الزيارات والعبور بالمستودعات",
            visits_section_desc: "تتبع كامل لعمليات الشحن والتفريغ والمراقبة المنجزة من قبل هذا السائق.",
            visits_btn_add: "إضافة زيارة",
            th_date_time: "التاريخ والتوقيت",
            th_dock: "المستودع والرصيف",
            th_cmr: "رقم الإذن / CMR",
            th_operation: "العملية",
            th_duration: "المدة",
            th_status: "الحالة",
            th_signoff: "التأشير",
            site_external: "موقع خارجي",
            unit_min: "دقيقة",
            signoff_validated: "✅ تم التأشير",
            signoff_pending: "⏳ في الانتظار",
            no_visits_msg: "لا توجد أي زيارات أو عبور مسجل حالياً لهذا السائق.",
            btn_record_first_visit: "تسجيل أول زيارة",
            slots_section_title: "المواعيد والحجوزات الأخيرة المرتبطة",
            slots_section_desc: "متزامن في الوقت الفعلي مع وحدة المواعيد وتنظيم الأرصفة.",
            btn_view_all_slots: "عرض جميع المواعيد ←",
            th_slot_ref: "المرجع",
            th_slot_datetime: "Date & Creneau",
            th_slot_dock: "الرصيف والمستودع",
            th_action: "الإجراء",
            btn_details: "التفاصيل",
            alert_expired_strong: "الرخصة منتهية الصلاحية!",
            alert_expired_text: "لم يعد مسموحاً لهذا السائق بالقيادة. التجديد العاجل مطلوب.",
            alert_soon_strong: "اقتراب انتهاء الصلاحية ({days} يوم)!",
            alert_soon_text: "يرجى تجديد الفحص الطبي وبطاقة السائق المهنية.",
            alert_valid_strong: "الرخصة سارية المفعول.",
            alert_valid_text: "صالحة لمدة {days} يوم إضافية.",
            btn_cancel_back: "إلغاء والعودة",
            form_subtitle: "يرجى إدخال البيانات الإدارية وأصناف رخصة القيادة والمركبة المخصصة للسائق.",
            form_errors_title: "أخطاء تم اكتشافها :",
            sec1_title: "1. البيانات الشخصية ومعلومات الاتصال",
            lbl_prenom: "الاسم *",
            lbl_nom: "اللقب *",
            lbl_cin: "رقم ب.ت.و / جواز السفر",
            lbl_email: "البريد الإلكتروني",
            lbl_phone: "الهاتف الرئيسي *",
            lbl_emergency_phone: "هاتف الطوارئ",
            lbl_birthdate: "تاريخ الولادة",
            lbl_hiredate: "تاريخ التوظيف",
            lbl_residence: "مدينة الإقامة",
            lbl_photo: "صورة السائق",
            sec2_title: "2. رخصة القيادة وصلاحيتها",
            lbl_license_num: "رقم الرخصة *",
            lbl_license_cat: "صنف الرخصة *",
            lbl_license_issued: "تاريخ الإصدار",
            lbl_license_expiry: "تاريخ انتهاء الصلاحية *",
            sec3_title: "3. شركة النقل والمركبة المرتبطة",
            lbl_company: "شركة النقل / الشحن *",
            lbl_carrier_account: "حساب مستخدم الناقل",
            lbl_truck_plate: "رقم لوحة الشاحنة",
            lbl_truck_model: "العلامة / الطراز",
            lbl_truck_type: "صنف وحجم الشاحنة",
            lbl_truck_capacity: "الحمولة (أطنان)",
            sec4_title: "4. الحالة التشغيلية والأمان",
            lbl_statut: "الحالة التشغيلية *",
            lbl_badge_portuaire: "شارة العبور المينائي / المؤمن نشطة",
            lbl_remarks: "ملاحظات وتراخيص خاصة",
            btn_cancel: "إلغاء",
            btn_submit_create: "حفظ بيانات السائق",
            btn_submit_update: "حفظ التعديلات",
            title_create: "سائق جديد",
            title_update_prefix: "تعديل ملف ",

            // Module Entrepôts & Quais
            wh_page_title: "المستودعات وتنظيم الأرصفة",
            wh_page_sub: "إشراف كامل على منشآت التخزين ومراقبة إشغال الأرصفة وتحسين تدفق الشاحنات الواردة.",
            wh_btn_optimizer: "مُحسِّن الذكاء الاصطناعي",
            wh_btn_all_quais: "عرض جميع الأرصفة",
            wh_btn_add_warehouse: "إضافة مستودع",
            wh_btn_add_quai: "إضافة رصيف",
            wh_kpi_operational: "المستودعات التشغيلية",
            wh_kpi_active_quais: "أرصفة الشحن",
            wh_kpi_available_quais: "الأرصفة المتاحة",
            wh_kpi_occupied_quais: "الأرصفة المشغولة",
            wh_kpi_total_capacity: "السعة الإجمالية (منصات)",
            wh_search_placeholder: "البحث بالاسم، الرمز، المدينة...",
            wh_filter_status_all: "جميع الحالات",
            wh_filter_city_all: "جميع المدن",
            wh_filter_type_all: "جميع أنواع الأرصفة",
            wh_status_actif: "تشغيلي / نشط",
            wh_status_maintenance: "في الصيانة",
            wh_status_ferme: "مغلق مؤقتاً",
            wh_status_disponible: "متاح",
            wh_status_occupe: "مشغول / قيد العمل",
            wh_status_reserve: "محجوز (مجدول)",
            wh_stat_capacity: "السعة",
            wh_stat_area: "المساحة",
            wh_stat_quais: "الأرصفة النشطة",
            wh_stat_avail: "التوفر",
            wh_btn_details: "التفاصيل والأرصفة ←",
            wh_empty_title: "لم يتم العثور على أي مستودع",
            wh_empty_desc: "لا توجد منشأة تخزين تطابق معايير البحث المحددة حالياً.",
            wh_btn_add_first: "إضافة أول مستودع",
            wh_back_list: "إلغاء والعودة",
            wh_meta_code: "رمز التعريف",
            wh_meta_city: "الموقع الجغرافي",
            wh_meta_manager: "مسؤول الموقع",
            wh_meta_phone: "رقم الهاتف",
            wh_meta_email: "البريد الإلكتروني",
            wh_meta_hours: "أوقات العمل",
            wh_sec_quais_title: "أرصفة الشحن والتفريغ",
            wh_sec_quais_sub: "مراقبة فورية وتنظيم وصول شاحنات الناقلين للأرصفة.",
            quai_feature_leveler: "مسوِّي هيدروليكي",
            quai_feature_seal: "ستار عازل للحرارة",
            quai_spec_flow: "معدل التدفق :",
            quai_spec_simultaneous: "أقصى شاحنات :",
            quai_spec_truck_type: "الصنف :",
            quai_btn_occupy: "تحديد كمشغول",
            quai_btn_release: "تحرير الرصيف",
            wh_form_sub: "أدخل المواصفات التقنية والموقع الجغرافي وسعة التخزين للمستودع.",
            quai_form_sub: "حدد المواصفات الفنية للرصيف وطاقة التدفق بالساعة والتجهيزات المتوفرة.",
            wh_lbl_nom: "اسم المستودع *",
            wh_lbl_code: "رمز التعريف الفريد *",
            wh_lbl_adresse: "العنوان البريدي الكامل *",
            wh_lbl_ville: "المدينة *",
            wh_lbl_code_postal: "الرمز البريدي *",
            wh_lbl_telephone: "رقم هاتف الاتصال",
            wh_lbl_email: "البريد الإلكتروني للاتصال",
            wh_lbl_statut: "الحالة التشغيلية",
            wh_lbl_gestionnaire: "المسؤول / المدير",
            wh_lbl_capacite: "سعة التخزين (منصات) *",
            wh_lbl_superficie: "المساحة بالمتر المربع",
            wh_lbl_ouverture: "ساعة الفتح (تنسيق HH:MM) *",
            wh_lbl_fermeture: "ساعة الإغلاق (تنسيق HH:MM) *",
            wh_lbl_jours: "أيام العمل",
            quai_lbl_entrepot: "المستودع المرتبط *",
            quai_lbl_numero: "رقم / معرّف الرصيف *",
            quai_lbl_type: "صنف الرصيف *",
            quai_lbl_statut: "الحالة الأولية *",
            quai_lbl_gabarit: "حجم الشاحنات المقبول",
            quai_lbl_simultaneous: "الشاحنات المتزامنة (1 إلى 5)",
            quai_lbl_flow: "معدل التفريغ (منصات / ساعة) *",
            quai_lbl_equipments: "التجهيزات الفنية والسلامة",
            quai_lbl_remarks: "تعليمات خاصة / ملاحظات",
            btn_save_warehouse: "حفظ بيانات المستودع",
            btn_save_quai: "إنشاء الرصيف",

            // Module Flotte & Camions
            truck_page_title: "إدارة الأسطول والشاحنات",
            truck_page_sub: "مراقبة مركبات النقل والجاهزية التشغيلية والحمولات والصيانة التنبؤية بالذكاء الاصطناعي",
            truck_btn_add: "إضافة شاحنة جديدة",
            truck_kpi_total: "إجمالي المركبات",
            truck_kpi_available: "متاحة / جاهزة",
            truck_kpi_transit: "في الطريق / عبور",
            truck_kpi_dock: "على الرصيف (قيد العمل)",
            truck_kpi_maintenance: "في الصيانة",
            truck_kpi_urgent_ct: "فحص فني عاجل (≤15 يوم)",
            truck_search_placeholder: "البحث برقم اللوحة، الماركة، الطراز، الناقل...",
            truck_filter_all_status: "جميع الحالات التشغيلية",
            truck_filter_all_types: "جميع الأحجام والأصناف",
            truck_filter_all_norms: "جميع المعايير البيئية",
            truck_spec_type: "الصنف / الحجم",
            truck_spec_payload: "الحمولة الصافية",
            truck_spec_pallets: "سعة المنصات",
            truck_spec_mileage: "المسافة المقطوعة",
            truck_spec_carrier_default: "ناقل مستقل",
            truck_btn_view_ai: "ملف الشاحنة • الذكاء الاصطناعي",
            truck_empty_title: "لا توجد أي شاحنة تطابق معاييرك",
            truck_empty_desc: "تحقق من فلاتر البحث أو أضف أول مركبة للبدء في إدارة أسطولك.",
            truck_btn_add_first: "إضافة شاحنة جديدة",
            truck_back_list: "العودة لكتالوج الأسطول",
            truck_btn_quick_status: "تحديث الحالة",
            truck_sec_specs_title: "المواصفات الفنية واللوجستية",
            truck_spec_max_payload: "أقصى حمولة نافعة",
            truck_spec_norm: "المعيار البيئي للانبعاثات",
            truck_spec_last_ct: "تاريخ آخر فحص فني",
            truck_spec_next_ct: "تاريخ الفحص الفني القادم",
            truck_ai_diag_title: "تشخيص الصيانة التنبؤية (الذكاء الاصطناعي)",
            truck_ai_health_score: "مؤشر السلامة العام",
            truck_ai_recommendations: "التوصيات والتنبيهات الوقائية",
            truck_sec_passages_title: "سجل العبور والمواعيد السابقة",
            truck_form_back: "العودة لقائمة الشاحنات",
            truck_form_sub: "أدخل المواصفات التقنية والحالة التشغيلية للمركبة.",
            truck_sec_id: "1. بيانات التعريف والصنف",
            truck_sec_capacities: "2. السعات والمحرك",
            truck_sec_maintenance: "3. الفحص الفني والتشغيل",
            truck_lbl_immat: "رقم اللوحة",
            truck_lbl_marque: "العلامة التجارية",
            truck_lbl_modele: "الطراز",
            truck_lbl_year: "سنة الصنع والتسجيل",
            truck_lbl_type: "صنف ونوع المركبة",
            truck_lbl_tonnage: "الحمولة القصوى (بالأطنان)",
            truck_lbl_palettes: "سعة التخزين (بالمنصات)",
            truck_lbl_km: "المسافة المقطوعة (كم)",
            truck_lbl_norm: "المعيار البيئي",
            truck_lbl_societe: "شركة النقل / الشحن",
            truck_lbl_last_ct: "تاريخ آخر فحص فني",
            truck_lbl_next_ct: "تاريخ الفحص الفني القادم",
            truck_lbl_etat: "الحالة التشغيلية الأولية",
            truck_lbl_notes: "ملاحظات وسجل الصيانة",
            truck_btn_save: "حفظ بيانات الشاحنة",
            btn_filter: "تصفية",
            btn_reset: "إعادة تعيين",
            btn_edit: "تعديل",
            btn_delete: "حذف",

            // Toasts & feedback
            toast_lang_changed: "🌐 تم تغيير لغة الواجهة إلى العربية",
            quai_btn_add_first: "إضافة رصيف جديد",
            quai_btn_manage_wh: "إدارة المستودعات",
            quai_empty_desc: "لا يوجد أي رصيف يطابق معايير التصفية المحددة.",
            quai_empty_title: "لم يتم العثور على أي رصيف",
            quai_filter_status_all: "جميع حالات الأرصفة",
            quai_filter_wh_all: "جميع المستودعات",
            quai_meta_capacity: "سعة المعالجة",
            quai_meta_equipments: "تجهيزات السلامة",
            quai_meta_gabarit: "أصناف المركبات المقبولة",
            quai_meta_notes: "تعليمات الدخول:",
            quai_meta_type: "نوع الرصيف",
            quai_page_sub: "نظرة شاملة وتحكم في الوقت الفعلي لجميع أرصفة الشبكة اللوجستية.",
            quai_page_title: "تنظيم أرصفة الشحن والتفريغ",
            wh_btn_add_quai_this: "إضافة رصيف لهذا المستودع",
            wh_meta_capacity: "سعة التخزين",
            wh_meta_contact: "جهة الاتصال والمسؤول",
            wh_meta_quais: "الأرصفة والتوفر",
            truck_ai_badge: "الذكاء الاصطناعي Google Gemini",
            truck_ai_btn_refresh: "تحديث الذكاء الاصطناعي",
            truck_ai_carbon_label: "مؤشر انبعاثات الكربون (الهدف 12):",
            truck_ai_critical_comps: "المكونات الميكانيكية المراقبة",
            truck_ai_risk_lvl: "مستوى الخطر",
            truck_ai_sub: "تشخيص الموثوقية الميكانيكية وتنبؤ التآكل بواسطة الذكاء الاصطناعي.",
            truck_ai_synthesis: "ملخص حالة المركبة",
            truck_ai_tip_label: "نصيحة تنبؤية:",
            truck_ai_title: "مؤشر السلامة والصيانة التنبؤية",
            truck_btn_add_passage: "+ تسجيل عبور",
            truck_btn_submit_pass: "تأكيد تسجيل العبور",
            truck_empty_passages: "لم يتم تسجيل أي عبور بالمستودع لهذه الشاحنة حتى الآن.",
            truck_form_new_passage: "تسجيل عبور جديد للمستودع",
            truck_lbl_pass_cmr: "رقم وصل التسليم / CMR",
            truck_lbl_pass_dock: "رصيف الاستقبال",
            truck_lbl_pass_notes: "ملاحظات الرصيف",
            truck_lbl_pass_op: "نوع العملية",
            truck_lbl_pass_status: "الحالة",
            truck_lbl_pass_weight: "الوزن المقاس بميزان الجسر (كغ)",
            truck_lbl_pass_wh: "مستودع العبور",
            truck_lbl_volume: "الحجم المفيد (م³)",
            truck_spec_carrier: "شركة النقل",
            truck_spec_last_maint: "آخر صيانة",
            truck_spec_odometer: "عداد الكيلومترات",
            truck_spec_pallets_euro: "سعة المنصات",
            truck_spec_volume: "حجم الشحن"
        }
    };

    // Table of direct text phrases for elements without data-i18n attributes
    const DIRECT_PHRASES = [
        {
            fr: "Entrepôts & Régulation des Quais",
            en: "Warehouses & Dock Regulation",
            ar: "المستودعات وتنظيم الأرصفة"
        },
        {
            fr: "Gestion de la Flotte • Camions",
            en: "Fleet Management • Trucks",
            ar: "إدارة الأسطول والشاحنات"
        },
        {
            fr: "Ajouter un Camion",
            en: "Add a Truck",
            ar: "إضافة شاحنة"
        },
        {
            fr: "Ajouter un Entrepôt",
            en: "Add Warehouse",
            ar: "إضافة مستودع"
        },
        {
            fr: "Nouveau Quai",
            en: "New Dock",
            ar: "رصيف جديد"
        },
        {
            fr: "Total Véhicules",
            en: "Total Vehicles",
            ar: "إجمالي المركبات"
        },
        {
            fr: "Disponibles / Prêts",
            en: "Available / Ready",
            ar: "متاحة / جاهزة"
        },
        {
            fr: "En Transit / Route",
            en: "In Transit / Route",
            ar: "في الطريق / عبور"
        },
        {
            fr: "À Quai (En cours)",
            en: "At Dock (In progress)",
            ar: "على الرصيف (قيد العمل)"
        },
        {
            fr: "En Maintenance",
            en: "Under Maintenance",
            ar: "في الصيانة"
        },
        {
            fr: "Contrôles Urgents (≤15j)",
            en: "Urgent Inspections (≤15d)",
            ar: "فحص فني عاجل (≤15 يوم)"
        },
        {
            fr: "Entrepôts Opérationnels",
            en: "Operational Warehouses",
            ar: "المستودعات التشغيلية"
        },
        {
            fr: "Quais de Chargement",
            en: "Loading Docks",
            ar: "أرصفة الشحن"
        },
        {
            fr: "Quais Disponibles",
            en: "Available Docks",
            ar: "الأرصفة المتاحة"
        },
        {
            fr: "Quais Occupés",
            en: "Occupied Docks",
            ar: "الأرصفة المشغولة"
        },
        {
            fr: "Capacité Totale (Palettes)",
            en: "Total Capacity (Pallets)",
            ar: "السعة الإجمالية (منصات)"
        },
        {
            fr: "Tous les états",
            en: "All statuses",
            ar: "جميع الحالات"
        },
        {
            fr: "Tous les gabarits",
            en: "All sizes",
            ar: "جميع الأصناف"
        },
        {
            fr: "Toutes les normes",
            en: "All emission standards",
            ar: "جميع المعايير"
        },
        {
            fr: "Type / Gabarit",
            en: "Type / Size",
            ar: "الصنف / الحجم"
        },
        {
            fr: "Charge Utile",
            en: "Payload",
            ar: "الحمولة الصافية"
        },
        {
            fr: "Capacité palettes",
            en: "Pallet capacity",
            ar: "سعة المنصات"
        },
        {
            fr: "Kilométrage",
            en: "Mileage",
            ar: "المسافة المقطوعة"
        },
        {
            fr: "Fiche Véhicule • IA",
            en: "Vehicle File • AI",
            ar: "ملف الشاحنة • الذكاء الاصطناعي"
        },
        {
            fr: "Modifier État",
            en: "Update Status",
            ar: "تحديث الحالة"
        },
        {
            fr: "Caractéristiques Techniques & Logistiques",
            en: "Technical & Logistic Specifications",
            ar: "المواصفات الفنية واللوجستية"
        },
        {
            fr: "Charge Utile Max",
            en: "Max Payload",
            ar: "أقصى حمولة نافعة"
        },
        {
            fr: "Norme Antipollution",
            en: "Emission Standard",
            ar: "معيار الانبعاثات"
        },
        {
            fr: "Dernier Contrôle Technique",
            en: "Last Technical Inspection",
            ar: "آخر فحص فني"
        },
        {
            fr: "Prochain Contrôle Exigé",
            en: "Next Due Inspection",
            ar: "الفحص الفني القادم"
        },
        {
            fr: "Diagnostic de Maintenance Prédictive (IA)",
            en: "Predictive Maintenance Diagnostic (AI)",
            ar: "تشخيص الصيانة التنبؤية (الذكاء الاصطناعي)"
        },
        {
            fr: "Indice de Santé Global",
            en: "Overall Health Score",
            ar: "مؤشر السلامة العام"
        },
        {
            fr: "Recommandations & Alertes Préventives",
            en: "Recommendations & Preventive Alerts",
            ar: "التوصيات والتنبيهات الوقائية"
        },
        {
            fr: "Historique Récent des Passages & Créneaux",
            en: "Recent Passages & Slots History",
            ar: "سجل العبور والمواعيد السابقة"
        },
        {
            fr: "Régulation & Créneaux des Quais",
            en: "Dock Regulation & Time Slots",
            ar: "تنظيم ومواعيد أرصفة الشحن"
        },
        {
            fr: "Planification horaire des réceptions et expéditions, vérification des disponibilités et prévention des conflits.",
            en: "Hourly scheduling for arrivals and departures, checking availability, and preventing conflicts.",
            ar: "جدولة مواعيد الاستلام والشحن والتحقق من التوفر ومنع التعارض."
        },
        {
            fr: "Vue Planning Graphique",
            en: "Visual Timeline View",
            ar: "عرض المخطط البياني"
        },
        {
            fr: "Vue Tableau / Liste",
            en: "Table / List View",
            ar: "عرض الجدول / القائمة"
        },
        {
            fr: "Planning Graphique d'Occupation des Quais",
            en: "Visual Dock Occupancy Schedule",
            ar: "المخطط البياني لإشغال الأرصفة"
        },
        {
            fr: "Vue temporelle synchronisée pour superviser l'occupation des quais, éviter les goulots d'étranglement et détecter les conflits.",
            en: "Synchronized timeline to monitor dock occupancy, prevent bottlenecks and detect conflicts.",
            ar: "جدول زمني متزامن لمراقبة إشغال الأرصفة وتجنب الاختناقات واكتشاف التعارضات."
        },
        {
            fr: "Demande de Créneau",
            en: "Slot Request",
            ar: "طلب موعد"
        },
        {
            fr: "Copilot IA Gemini",
            en: "Gemini AI Copilot",
            ar: "المساعد الذكي Gemini"
        },
        {
            fr: "Planifier un Créneau",
            en: "Schedule a Slot",
            ar: "جدولة موعد جديد"
        },
        {
            fr: "Total Créneaux Enregistrés",
            en: "Total Registered Slots",
            ar: "إجمالي المواعيد المسجلة"
        },
        {
            fr: "Prévus Aujourd'hui",
            en: "Scheduled Today",
            ar: "المجدولة اليوم"
        },
        {
            fr: "En Attente de Validation",
            en: "Pending Approval",
            ar: "قيد انتظار الموافقة"
        },
        {
            fr: "À Quai (Opérations en cours)",
            en: "At Dock (Ongoing Operations)",
            ar: "على الرصيف (عمليات جارية)"
        },
        {
            fr: "Opérations Terminées",
            en: "Completed Operations",
            ar: "العمليات المكتملة"
        },
        {
            fr: "Tous les entrepôts",
            en: "All warehouses",
            ar: "جميع المستودعات"
        },
        {
            fr: "Tous les statuts",
            en: "All statuses",
            ar: "جميع الحالات"
        },
        {
            fr: "Tous types",
            en: "All types",
            ar: "جميع العمليات"
        },
        {
            fr: "Filtrer",
            en: "Filter",
            ar: "تصفية"
        },
        {
            fr: "Réinitialiser",
            en: "Reset",
            ar: "إعادة تعيين"
        },
        {
            fr: "Référence & Date",
            en: "Reference & Date",
            ar: "المرجع والتاريخ"
        },
        {
            fr: "Plage Horaire",
            en: "Time Range",
            ar: "الفترة الزمنية"
        },
        {
            fr: "Entrepôt & Quai",
            en: "Warehouse & Dock",
            ar: "المستودع والرصيف"
        },
        {
            fr: "Opération",
            en: "Operation",
            ar: "نوع العملية"
        },
        {
            fr: "Transporteur & Véhicule",
            en: "Carrier & Vehicle",
            ar: "الناقل والمركبة"
        },
        {
            fr: "Chauffeur",
            en: "Driver",
            ar: "السائق"
        },
        {
            fr: "Statut",
            en: "Status",
            ar: "الحالة"
        },
        {
            fr: "Action",
            en: "Action",
            ar: "الإجراء"
        },
        {
            fr: "Non assigné",
            en: "Unassigned",
            ar: "غير معين"
        },
        {
            fr: "En attente",
            en: "Pending",
            ar: "قيد الانتظار"
        },
        {
            fr: "Confirmé",
            en: "Confirmed",
            ar: "مؤكد"
        },
        {
            fr: "À quai",
            en: "At dock",
            ar: "على الرصيف"
        },
        {
            fr: "En cours",
            en: "In progress",
            ar: "قيد التنفيذ"
        },
        {
            fr: "Terminé",
            en: "Completed",
            ar: "مكتمل"
        },
        {
            fr: "Annulé",
            en: "Cancelled",
            ar: "ملغى"
        },
        {
            fr: "En retard",
            en: "Delayed",
            ar: "متأخر"
        },
        {
            fr: "Chargement",
            en: "Loading",
            ar: "تحميل"
        },
        {
            fr: "Déchargement",
            en: "Unloading",
            ar: "تفريغ"
        },
        {
            fr: "Mixte",
            en: "Mixed",
            ar: "مختلط"
        },
        {
            fr: "Hier",
            en: "Yesterday",
            ar: "أمس"
        },
        {
            fr: "Demain",
            en: "Tomorrow",
            ar: "غداً"
        },
        {
            fr: "Aujourd'hui",
            en: "Today",
            ar: "اليوم"
        },
        {
            fr: "Site Logistique :",
            en: "Logistics Site:",
            ar: "الموقع اللوجستي:"
        },
        {
            fr: "QUAI D'ACCÈS",
            en: "ACCESS DOCK",
            ar: "رصيف الوصول"
        },
        {
            fr: "Imprimer Bon de Passage",
            en: "Print Pass Voucher",
            ar: "طباعة إذن المرور"
        },
        {
            fr: "Modifier",
            en: "Edit",
            ar: "تعديل"
        },
        {
            fr: "Annuler ce créneau",
            en: "Cancel this slot",
            ar: "إلغاء هذا الموعد"
        },
        {
            fr: "Bon de passage à quai",
            en: "Dock Pass Voucher",
            ar: "إذن المرور إلى الرصيف"
        },
        {
            fr: "Retour à la liste des créneaux",
            en: "Back to slots list",
            ar: "العودة لقائمة المواعيد"
        },
        {
            fr: "Retour au planning des créneaux",
            en: "Back to slots schedule",
            ar: "العودة إلى جدول المواعيد"
        },
        {
            fr: "Enregistrer le créneau",
            en: "Save time slot",
            ar: "حفظ الموعد"
        },
        {
            fr: "Optimisation Quai (IA)",
            en: "Dock Optimization (AI)",
            ar: "تحسين الرصيف (ذكاء اصطناعي)"
        },
        {
            fr: "Priorité :",
            en: "Priority:",
            ar: "الأولوية:"
        },
        {
            fr: "Normal",
            en: "Normal",
            ar: "عادي"
        },
        {
            fr: "Urgent",
            en: "Urgent",
            ar: "عاجل"
        },
        {
            fr: "Très Urgent",
            en: "High Urgent",
            ar: "عاجل جداً"
        },
        {
            fr: "Faible",
            en: "Low",
            ar: "منخفض"
        },
        {
            fr: "Entrepôt cible *",
            en: "Target Warehouse *",
            ar: "المستودع المستهدف *"
        },
        {
            fr: "Date d'opération *",
            en: "Operation Date *",
            ar: "تاريخ العملية *"
        },
        {
            fr: "Heure de début *",
            en: "Start Time *",
            ar: "وقت البدء *"
        },
        {
            fr: "Heure de fin *",
            en: "End Time *",
            ar: "وقت الانتهاء *"
        },
        {
            fr: "Type d'opération *",
            en: "Operation Type *",
            ar: "نوع العملية *"
        },
        {
            fr: "Priorité logistique *",
            en: "Logistics Priority *",
            ar: "الأولوية اللوجستية *"
        },
        {
            fr: "Société de transport",
            en: "Transport Company",
            ar: "شركة النقل"
        },
        {
            fr: "Camion / Véhicule",
            en: "Truck / Vehicle",
            ar: "الشاحنة / المركبة"
        },
        {
            fr: "Chauffeur assigné",
            en: "Assigned Driver",
            ar: "السائق المعين"
        },
        {
            fr: "Poids estimé (kg)",
            en: "Estimated Weight (kg)",
            ar: "الوزن التقديري (كغ)"
        },
        {
            fr: "Volume estimé (m³)",
            en: "Estimated Volume (m³)",
            ar: "الحجم التقديري (م³)"
        },
        {
            fr: "Instructions / Remarques",
            en: "Instructions / Notes",
            ar: "التعليمات / الملاحظات"
        },
        {
            fr: "Statut du créneau",
            en: "Slot Status",
            ar: "حالة الموعد"
        },
        {
            fr: "Planning & Créneaux",
            en: "Schedule & Slots",
            ar: "الجدول الزمني والمواعيد"
        },
        {
            fr: "Entrepôts & Quais",
            en: "Warehouses & Docks",
            ar: "المستودعات والأرصفة"
        },
        {
            fr: "Flotte & Camions",
            en: "Fleet & Trucks",
            ar: "الأسطول والشاحنات"
        },
        {
            fr: "Chauffeurs",
            en: "Drivers",
            ar: "السائقون"
        },
        {
            fr: "Mon Profil",
            en: "My Profile",
            ar: "ملفي الشخصي"
        },
        {
            fr: "Se Déconnecter",
            en: "Log Out",
            ar: "تسجيل الخروج"
        },
        {
            fr: "Connexion",
            en: "Login",
            ar: "تسجيل الدخول"
        },
        {
            fr: "Créer un compte",
            en: "Create Account",
            ar: "إنشاء حساب"
        },
        {
            fr: "Planificateur de Créneaux",
            en: "Slot Planner",
            ar: "مخطط المواعيد"
        },
        {
            fr: "Gestionnaire d'Entrepôt",
            en: "Warehouse Manager",
            ar: "مدير المستودع"
        },
        {
            fr: "Administrateur",
            en: "Administrator",
            ar: "مسؤول النظام"
        }
    ];

    const CargoLinkI18n = {
        currentLang: 'fr',

        init: function () {
            const savedLang = localStorage.getItem('cargolink_lang') || 'fr';
            this.setLanguage(savedLang, false);
            this.setupUI();
        },

        getTranslations: function (lang) {
            return TRANSLATIONS[lang] || TRANSLATIONS.fr;
        },

        t: function (key, lang) {
            const targetLang = lang || this.currentLang;
            const dict = this.getTranslations(targetLang);
            return dict[key] || TRANSLATIONS.fr[key] || key;
        },

        setLanguage: function (lang, showToast = true) {
            if (!['fr', 'en', 'ar'].includes(lang)) {
                lang = 'fr';
            }
            this.currentLang = lang;
            localStorage.setItem('cargolink_lang', lang);

            // Attributs du document
            document.documentElement.setAttribute('data-lang', lang);
            document.documentElement.setAttribute('lang', lang);
            const isRTL = lang === 'ar';
            document.documentElement.setAttribute('dir', isRTL ? 'rtl' : 'ltr');

            // Traduction DOM
            this.translateDOM(lang);

            // Mise à jour de l'UI du sélecteur
            this.updateSwitcherUI(lang);

            // Notification Toast
            if (showToast && window.__cargoLinkShowToast) {
                const toastMsg = this.t('toast_lang_changed', lang);
                window.__cargoLinkShowToast(toastMsg);
            }

            // Déclencher événement personnalisé
            window.dispatchEvent(new CustomEvent('cargolink:languageChanged', {
                detail: { lang: lang, isRTL: isRTL }
            }));
        },

        translateDOM: function (lang) {
            const dict = this.getTranslations(lang);

            // 1. Éléments avec attribut data-i18n
            document.querySelectorAll('[data-i18n]').forEach(el => {
                const key = el.getAttribute('data-i18n');
                if (dict[key]) {
                    el.textContent = dict[key];
                }
            });

            // 2. Attributs placeholder
            document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
                const key = el.getAttribute('data-i18n-placeholder');
                if (dict[key]) {
                    el.setAttribute('placeholder', dict[key]);
                }
            });

            // 3. Attributs title
            document.querySelectorAll('[data-i18n-title]').forEach(el => {
                const key = el.getAttribute('data-i18n-title');
                if (dict[key]) {
                    el.setAttribute('title', dict[key]);
                }
            });

            // 4. Attributs aria-label
            document.querySelectorAll('[data-i18n-aria]').forEach(el => {
                const key = el.getAttribute('data-i18n-aria');
                if (dict[key]) {
                    el.setAttribute('aria-label', dict[key]);
                }
            });

            // 5. Remplacement des expressions directes (tables, filtres, options)
            this.translateDirectPhrases(lang);

            // 6. Traduction dynamique des modules
            this.translateChauffeurs(lang);
            this.translateEntrepots(lang);
            this.translateCamions(lang);
        },

        translateChauffeurs: function (lang) {
            const dict = this.getTranslations(lang);
            const isRTL = lang === 'ar';

            // 1. Conteneurs avec direction RTL / LTR
            document.querySelectorAll('.chauffeurs-container, .chauffeur-form-container').forEach(c => {
                c.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
            });

            // 2. Flèches de retour
            const breadcrumbArrow = document.getElementById('breadcrumbBackArrow');
            if (breadcrumbArrow) {
                breadcrumbArrow.innerHTML = isRTL ? '&rarr;' : '&larr;';
            }
            const formArrow = document.getElementById('formBackArrow');
            if (formArrow) {
                formArrow.innerHTML = isRTL ? '&rarr;' : '&larr;';
            }

            // 3. Mappages des libellés dynamiques
            const STATUS_MAP = {
                DISPONIBLE: { fr: "Disponible", en: "Available", ar: "متاح" },
                EN_MISSION: { fr: "En mission", en: "On mission", ar: "في مهمة" },
                A_QUAI: { fr: "À quai", en: "At dock", ar: "على الرصيف" },
                EN_REPOS: { fr: "En repos", en: "On rest", ar: "في راحة" },
                INACTIF: { fr: "Inactif", en: "Inactive", ar: "غير نشط" }
            };

            const CAMION_MAP = {
                DISPONIBLE: { fr: "Disponible", en: "Available", ar: "متاح" },
                EN_MISSION: { fr: "En mission", en: "On mission", ar: "في مهمة" },
                EN_MAINTENANCE: { fr: "En maintenance", en: "In maintenance", ar: "في الصيانة" },
                HORS_SERVICE: { fr: "Hors service", en: "Out of service", ar: "خارج الخدمة" }
            };

            const OP_MAP = {
                DECHARGEMENT: { fr: "Déchargement", en: "Unloading", ar: "تفريغ" },
                CHARGEMENT: { fr: "Chargement", en: "Loading", ar: "شحن" },
                CONTROLE: { fr: "Contrôle / Transit", en: "Inspection / Transit", ar: "مراقبة / عبور" },
                LIVRAISON: { fr: "Livraison", en: "Delivery", ar: "تسليم" }
            };

            const VISITE_STATUS_MAP = {
                EN_ATTENTE: { fr: "En attente", en: "Pending", ar: "في الانتظار" },
                A_QUAI: { fr: "À quai", en: "At dock", ar: "على الرصيف" },
                EN_COURS: { fr: "En cours", en: "In progress", ar: "قيد الإنجاز" },
                TERMINE: { fr: "Terminé", en: "Completed", ar: "مكتمل" },
                ANNULE: { fr: "Annulé", en: "Cancelled", ar: "ملغى" }
            };

            const CRENEAU_STATUS_MAP = {
                DEMANDE: { fr: "Demandé", en: "Requested", ar: "مطلوب" },
                CONFIRME: { fr: "Confirmé", en: "Confirmed", ar: "مؤكد" },
                EN_COURS: { fr: "En cours", en: "In progress", ar: "قيد الإنجاز" },
                TERMINE: { fr: "Terminé", en: "Completed", ar: "مكتمل" },
                ANNULE: { fr: "Annulé", en: "Cancelled", ar: "ملغى" }
            };

            const LIC_CAT_MAP = {
                C: { fr: "Permis C (Poids lourd > 3.5t)", en: "Class C (Heavy truck > 3.5t)", ar: "صنف C (وزن ثقيل > 3.5 طن)" },
                CE: { fr: "Permis CE (Poids lourd avec remorque)", en: "Class CE (Heavy truck with trailer)", ar: "صنف CE (شاحنة مقطورة)" },
                C1: { fr: "Permis C1 (Poids lourd intermédiaire)", en: "Class C1 (Intermediate heavy truck)", ar: "صنف C1 (وزن ثقيل متوسط)" },
                C1E: { fr: "Permis C1E (Intermédiaire avec remorque)", en: "Class C1E (Intermediate with trailer)", ar: "صنف C1E (متوسط بمقطورة)" },
                D: { fr: "Permis D (Transport en commun)", en: "Class D (Passenger transport)", ar: "صنف D (نقل جماعي)" },
                ADR: { fr: "Certificat ADR (Matières Dangereuses)", en: "ADR Certificate (Hazardous materials)", ar: "شهادة ADR (مواد خطرة)" }
            };

            // Badges statut chauffeur
            document.querySelectorAll('[data-status-badge]').forEach(badge => {
                const code = badge.getAttribute('data-status-badge');
                const labelSpan = badge.querySelector('.status-badge-text');
                if (labelSpan && STATUS_MAP[code] && STATUS_MAP[code][lang]) {
                    labelSpan.textContent = STATUS_MAP[code][lang];
                }
            });

            // Options de filtrage par statut
            document.querySelectorAll('#selectStatut option[data-status-opt]').forEach(opt => {
                const code = opt.getAttribute('data-status-opt');
                if (STATUS_MAP[code] && STATUS_MAP[code][lang]) {
                    opt.textContent = STATUS_MAP[code][lang];
                }
            });

            // Options formulaires statut
            document.querySelectorAll('select[name="statut"] option').forEach(opt => {
                const code = opt.value;
                if (STATUS_MAP[code] && STATUS_MAP[code][lang]) {
                    opt.textContent = STATUS_MAP[code][lang];
                }
            });

            // Options catégories permis
            document.querySelectorAll('select[name="categorie_permis"] option').forEach(opt => {
                const code = opt.value;
                if (LIC_CAT_MAP[code] && LIC_CAT_MAP[code][lang]) {
                    opt.textContent = LIC_CAT_MAP[code][lang];
                }
            });

            // Statut camion associé
            document.querySelectorAll('[data-camion-status]').forEach(badge => {
                const code = badge.getAttribute('data-camion-status');
                const labelSpan = badge.querySelector('.status-badge-text');
                if (labelSpan && CAMION_MAP[code] && CAMION_MAP[code][lang]) {
                    labelSpan.textContent = CAMION_MAP[code][lang];
                }
            });

            // Types d'opérations
            document.querySelectorAll('[data-operation-type]').forEach(el => {
                const code = el.getAttribute('data-operation-type');
                if (OP_MAP[code] && OP_MAP[code][lang]) {
                    el.textContent = OP_MAP[code][lang];
                }
            });

            // Statuts visites
            document.querySelectorAll('[data-visite-status]').forEach(el => {
                const code = el.getAttribute('data-visite-status');
                if (VISITE_STATUS_MAP[code] && VISITE_STATUS_MAP[code][lang]) {
                    el.textContent = VISITE_STATUS_MAP[code][lang];
                }
            });

            // Statuts créneaux
            document.querySelectorAll('[data-creneau-status]').forEach(el => {
                const code = el.getAttribute('data-creneau-status');
                if (CRENEAU_STATUS_MAP[code] && CRENEAU_STATUS_MAP[code][lang]) {
                    el.textContent = CRENEAU_STATUS_MAP[code][lang];
                }
            });

            // Libellé de catégorie de permis sur la fiche
            document.querySelectorAll('[data-license-category]').forEach(el => {
                const cat = el.getAttribute('data-license-category');
                const span = el.querySelector('.license-cat-text');
                if (span && LIC_CAT_MAP[cat] && LIC_CAT_MAP[cat][lang]) {
                    span.textContent = LIC_CAT_MAP[cat][lang];
                }
            });

            // Badges de validité permis dans la liste
            document.querySelectorAll('.license-validity-badge').forEach(badge => {
                const status = badge.getAttribute('data-license-status');
                const days = badge.getAttribute('data-days');
                if (status === 'expire') {
                    badge.innerHTML = `<span class="badge-permis-expire">${dict.badge_expire || 'Expiré'}</span>`;
                } else if (status === 'bientot') {
                    badge.innerHTML = `<span class="badge-permis-bientot">${dict.badge_soon_prefix || 'Expire dans '}${days}${dict.badge_soon_suffix || ' jours'}</span>`;
                } else {
                    badge.innerHTML = `<span class="badge-permis-valide">${dict.badge_valid || 'Permis Valide'}</span>`;
                }
            });

            // Alertes permis sur la fiche détail
            document.querySelectorAll('[data-license-alert]').forEach(box => {
                const alertType = box.getAttribute('data-license-alert');
                const days = box.getAttribute('data-days') || '0';
                const content = box.querySelector('.license-alert-content');
                if (!content) return;
                if (alertType === 'expired') {
                    content.innerHTML = `<strong>${dict.alert_expired_strong || 'Permis Expiré !'}</strong> ${dict.alert_expired_text || "Ce chauffeur n'est plus autorisé à circuler."}`;
                } else if (alertType === 'soon') {
                    const strong = (dict.alert_soon_strong || 'Expiration proche ({days} jours) !').replace('{days}', days);
                    content.innerHTML = `<strong>${strong}</strong> ${dict.alert_soon_text || 'Penser au renouvellement.'}`;
                } else if (alertType === 'valid') {
                    const text = (dict.alert_valid_text || 'Valide pour encore {days} jours.').replace('{days}', days);
                    content.innerHTML = `<strong>${dict.alert_valid_strong || 'Permis en règle.'}</strong> ${text}`;
                }
            });

            // Compteur de visites
            document.querySelectorAll('.visits-count-text').forEach(el => {
                const count = parseInt(el.getAttribute('data-count') || '0', 10);
                const suffix = (count > 1 && dict.visits_plural_suffix) ? dict.visits_plural_suffix : (dict.visits_suffix || 'visites');
                el.textContent = `${count} ${suffix}`;
            });

            // Formulaire chauffeur (Create / Edit)
            const formRoot = document.getElementById('chauffeurFormContainer');
            if (formRoot) {
                const isEdit = formRoot.getAttribute('data-is-edit') === '1';
                const chName = formRoot.getAttribute('data-chauffeur-name') || '';
                const mainTitle = document.getElementById('formMainTitle');
                if (mainTitle) {
                    mainTitle.textContent = isEdit ? ((dict.title_update_prefix || 'Modifier ') + chName) : (dict.title_create || 'Nouveau Chauffeur');
                }
                const submitBtn = document.getElementById('btnSubmitForm');
                if (submitBtn) {
                    submitBtn.textContent = isEdit ? (dict.btn_submit_update || 'Enregistrer les Modifications') : (dict.btn_submit_create || 'Enregistrer le Chauffeur');
                }
            }
        },

        translateEntrepots: function (lang) {
            const dict = this.getTranslations(lang);
            const isRTL = lang === 'ar';

            document.querySelectorAll('.entrepots-container, .form-page-container').forEach(c => {
                c.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
            });

            // Status mapping for Entrepôts and Quais
            const WH_STATUS = {
                ACTIF: { fr: "Opérationnel", en: "Operational", ar: "تشغيلي" },
                MAINTENANCE: { fr: "Maintenance", en: "In Maintenance", ar: "في الصيانة" },
                FERME: { fr: "Fermé", en: "Closed", ar: "مغلق" }
            };
            const QUAI_STATUS = {
                DISPONIBLE: { fr: "Libre", en: "Available", ar: "متاح" },
                OCCUPE: { fr: "Occupé", en: "Occupied", ar: "مشغول" },
                RESERVE: { fr: "Réservé", en: "Reserved", ar: "محجوز" },
                MAINTENANCE: { fr: "Maintenance", en: "In Maintenance", ar: "في الصيانة" }
            };

            document.querySelectorAll('.badge-status-pill').forEach(el => {
                const dot = el.querySelector('.status-dot');
                let targetText = null;

                if (el.classList.contains('status-actif')) targetText = WH_STATUS.ACTIF[lang];
                else if (el.classList.contains('status-disponible')) targetText = QUAI_STATUS.DISPONIBLE[lang];
                else if (el.classList.contains('status-occupe')) targetText = QUAI_STATUS.OCCUPE[lang];
                else if (el.classList.contains('status-reserve')) targetText = QUAI_STATUS.RESERVE[lang];
                else if (el.classList.contains('status-maintenance')) targetText = WH_STATUS.MAINTENANCE[lang];
                else if (el.classList.contains('status-ferme')) targetText = WH_STATUS.FERME[lang];

                if (targetText) {
                    el.innerHTML = '';
                    if (dot) el.appendChild(dot);
                    el.appendChild(document.createTextNode(' ' + targetText));
                }
            });

            document.querySelectorAll('.quai-chip').forEach(el => {
                const dot = el.querySelector('.status-dot');
                let targetText = null;

                if (el.classList.contains('status-disponible')) targetText = QUAI_STATUS.DISPONIBLE[lang];
                else if (el.classList.contains('status-occupe')) targetText = QUAI_STATUS.OCCUPE[lang];
                else if (el.classList.contains('status-reserve')) targetText = QUAI_STATUS.RESERVE[lang];
                else if (el.classList.contains('status-maintenance')) targetText = QUAI_STATUS.MAINTENANCE[lang];

                if (targetText) {
                    // Extract dock number if present
                    const numMatch = el.textContent.match(/\b([A-Za-z0-9\-_]+)\b$/);
                    const dockNum = numMatch ? numMatch[1] : '';
                    el.innerHTML = '';
                    if (dot) el.appendChild(dot);
                    el.appendChild(document.createTextNode(' ' + (dockNum ? dockNum : targetText)));
                }
            });

            // Quai types in select options
            const QUAI_TYPE_MAPPING = {
                'STANDARD': { fr: "Standard (Sec)", en: "Standard (Dry)", ar: "قياسي (جاف)" },
                'FRIGORIFIQUE': { fr: "Frigorifique (Froid positif/négatif)", en: "Refrigerated (Cold storage)", ar: "مبرد (تخزين مبرد/مجمد)" },
                'ADR': { fr: "Matières Dangereuses (ADR)", en: "Hazardous Materials (ADR)", ar: "مواد خطرة (ADR)" },
                'GROS_VOLUME': { fr: "Gros Volume (Haute cadence)", en: "High Volume (High throughput)", ar: "حجم كبير (وتيرة عالية)" },
                'VRAC': { fr: "Vrac / Extérieur", en: "Bulk / Outdoor", ar: "صب / خارجي" }
            };
            document.querySelectorAll('select[name="type"] option, select[name="type_quai"] option').forEach(opt => {
                if (QUAI_TYPE_MAPPING[opt.value]) {
                    opt.textContent = QUAI_TYPE_MAPPING[opt.value][lang];
                }
            });

            // Action toggle buttons
            document.querySelectorAll('.btn-toggle-occupy').forEach(btn => {
                const textSpan = btn.querySelector('span') || btn;
                textSpan.textContent = dict.quai_btn_occupy || (lang === 'en' ? 'Mark Occupied' : lang === 'ar' ? 'تحديد كمشغول' : 'Occuper');
            });
            document.querySelectorAll('.btn-toggle-release').forEach(btn => {
                const textSpan = btn.querySelector('span') || btn;
                textSpan.textContent = dict.quai_btn_release || (lang === 'en' ? 'Free Dock' : lang === 'ar' ? 'تحرير الرصيف' : 'Libérer');
            });
        },

        translateCamions: function (lang) {
            const dict = this.getTranslations(lang);
            const isRTL = lang === 'ar';

            document.querySelectorAll('.camions-container').forEach(c => {
                c.setAttribute('dir', isRTL ? 'rtl' : 'ltr');
            });

            const CAMION_STATUS = {
                'status-disponible': { fr: "Disponible / Prêt", en: "Available / Ready", ar: "متاح / جاهز" },
                'status-transit': { fr: "En Transit / Route", en: "In Transit / Route", ar: "في الطريق / عبور" },
                'status-quai': { fr: "À Quai (En cours)", en: "At Dock (In progress)", ar: "على الرصيف (قيد العمل)" },
                'status-maintenance': { fr: "En Maintenance", en: "Under Maintenance", ar: "في الصيانة" },
                'status-hors-service': { fr: "Hors Service", en: "Out of Service", ar: "خارج الخدمة" }
            };

            const CT_URGENT = {
                fr: "Contrôle technique imminent",
                en: "Inspection Due Soon",
                ar: "فحص فني وشيك"
            };

            document.querySelectorAll('.status-pill').forEach(pill => {
                const txt = pill.textContent.trim();
                const dot = pill.querySelector('.status-dot');

                if (txt.includes('Contrôle technique imminent') || txt.includes('Inspection Due Soon') || txt.includes('فحص فني وشيك')) {
                    pill.innerHTML = '';
                    if (dot) pill.appendChild(dot);
                    pill.appendChild(document.createTextNode(' ' + CT_URGENT[lang]));
                    return;
                }

                for (const cls of Object.keys(CAMION_STATUS)) {
                    if (pill.classList.contains(cls)) {
                        pill.innerHTML = '';
                        if (dot) pill.appendChild(dot);
                        pill.appendChild(document.createTextNode(' ' + CAMION_STATUS[cls][lang]));
                        break;
                    }
                }
            });

            // Back arrow
            const truckArrow = document.getElementById('truckBackArrow');
            if (truckArrow) {
                truckArrow.innerHTML = isRTL ? '&rarr;' : '&larr;';
            }

            // Status select options
            const STATUS_OPTS = {
                'DISPONIBLE': { fr: "Disponible / Prêt", en: "Available / Ready", ar: "متاح / جاهز" },
                'EN_TRANSIT': { fr: "En Transit / Route", en: "In Transit / Route", ar: "في الطريق / عبور" },
                'A_QUAI': { fr: "À Quai (En cours)", en: "At Dock (In progress)", ar: "على الرصيف (قيد العمل)" },
                'EN_MAINTENANCE': { fr: "En Maintenance", en: "Under Maintenance", ar: "في الصيانة" },
                'HORS_SERVICE': { fr: "Hors Service", en: "Out of Service", ar: "خارج الخدمة" }
            };
            document.querySelectorAll('select[name="etat"] option, select[name="nouvel_etat"] option').forEach(opt => {
                if (STATUS_OPTS[opt.value]) {
                    opt.textContent = STATUS_OPTS[opt.value][lang];
                }
            });

            // Truck types select options
            const TYPE_MAPPING = {
                'SEMI_REMORQUE': { fr: "Semi-remorque (Tautliner / Bâché)", en: "Semi-trailer (Curtainsider)", ar: "نصف مقطورة (ستارة / مغطى)" },
                'FOURGON': { fr: "Fourgon Grand Volume (Rigide)", en: "High-Volume Box Truck", ar: "شاحنة صندوقية كبيرة الحجم" },
                'FRIGORIFIQUE': { fr: "Frigorifique (Sous température contrôlée)", en: "Refrigerated (Temperature Controlled)", ar: "مبردة (حرارة مضبوطة)" },
                'PLATEAU': { fr: "Plateau Nu (Charges lourdes / Conteneurs)", en: "Flatbed (Heavy Cargo / Containers)", ar: "سطحة (حمولة ثقيلة / حاويات)" },
                'BENNE': { fr: "Camion Benne (Vrac minéral / Céréales)", en: "Dump Truck (Bulk Minerals / Grain)", ar: "شاحنة قلابة (صب / حبوب)" },
                'CITERNE': { fr: "Citerne (Hydrocarbures & Liquides)", en: "Tanker (Fuel & Liquids)", ar: "صهريج (محروقات وسوائل)" },
                'PORTE_CONTENEUR': { fr: "Porte-conteneur Portuaire", en: "Port Container Chassis", ar: "حاملة حاويات مينائية" }
            };
            document.querySelectorAll('select[name="type_camion"] option').forEach(opt => {
                if (TYPE_MAPPING[opt.value]) {
                    opt.textContent = TYPE_MAPPING[opt.value][lang];
                }
            });

            // Emission norms select options
            const NORME_MAPPING = {
                'EURO_6': { fr: "Euro 6 (Crit'Air 2 - Flotte verte)", en: "Euro 6 (Low emission fleet)", ar: "يورو 6 (أسطول أخضر منخفض الانبعاثات)" },
                'EURO_5': { fr: "Euro 5 (Standard Autoroutier)", en: "Euro 5 (Highway Standard)", ar: "يورو 5 (معيار الطرق السريعة)" },
                'EURO_4': { fr: "Euro 4 (Usage restreint)", en: "Euro 4 (Restricted Use)", ar: "يورو 4 (استخدام مقيد)" },
                'ELECTRIQUE': { fr: "100% Électrique (Zéro Émission)", en: "100% Electric (Zero Emission)", ar: "كهربائي 100% (صفر انبعاثات)" },
                'HYBRIDE': { fr: "Hybride / GNV (Gaz Naturel)", en: "Hybrid / CNG (Natural Gas)", ar: "هجين / غاز طبيعي" }
            };
            document.querySelectorAll('select[name="norme_anti_pollution"] option, select[name="norme"] option').forEach(opt => {
                if (NORME_MAPPING[opt.value]) {
                    opt.textContent = NORME_MAPPING[opt.value][lang];
                }
            });

            const camionSearch = document.querySelector('form[action*="camion"] input[name="q"]');
            if (camionSearch && dict.truck_search_placeholder) {
                camionSearch.setAttribute('placeholder', dict.truck_search_placeholder);
            }
        },

        translateDirectPhrases: function (lang) {
            // Options de sélection
            document.querySelectorAll('select option').forEach(opt => {
                const text = opt.textContent.trim();
                for (const phrase of DIRECT_PHRASES) {
                    if (text === phrase.fr || text === phrase.en || text === phrase.ar) {
                        opt.textContent = phrase[lang] || phrase.fr;
                        break;
                    }
                }
            });

            // Recherche et remplacement ciblé dans les éléments textuels de la session créneaux
            const selectors = [
                '.page-title-box h1', '.page-title-box p',
                '.top-actions-group .btn', '.top-actions-group a',
                '.kpi-label', '.creneaux-table th',
                '.nav-menu .nav-item a', '.badge-slot',
                '.filter-toolbar label', '.filter-toolbar button',
                '.form-group label', '.planning-hours-header div',
                '.current-date-title', '.nav-day-btn',
                '.detail-main-card h1', '.detail-main-card h3',
                '.meta-label', '.dropdown-item-title', '.dropdown-item-sub',
                '.spec-cell-label', '.meta-block-label', '.section-quais-header h2',
                '.section-quais-header p', '.detail-card-title', '.btn-card',
                '.empty-box h3', '.empty-box p', '.empty-state-box h3', '.empty-state-box p'
            ];

            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => {
                    // Si l'élément a des enfants complexes sans balise dédiée, remplacer le texte pur
                    const currentText = el.textContent.trim();
                    for (const phrase of DIRECT_PHRASES) {
                        if (currentText === phrase.fr || currentText === phrase.en || currentText === phrase.ar) {
                            el.textContent = phrase[lang];
                            break;
                        }
                    }
                });
            });

            // Input placeholder spécial pour la recherche
            const searchInput = document.querySelector('.search-input-field');
            if (searchInput) {
                const currentPh = searchInput.getAttribute('placeholder');
                if (currentPh) {
                    searchInput.setAttribute('placeholder', this.t('filter_search_ph', lang));
                }
            }

            // Input placeholder spécial pour le chat Gemini
            const chatInput = document.getElementById('chatInput') || document.getElementById('userInput');
            if (chatInput) {
                chatInput.setAttribute('placeholder', this.t('ai_chat_ph', lang));
            }
        },

        setupUI: function () {
            const trigger = document.getElementById('langMenuTrigger');
            const menu = document.getElementById('langDropdownMenu');
            const wrapper = document.getElementById('langDropdownWrapper');

            if (trigger && menu) {
                trigger.addEventListener('click', function (e) {
                    e.stopPropagation();
                    const isOpen = menu.classList.contains('show');
                    if (isOpen) {
                        menu.classList.remove('show');
                        trigger.classList.remove('active');
                        trigger.setAttribute('aria-expanded', 'false');
                    } else {
                        menu.classList.add('show');
                        trigger.classList.add('active');
                        trigger.setAttribute('aria-expanded', 'true');
                    }
                });

                // Fermer si clic en dehors
                document.addEventListener('click', function (e) {
                    if (wrapper && !wrapper.contains(e.target)) {
                        menu.classList.remove('show');
                        trigger.classList.remove('active');
                        trigger.setAttribute('aria-expanded', 'false');
                    }
                });

                // Touche Escape
                document.addEventListener('keydown', function (e) {
                    if (e.key === 'Escape' && menu.classList.contains('show')) {
                        menu.classList.remove('show');
                        trigger.classList.remove('active');
                        trigger.setAttribute('aria-expanded', 'false');
                        trigger.focus();
                    }
                });
            }

            // Écouteur sur chaque option de langue du menu déroulant
            const options = document.querySelectorAll('.lang-dropdown-option, .lang-pill-btn');
            options.forEach(opt => {
                opt.addEventListener('click', (e) => {
                    e.preventDefault();
                    const lang = opt.getAttribute('data-lang-choice');
                    this.setLanguage(lang, true);

                    // Fermer le menu après sélection
                    if (menu) menu.classList.remove('show');
                    if (trigger) {
                        trigger.classList.remove('active');
                        trigger.setAttribute('aria-expanded', 'false');
                    }
                });
            });
        },

        updateSwitcherUI: function (activeLang) {
            const LANG_METAS = {
                fr: {
                    flagSvg: '<svg class="flag-svg" width="20" height="14" viewBox="0 0 30 20" aria-hidden="true"><rect width="10" height="20" fill="#002654"/><rect x="10" width="10" height="20" fill="#FFFFFF"/><rect x="20" width="10" height="20" fill="#CE1126"/></svg>',
                    code: "FR"
                },
                en: {
                    flagSvg: '<svg class="flag-svg" width="20" height="14" viewBox="0 0 60 30" aria-hidden="true"><clipPath id="uk-f-dyn"><path d="M0,0 v30 h60 v-30 z"/></clipPath><clipPath id="uk-d-dyn"><path d="M30,15 h30 v15 z v15 h-30 z h-30 v-15 z v-15 h30 z"/></clipPath><g clip-path="url(#uk-f-dyn)"><path d="M0,0 v30 h60 v-30 z" fill="#012169"/><path d="M0,0 L60,30 M60,0 L0,30" stroke="#fff" stroke-width="6"/><path d="M0,0 L60,30 M60,0 L0,30" clip-path="url(#uk-d-dyn)" stroke="#C8102E" stroke-width="4"/><path d="M30,0 v30 M0,15 h60" stroke="#fff" stroke-width="10"/><path d="M30,0 v30 M0,15 h60" stroke="#C8102E" stroke-width="6"/></g></svg>',
                    code: "EN"
                },
                ar: {
                    flagSvg: '<svg class="flag-svg" width="20" height="14" viewBox="0 0 30 20" aria-hidden="true"><rect width="30" height="20" fill="#006C35"/><path d="M5 14.2h16.5l2.5-1-2.5-1H5v2z M6.5 11.5v3.5h1.2v-3.5z" fill="#ffffff"/><path d="M6 6.2h2.2v2.5H6z M9 5.8h1.8v3H9z M11.5 5.2h2v3.8h-2z M14.5 5.5h2v3.3h-2z M17.5 5.8h2v2.8h-2z M20.5 6.2h2v2.2h-2z" fill="#ffffff" opacity="0.95"/></svg>',
                    code: "AR"
                }
            };

            const meta = LANG_METAS[activeLang] || LANG_METAS.fr;
            const flagEl = document.getElementById('langCurrentFlag');
            const codeEl = document.getElementById('langCurrentCode');

            if (flagEl) flagEl.innerHTML = meta.flagSvg;
            if (codeEl) codeEl.textContent = meta.code;

            document.querySelectorAll('.lang-dropdown-option, .lang-pill-btn').forEach(btn => {
                const btnLang = btn.getAttribute('data-lang-choice');
                if (btnLang === activeLang) {
                    btn.classList.add('active');
                    btn.setAttribute('aria-pressed', 'true');
                } else {
                    btn.classList.remove('active');
                    btn.setAttribute('aria-pressed', 'false');
                }
            });
        }
    };

    // Export global
    window.CargoLinkI18n = CargoLinkI18n;

    // Auto-init au chargement du DOM
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', () => CargoLinkI18n.init());
    } else {
        CargoLinkI18n.init();
    }
})();
