"""
Données de référence de l'évaluation CargoLink AI (base SQLite isolée, jamais Supabase).
Crée les entrepôts, quais, camions et chauffeurs, puis transforme chaque scénario JSON
en vraie livraison, pour que l'IA reçoive exactement le même contexte que dans l'application.
"""
from datetime import date, datetime, time, timedelta

from django.contrib.auth.models import User
from django.utils import timezone

from camions.models import Camion
from chauffeurs.models import Chauffeur
from creneaux.models import Creneau
from entrepots.models import Entrepot, Quai
from livraisons import geo
from livraisons.models import IncidentLivraison, Livraison

ENTREPOTS = {
    'RADES': ("Hub Logistique Portuaire de Radès", "ENT-RADES-01", "Radès", "2040"),
    'TUNIS': ("Centre Logistique Tunis Aéroport", "ENT-TUNIS-02", "Tunis", "2035"),
    'SFAX': ("Plateforme Agro-Logistique Sfax Sud", "ENT-SFAX-03", "Sfax", "3000"),
    'SOUSSE': ("Entrepôt Sahel Sousse", "ENT-SOUSSE-04", "Sousse", "4000"),
}

CAMIONS = {
    'semi_euro6': dict(immatriculation="234 TUN 5678", marque="Volvo Trucks", modele="FH16", type_camion='SEMI_REMORQUE',
                       capacite_tonnage=25, capacite_palettes=33, norme_anti_pollution='EURO_6', societe_transport="TransMed Express"),
    'semi_ct': dict(immatriculation="245 TUN 1100", marque="Scania", modele="R450", type_camion='SEMI_REMORQUE',
                    capacite_tonnage=25, capacite_palettes=33, norme_anti_pollution='EURO_5', societe_transport="Carthage Logistics",
                    prochain_controle_jours=5),
    'frigo': dict(immatriculation="198 TUN 1124", marque="Scania", modele="P280", type_camion='FRIGORIFIQUE',
                  capacite_tonnage=22.5, capacite_palettes=30, norme_anti_pollution='EURO_6', societe_transport="STAF Agro Logistics"),
    'porteur': dict(immatriculation="215 TUN 9931", marque="Mercedes-Benz", modele="Atego", type_camion='PORTEUR',
                    capacite_tonnage=18, capacite_palettes=22, norme_anti_pollution='EURO_5', societe_transport="Express Fret Tunisie"),
    'fourgon': dict(immatriculation="241 TUN 3302", marque="Renault", modele="Master E-Tech", type_camion='FOURGON',
                    capacite_tonnage=3.5, capacite_palettes=6, norme_anti_pollution='ELECTRIQUE', societe_transport="GreenCargo Livraisons"),
    'citerne': dict(immatriculation="177 TUN 8450", marque="DAF", modele="XF", type_camion='CITERNE',
                    capacite_tonnage=26, capacite_palettes=28, norme_anti_pollution='EURO_4', societe_transport="PetroTrans Maghreb"),
    'maintenance': dict(immatriculation="160 TUN 0001", marque="Iveco", modele="S-Way", type_camion='SEMI_REMORQUE',
                        capacite_tonnage=25, capacite_palettes=33, norme_anti_pollution='EURO_6', etat='EN_MAINTENANCE'),
}

CHAUFFEURS = {
    'khalil': dict(prenom="Khalil", nom="Hlila", categorie_permis='C_CE_ADR', expiration_jours=500,
                   entreprise_transport="TransMed Express", immatriculation_camion="234 TUN 5678", type_camion='SEMI_REMORQUE'),
    'tarak': dict(prenom="Tarak", nom="Mansour", categorie_permis='CE', expiration_jours=300,
                  entreprise_transport="Carthage Logistics", immatriculation_camion="245 TUN 1100", type_camion='SEMI_REMORQUE'),
    'sami': dict(prenom="Sami", nom="Trabelsi", categorie_permis='CE', expiration_jours=10,
                 entreprise_transport="Trans-Maghreb Cargo", type_camion='SEMI_REMORQUE'),
    'walid': dict(prenom="Walid", nom="Bouazizi", categorie_permis='C', expiration_jours=400,
                  entreprise_transport="STAF Agro Logistics", immatriculation_camion="198 TUN 1124", type_camion='FRIGORIFIQUE'),
    'nader': dict(prenom="Nader", nom="Gharbi", categorie_permis='B', expiration_jours=400,
                  entreprise_transport="GreenCargo Livraisons", immatriculation_camion="241 TUN 3302", type_camion='FOURGON'),
    'kamel': dict(prenom="Kamel", nom="Zouari", categorie_permis='CE', expiration_jours=-5,
                  entreprise_transport="Tunis Fret International", type_camion='SEMI_REMORQUE'),
}


class Referentiel:
    """Crée et garde les objets de référence, indexés par leur clé courte."""

    def __init__(self):
        aujourd_hui = date.today()
        self.planificateur = User.objects.create_user('eval_planificateur', 'eval@cargolink.tn', 'Evaluation-2026')
        self.planificateur.profile.role = 'PLANIFICATEUR'
        self.planificateur.profile.save()

        self.entrepots, self.quais = {}, {}
        for cle, (nom, code, ville, cp) in ENTREPOTS.items():
            entrepot = Entrepot.objects.create(
                nom=nom, code=code, adresse="Zone industrielle", ville=ville, code_postal=cp,
                horaire_ouverture=time(0, 0), horaire_fermeture=time(23, 59),
            )
            self.entrepots[cle] = entrepot
            self.quais[cle] = {
                'STANDARD': [Quai.objects.create(entrepot=entrepot, numero=f"{cle[:3]}-Q{i}", type_quai='STANDARD') for i in (1, 2, 3)],
                'FRIGORIFIQUE': Quai.objects.create(entrepot=entrepot, numero=f"{cle[:3]}-FRIGO", type_quai='FRIGORIFIQUE'),
                'ADR': Quai.objects.create(entrepot=entrepot, numero=f"{cle[:3]}-ADR", type_quai='ADR'),
            }

        self.camions = {}
        for cle, donnees in CAMIONS.items():
            donnees = dict(donnees)
            jours = donnees.pop('prochain_controle_jours', 300)
            donnees.setdefault('etat', 'DISPONIBLE')
            self.camions[cle] = Camion.objects.create(
                date_prochain_controle=aujourd_hui + timedelta(days=jours), **donnees
            )

        self.chauffeurs = {}
        for i, (cle, donnees) in enumerate(CHAUFFEURS.items(), start=1):
            donnees = dict(donnees)
            jours = donnees.pop('expiration_jours')
            self.chauffeurs[cle] = Chauffeur.objects.create(
                telephone=f"+216 98 000 {i:03d}", numero_permis=f"EVAL-PERM-{i:03d}",
                date_expiration_permis=aujourd_hui + timedelta(days=jours), **donnees
            )

    # ------------------------------------------------------------------
    def quai_pour(self, cle_entrepot, marchandise):
        quais = self.quais[cle_entrepot]
        if marchandise in ('FRIGORIFIQUE', 'ADR'):
            return quais[marchandise]
        return quais['STANDARD'][0]

    def construire(self, spec, maintenant):
        """Transforme un scénario JSON en livraison (création directe, comme une donnée existante)."""
        camion = self.camions.get(spec.get('camion')) if spec.get('camion') else None
        chauffeur = self.chauffeurs.get(spec.get('chauffeur')) if spec.get('chauffeur') else None
        marchandise = spec.get('marchandise', 'STANDARD')
        origine = self.entrepots[spec['origine']]
        client = spec.get('client')
        destination = None if client else self.entrepots[spec['destination']]
        ville_arrivee = client['ville'] if client else destination.ville

        depart = (maintenant + timedelta(minutes=spec['depart_min'])).replace(second=0, microsecond=0)
        duree = geo.duree_trajet(geo.distance_km(origine.ville, ville_arrivee), camion.type_camion if camion else 'SEMI_REMORQUE')
        eta = depart + duree
        echeance = spec['echeance']
        if 'eta_plus' in echeance:
            date_echeance = eta + timedelta(minutes=echeance['eta_plus'])
        else:
            date_echeance = maintenant + timedelta(minutes=echeance['depuis_maintenant'])
        if date_echeance <= depart:
            date_echeance = depart + timedelta(minutes=30)

        livraison = Livraison(
            type_livraison='CLIENT' if client else 'INTER_ENTREPOT',
            statut=spec['statut'],
            priorite=spec.get('priorite', 'NORMALE'),
            entrepot_origine=origine,
            entrepot_destination=destination,
            camion=camion,
            chauffeur=chauffeur,
            type_marchandise=marchandise,
            description_marchandise="Marchandise d'évaluation",
            nb_palettes=spec['palettes'],
            poids_kg=spec['poids'],
            numero_bl=f"EVAL-{spec['id']}",
            date_depart_prevue=depart,
            date_livraison_prevue=date_echeance,
            est_en_retard=spec.get('en_retard', False),
            createur=self.planificateur,
        )
        if client:
            livraison.destinataire_nom = client['nom']
            livraison.adresse_livraison = "Zone industrielle"
            livraison.ville_livraison = client['ville']
        if spec['statut'] in ('EN_CHARGEMENT', 'EN_TRANSIT', 'ARRIVEE', 'LIVREE'):
            livraison.date_depart_reelle = depart
        if spec['statut'] == 'ARRIVEE':
            # Arrivée à l'heure prévue (au plus tard maintenant) : cohérent avec l'échéance du scénario
            livraison.date_arrivee_reelle = min(eta, maintenant - timedelta(minutes=5))
        if spec['statut'] == 'LIVREE':
            livre = depart + timedelta(minutes=spec.get('livree_min', 240))
            livraison.date_arrivee_reelle = livre - timedelta(minutes=10)
            livraison.date_livraison_reelle = livre
            livraison.receptionnaire_nom = "Responsable réception"
        if spec['statut'] == 'ANNULEE':
            livraison.motif_annulation = "Commande reportée par le client."

        if spec.get('creneaux'):
            livraison.creneau_chargement = self._creneau(origine, spec['origine'], marchandise, depart - timedelta(minutes=45), depart, 'CHARGEMENT', livraison)
            if destination:
                livraison.creneau_dechargement = self._creneau(destination, spec['destination'], marchandise, eta, eta + timedelta(minutes=45), 'DECHARGEMENT', livraison)
        livraison.save()

        for incident in spec.get('incidents', []):
            IncidentLivraison.objects.create(
                livraison=livraison, type_incident=incident['type'], gravite=incident['gravite'],
                description=f"Incident d'évaluation : {incident['type'].lower()}.",
            )
        return livraison

    def _creneau(self, entrepot, cle, marchandise, debut, fin, type_operation, livraison):
        debut_local, fin_local = timezone.localtime(debut), timezone.localtime(fin)
        if debut_local.date() != fin_local.date():
            debut_local = datetime.combine(fin_local.date(), time(0, 0), tzinfo=fin_local.tzinfo)
        return Creneau.objects.create(
            entrepot=entrepot, quai=self.quai_pour(cle, marchandise), date_creneau=fin_local.date(),
            heure_debut=debut_local.time().replace(second=0, microsecond=0),
            heure_fin=fin_local.time().replace(second=0, microsecond=0),
            type_operation=type_operation, statut='CONFIRME', type_marchandise=marchandise,
            transporteur_nom="Évaluation", immatriculation_camion=livraison.camion.immatriculation if livraison.camion else "À affecter",
            chauffeur_nom=livraison.chauffeur.nom_complet if livraison.chauffeur else "À affecter",
            nb_palettes=livraison.nb_palettes,
        )
