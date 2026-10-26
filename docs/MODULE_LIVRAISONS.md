# Module Gestion des Livraisons (Eya) — Plan d'intégration & guide

> Branche : `eya` · App Django : `livraisons/` · Statut : prêt pour revue avant fusion dans `main`

## 1. Pourquoi ce module

Les quatre modules existants gèrent chacun **une ressource** : entrepôts et quais (Aziz), camions (Rahma),
chauffeurs (Khalil), créneaux de quai (Kacem). Aucun ne représente **la marchandise qui voyage d'un point A
à un point B**. La **Livraison** est cet objet métier : elle relie un camion, un chauffeur, un créneau de
chargement, un créneau de déchargement et deux entrepôts (ou un client final), du chargement jusqu'à la
**preuve de livraison**.

Deux types de livraison :

| Type | Départ | Arrivée |
| :--- | :--- | :--- |
| Transfert inter-entrepôts | Créneau de chargement (quai) | Créneau de déchargement (quai) |
| Livraison client | Créneau de chargement (quai) | Adresse du client + signature / photo |

## 2. Constats issus du test de l'application (rôle par rôle)

L'application a été parcourue avec chaque compte de la base Supabase (lecture seule) :

| Rôle | Comptes | Accès constatés |
| :--- | :--- | :--- |
| ADMIN | `admin` | Tout |
| PLANIFICATEUR | `kacem trabelsi` | Créneaux, entrepôts, camions — **pas** les pages Chauffeurs |
| ENTREPOT | `aziz_logi`, `r-ENTREPOT` | Entrepôts, créneaux en lecture seule — pas les Chauffeurs |
| TRANSPORTEUR | `r-transporteur`, `khalil_chauffeur`, `tt-tt` | Camions (les siens), chauffeurs — **pas** les Créneaux |

Conséquences pour la conception :

1. **Le planificateur ne voit pas les chauffeurs** → le module Livraisons propose lui-même les chauffeurs
   (et camions) compatibles dans son formulaire.
2. **Le transporteur ne voit pas les créneaux** → la livraison affiche elle-même le quai et l'heure au chauffeur
   (page « Missions en cours »).
3. **Les liens entre modules sont textuels** (`Creneau.chauffeur_nom`, `Chauffeur.immatriculation_camion`) :
   dans les données réelles, des créneaux associent un chauffeur au camion d'un autre. La livraison utilise de
   **vraies clés étrangères** et recopie les bonnes valeurs dans les créneaux liés.
4. **Un seul compte transporteur est lié à un chauffeur** (`khalil_chauffeur` → « test testt ») et tous les
   camions appartiennent à `admin`. Pour qu'un transporteur voie ses livraisons, il faut lier son compte à un
   chauffeur (`Chauffeur.transporteur_user`) ou à un camion (`Camion.transporteur`).

## 3. Intégration avec les modules de l'équipe

**Principe : aucune migration dans les apps des coéquipiers.** Toutes les clés étrangères partent de
`livraisons`. Les changements d'état passent par les **méthodes existantes** des autres modules.

| Étape livraison | Créneaux (Kacem) | Quais (Aziz) | Camion (Rahma) | Chauffeur (Khalil) | Historiques |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Planifier | `confirmer()` + recopie camion/chauffeur | — | — | — | Suivi |
| Charger | `marquer_arrive()` + `mettre_a_quai()` | OCCUPE | A_QUAI | A_QUAI | Suivi |
| Partir | `terminer()` | DISPONIBLE | EN_TRANSIT | EN_MISSION | `HistoriquePassage` + `VisiteChauffeur` |
| Arriver | `marquer_arrive()` + `mettre_a_quai()` (destination) | OCCUPE | A_QUAI | A_QUAI | Suivi |
| Livrer (POD) | `terminer()` | DISPONIBLE | DISPONIBLE | DISPONIBLE | `HistoriquePassage` + `VisiteChauffeur` |
| Annuler | `annuler()` | libéré | — | — | Suivi |

Réservation automatique d'un créneau : le bouton « Réserver automatiquement » appelle
`SmartDockAllocator.recommend_best_dock()` du module Créneaux, puis crée le créneau (validé par
`Creneau.clean()`, donc sans conflit ni hors horaires).

Fichiers partagés modifiés (uniquement des ajouts) :

- `cargolink/settings.py` : `'livraisons'` dans `INSTALLED_APPS`, chargement du `.env`, configuration DeepSeek
- `cargolink/urls.py` : `path('livraisons/', include('livraisons.urls'))`
- `landing/templates/landing/base.html` : liens « Livraisons » (navbar et footer)
- `.env.example`, `.gitignore`, `cargolink/settings_test.py` (tests sur SQLite)

### Points de coordination à valider avec l'équipe

| Avec | Sujet | Proposition |
| :--- | :--- | :--- |
| Khalil | L'« affectation de mission » du module Chauffeurs **déplace un créneau** vers un autre entrepôt et passe le camion / chauffeur en mission (observé en direct sur Supabase). Elle peut donc entrer en conflit avec une livraison planifiée sur les mêmes ressources. | Ignorer les créneaux liés à une livraison (`creneau.livraisons_chargement.exists()`), ou créer une livraison à la place. Garde-fou déjà en place côté Livraisons : l'action est refusée si le créneau a été déplacé. |
| Khalil | « Libérer mission » clôture les créneaux trouvés par **nom** de chauffeur. | Filtrer par créneaux non liés à une livraison. |
| Rahma | Un transporteur ne voit que ses camions (`Camion.transporteur`). | Même règle reprise dans les Livraisons. Lier les camions de démo aux comptes transporteurs. |
| Kacem | Les créneaux créés par la livraison ont la consigne « Créneau réservé automatiquement pour la livraison LIV-… ». | Afficher un badge « Livraison liée » sur le détail du créneau (optionnel). |
| Équipe | `TIME_ZONE='UTC'` : les heures réelles s'affichent avec 1 h d'écart avec la Tunisie. | Passer à `Africa/Tunis` (décision commune). |
| Équipe | Secrets en clair dans `settings.py` (mot de passe Supabase, clé Gemini). | Les déplacer dans `.env` (désormais chargé) puis changer le mot de passe et la clé. |

## 4. Fonctionnalités

### Cœur

- CRUD des livraisons (planificateur), deux types, échéance **calculée automatiquement** à partir de la distance
- Cycle de vie : `BROUILLON → PLANIFIEE → EN_CHARGEMENT → EN_TRANSIT → ARRIVEE → LIVREE`, avec `ECHEC` et `ANNULEE`
- Retard : indicateur `est_en_retard` (commande `check_retards_livraisons`) plutôt qu'un statut, pour ne pas perdre l'étape en cours
- Preuve de livraison mobile : **signature au doigt**, photo, réserves, conformité, note de satisfaction
- Incidents (panne, accident, dommage, refus…) et **réaffectation** du camion / chauffeur
- Espace chauffeur mobile « Missions en cours » : une grande action à la fois
- Bon de livraison imprimable (A4 / PDF via le navigateur) et export CSV filtré
- **Suivi public par code** sans compte, sans aucune donnée personnelle

### Règles de gestion (contraintes dures, `livraisons/regles.py`)

R1 charge utile · R2 palettes · R3 camion ni en maintenance ni hors service · R4 permis valide jusqu'à la fin
de la livraison et chauffeur actif · catégorie de permis compatible avec le gabarit (CE pour une semi-remorque)
· R5 habilitation ADR · R6 camion frigorifique pour le froid · R7 pas de double affectation sur la période ·
R8 créneaux cohérents (type, entrepôt, non annulés, non partagés) · R9 dates · R10 champs selon le type ·
R11 preuve obligatoire pour clôturer.

### Avancé

| Fonction | Fonctionnement |
| :--- | :--- |
| **Affectation intelligente** | Contraintes dures puis score sur 100 : capacité (30), disponibilité immédiate (15), environnement / norme Euro (15), affinité chauffeur-camion (15), fiabilité CT / permis (15), équité de charge sur 7 jours (10). Top 3 avec points forts / points d'attention et ressources écartées avec leur motif. |
| **Recherche avancée** | 12 critères combinables (texte, statuts, entrepôt, ville, type, priorité, marchandise, chauffeur, camion, période, en retard, incidents) + tri. Les KPI sont cliquables. |
| **Recherche en langage naturel** | « livraisons urgentes en retard vers Sfax cette semaine » → filtres validés (DeepSeek, ou moteur de mots-clés local). |
| **Analyse de risque** | Score 0-100, facteurs et recommandations (ETA vs échéance, incidents, CT, permis, ADR, froid, distance…). |
| **Message destinataire FR / AR / EN** | SMS / email prêt à copier (répond à la promesse « multilingue » des slides). |
| **ETA & CO₂** | Distance routière estimée entre villes tunisiennes, durée selon le gabarit, émissions selon la norme du camion (ODD 12 / 13). |
| **Réservation automatique de créneau** | Via l'allocateur de quais de Kacem. |

## 5. IA DeepSeek — prompt engineering

Fichier : `livraisons/ai_service.py`. API compatible OpenAI (`/chat/completions`), **mode JSON**.

- **Prompt système** : rôle « CargoLink Delivery Copilot », périmètre limité aux livraisons, interdiction d'inventer, JSON uniquement.
- **Séparation données / instructions** : les données sont envoyées dans `<donnees>…</donnees>`, et le prompt précise que tout texte qui s'y trouve (consignes, noms saisis par les utilisateurs) est une donnée, jamais une instruction (protection contre l'injection de prompt).
- **Schéma + exemple (few-shot)** pour chaque tâche, température basse (0 à 0,2, et 0,5 pour la rédaction).
- **Validation serveur** de chaque réponse : valeurs autorisées (statuts, priorités…), bornes (score 0-100), longueurs ; une valeur hors liste est ignorée.
- **Minimisation des données** : ni téléphone, ni email, ni adresse exacte envoyés au modèle.
- **Repli local** systématique si la clé est absente ou l'API indisponible : l'application fonctionne sans IA.
- **Affichage** : réponses insérées avec `textContent` (aucun HTML du modèle interprété), source affichée (« DeepSeek » / « Moteur local »).

Configuration (fichier `.env` à la racine, jamais commité) :

```env
DEEPSEEK_API_KEY=sk-...
DEEPSEEK_MODEL=deepseek-chat
```

## 6. Rôles et périmètre

| Action | Planificateur / Admin | Transporteur (ses livraisons) | Gestionnaire d'entrepôt (ses sites) |
| :--- | :---: | :---: | :---: |
| Voir | Toutes | Chauffeur ou camion lié à son compte | Départ ou arrivée dans ses entrepôts |
| Créer, modifier, planifier, annuler, réaffecter | Oui | — | — |
| Charger, partir | Oui | Oui | — |
| Arriver, preuve de livraison, échec | Oui | Oui | Destination uniquement |
| Déclarer un incident | Oui | Oui | Oui |

Une livraison hors périmètre renvoie une **404** (on ne révèle pas son existence). Toutes les actions sont en **POST + CSRF**.

## 7. Lancer, tester, démontrer

```bash
uv sync
uv run python manage.py migrate                      # crée uniquement les 3 tables livraisons_*
uv run python manage.py populate_livraisons          # 6 livraisons de démo (--clear pour les retirer)
uv run python manage.py check_retards_livraisons     # à planifier toutes les 15 min (--dry-run pour simuler)
uv run python manage.py runserver
```

Tests (base SQLite isolée, ne touche jamais Supabase) :

```bash
uv run python manage.py test --settings=cargolink.settings_test
```

Résultat : **133 tests OK** (54 tests du module Livraisons + tous les tests existants des autres modules).

Scénario de démonstration conseillé (soutenance) :

1. Planificateur → *Nouvelle livraison* Radès → Sfax, 24 palettes / 18 t, départ demain 08:30, échéance vide (calculée).
2. *Affectation intelligente + explication IA* → choisir la première proposition → *Enregistrer et planifier*.
3. Sur le détail : *Réserver automatiquement* les créneaux de chargement et de déchargement (allocateur de Kacem).
4. Ouvrir *Entrepôts & Quais* et *Planning & Créneaux* dans un autre onglet pendant les étapes : *à quai* (le quai passe OCCUPÉ), *départ* (quai libéré, camion EN_TRANSIT, historiques du camion et du chauffeur créés).
5. *Déclarer l'arrivée* puis *Preuve de livraison* avec signature au doigt (sur téléphone).
6. Montrer le *suivi public* (lien du détail), le *bon de livraison*, la *recherche en langage naturel* et l'*analyse de risque*.

## 8. Perspectives

- Tournées multi-arrêts / groupage (« covoiturage de marchandises » de la conclusion) : modèle `Tournee`.
- Notifications email / SMS au destinataire à chaque étape (n8n branché sur `check_retards_livraisons`).
- Carte (Leaflet / OpenStreetMap) et ETA recalculée depuis la position déclarée.
- FK `Chauffeur.camion` et liste unique des gabarits de camion pour tout le projet.
