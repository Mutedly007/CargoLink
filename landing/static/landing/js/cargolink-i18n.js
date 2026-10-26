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

            // Toasts & feedback
            toast_lang_changed: "🌐 Langue basculée en Français",
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

            // Toasts & feedback
            toast_lang_changed: "🌐 Language switched to English",
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

            // Toasts & feedback
            toast_lang_changed: "🌐 تم تغيير لغة الواجهة إلى العربية",
        }
    };

    // Table of direct text phrases for elements without data-i18n attributes
    const DIRECT_PHRASES = [
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
                '.meta-label', '.dropdown-item-title', '.dropdown-item-sub'
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
