"""
Affectation intelligente camion + chauffeur (Module Eya - Volet IA).
Même approche que SmartDockAllocator (module Kacem) : contraintes dures puis score multi-critères.

Contraintes dures (règles R1 à R7) :
  capacité, état du camion, camion frigorifique, permis valide / catégorie / ADR, disponibilité sur la période.
Critères souples (score sur 100) :
  - Adéquation de capacité (30) : remplissage idéal autour de 85 %, ni camion sous-dimensionné ni trop grand
  - Disponibilité immédiate (15) : camion et chauffeur libres maintenant si le départ est proche
  - Performance environnementale (15) : norme Euro 6 / hybride / électrique favorisée (ODD 12)
  - Affinité (15) : camion habituel du chauffeur, même société de transport
  - Fiabilité (15) : contrôle technique et permis sans échéance proche
  - Équité de charge (10) : répartition des missions entre chauffeurs sur 7 jours
"""
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from . import regles

POINTS_NORME = {'ELECTRIQUE': 15, 'HYBRIDE': 13, 'EURO_6': 11, 'EURO_5': 6, 'EURO_4': 2}


class MoteurAffectation:

    def recommander(self, *, poids_kg=None, nb_palettes=None, type_marchandise='STANDARD',
                    debut=None, fin=None, livraison_pk=None, limite=3):
        from camions.models import Camion
        from chauffeurs.models import Chauffeur

        camions = list(Camion.objects.exclude(etat__in=regles.ETATS_CAMION_BLOQUANTS))
        chauffeurs = list(Chauffeur.objects.exclude(statut='INACTIF'))
        exclusions_camions, exclusions_chauffeurs = [], []

        # Contraintes propres au camion (une seule évaluation par camion)
        camions_ok = []
        for camion in camions:
            erreurs = regles.verifier_camion(camion, poids_kg, nb_palettes, type_marchandise)
            erreurs.update(regles.conflits_planning(debut, fin, camion=camion, exclure_pk=livraison_pk))
            if erreurs:
                exclusions_camions.append({'label': camion.immatriculation, 'motif': next(iter(erreurs.values()))})
            else:
                camions_ok.append(camion)

        # Contraintes propres au chauffeur
        chauffeurs_ok = []
        for chauffeur in chauffeurs:
            erreurs = regles.verifier_chauffeur(chauffeur, None, type_marchandise, fin)
            erreurs.update(regles.conflits_planning(debut, fin, chauffeur=chauffeur, exclure_pk=livraison_pk))
            if erreurs:
                exclusions_chauffeurs.append({'label': chauffeur.nom_complet, 'motif': next(iter(erreurs.values()))})
            else:
                chauffeurs_ok.append(chauffeur)

        charge_recente = self._charge_7_jours([c.pk for c in chauffeurs_ok])
        depart_proche = bool(debut and debut - timezone.now() < timedelta(hours=6))

        propositions = []
        for camion in camions_ok:
            for chauffeur in chauffeurs_ok:
                # Contrainte de couple : catégorie de permis compatible avec le gabarit
                if regles.verifier_chauffeur(chauffeur, camion, type_marchandise, fin):
                    continue
                propositions.append(self._scorer(
                    camion, chauffeur, poids_kg, nb_palettes, depart_proche, charge_recente.get(chauffeur.pk, 0)
                ))

        propositions.sort(key=lambda p: p['score'], reverse=True)
        if not propositions:
            return {
                'success': False,
                'message': "Aucune combinaison camion + chauffeur ne respecte toutes les contraintes.",
                'exclusions_camions': exclusions_camions,
                'exclusions_chauffeurs': exclusions_chauffeurs,
            }
        return {
            'success': True,
            'recommandations': propositions[:limite],
            'nb_combinaisons': len(propositions),
            'exclusions_camions': exclusions_camions,
            'exclusions_chauffeurs': exclusions_chauffeurs,
        }

    def _charge_7_jours(self, chauffeur_ids):
        from .models import Livraison

        depuis = timezone.now() - timedelta(days=7)
        lignes = (
            Livraison.objects.filter(chauffeur_id__in=chauffeur_ids, date_depart_prevue__gte=depuis)
            .exclude(statut='ANNULEE')
            .values('chauffeur_id').annotate(nb=Count('id'))
        )
        return {ligne['chauffeur_id']: ligne['nb'] for ligne in lignes}

    def _scorer(self, camion, chauffeur, poids_kg, nb_palettes, depart_proche, nb_missions):
        points_forts, points_attention = [], []

        # 1. Adéquation de capacité (30)
        taux = []
        if poids_kg and camion.capacite_tonnage:
            taux.append(poids_kg / float(camion.capacite_tonnage * 1000))
        if nb_palettes and camion.capacite_palettes:
            taux.append(nb_palettes / camion.capacite_palettes)
        remplissage = max(taux) if taux else 0.5
        score_capacite = 30 * max(0.0, 1 - abs(0.85 - remplissage) / 0.85)
        if remplissage >= 0.6:
            points_forts.append(f"Remplissage optimal du camion ({round(remplissage * 100)} %)")
        elif remplissage < 0.35:
            points_attention.append(f"Camion surdimensionné (remplissage {round(remplissage * 100)} %)")

        # 2. Disponibilité immédiate (15)
        score_dispo = 15
        if depart_proche:
            if camion.etat != 'DISPONIBLE':
                score_dispo -= 8
                points_attention.append(f"Camion actuellement « {camion.get_etat_display()} »")
            if chauffeur.statut != 'DISPONIBLE':
                score_dispo -= 7
                points_attention.append(f"Chauffeur actuellement « {chauffeur.get_statut_display()} »")
        if score_dispo == 15 and depart_proche:
            points_forts.append("Camion et chauffeur disponibles immédiatement")

        # 3. Performance environnementale (15)
        score_eco = POINTS_NORME.get(camion.norme_anti_pollution, 5)
        if score_eco >= 11:
            points_forts.append(f"Véhicule faible émission ({camion.get_norme_anti_pollution_display()})")

        # 4. Affinité chauffeur / camion (15)
        score_affinite = 0
        if (chauffeur.immatriculation_camion or '').strip().upper() == camion.immatriculation.strip().upper():
            score_affinite += 10
            points_forts.append("Camion habituel du chauffeur")
        elif chauffeur.type_camion == camion.type_camion:
            score_affinite += 5
            points_forts.append("Chauffeur habitué à ce gabarit")
        if camion.societe_transport and chauffeur.entreprise_transport \
                and camion.societe_transport.lower() == chauffeur.entreprise_transport.lower():
            score_affinite += 5
            points_forts.append("Même société de transport")

        # 5. Fiabilité (15)
        score_fiabilite = 15
        if camion.controle_technique_urgent:
            score_fiabilite -= 8
            points_attention.append("Contrôle technique du camion à échéance proche")
        if regles.permis_expire_bientot(chauffeur):
            score_fiabilite -= 7
            points_attention.append("Permis du chauffeur expirant sous 30 jours")

        # 6. Équité de charge (10)
        score_equite = max(0, 10 - 3 * nb_missions)
        if nb_missions == 0:
            points_forts.append("Aucune mission sur les 7 derniers jours (équité)")
        elif nb_missions >= 3:
            points_attention.append(f"{nb_missions} missions sur les 7 derniers jours")

        score = round(score_capacite + score_dispo + score_eco + score_affinite + score_fiabilite + score_equite)
        return {
            'camion_id': camion.pk,
            'camion_label': f"{camion.immatriculation} • {camion.marque} {camion.modele}",
            'camion_type': camion.get_type_camion_display(),
            'capacite_tonnes': float(camion.capacite_tonnage),
            'capacite_palettes': camion.capacite_palettes,
            'chauffeur_id': chauffeur.pk,
            'chauffeur_label': chauffeur.nom_complet,
            'chauffeur_permis': chauffeur.get_categorie_permis_display(),
            'score': min(100, score),
            'remplissage_pct': round(remplissage * 100) if taux else None,
            'details': {
                'capacite': round(score_capacite),
                'disponibilite': score_dispo,
                'environnement': score_eco,
                'affinite': score_affinite,
                'fiabilite': score_fiabilite,
                'equite': score_equite,
            },
            'points_forts': points_forts,
            'points_attention': points_attention,
        }
