"""
Évaluation de CargoLink AI (module Livraisons) : métriques et temps de réponse.

Usage (base SQLite isolée, ne touche jamais Supabase) :
    uv run python manage.py evaluer_ia --settings=cargolink.settings_test

Produit dans livraisons/evaluation/resultats/ :
    evaluation_<date>.json  (toutes les mesures et chaque cas)
    evaluation_<date>.html  (rapport lisible)
"""
import json
import os
import random
import statistics
import time
from datetime import timedelta
from html import escape
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from entrepots.models import Entrepot
from livraisons import regles
from livraisons.ai_service import (DeepSeekLivraisonAI, contexte_livraison, message_local, recherche_locale,
                                   risque_local)
from livraisons.evaluation import metriques as m
from livraisons.evaluation.referentiel import Referentiel
from livraisons.smart_assign import MoteurAffectation

DOSSIER = Path(__file__).resolve().parents[2] / 'evaluation'
NIVEAUX = ['faible', 'moyen', 'eleve']


class Command(BaseCommand):
    help = "Évalue CargoLink AI (recherche, risque, messages, affectation) et mesure les temps de réponse."

    def add_arguments(self, parser):
        parser.add_argument('--sortie', default=str(DOSSIER / 'resultats'), help="Dossier des résultats.")
        parser.add_argument('--graine', type=int, default=42, help="Graine aléatoire du contrôle du moteur.")
        parser.add_argument('--limite', type=int, default=None, help="Nombre de cas par jeu (essai rapide).")

    def handle(self, *args, **options):
        if 'sqlite' not in settings.DATABASES['default']['ENGINE']:
            raise CommandError(
                "Par sécurité, l'évaluation ne tourne que sur une base SQLite isolée : "
                "ajoutez --settings=cargolink.settings_test"
            )
        cle = os.environ.get('DEEPSEEK_API_KEY', '')
        if not cle:
            raise CommandError("DEEPSEEK_API_KEY absente : renseignez-la dans le fichier .env.")

        self.stdout.write("Préparation de la base d'évaluation isolée...")
        call_command('migrate', verbosity=0, interactive=False)
        call_command('flush', verbosity=0, interactive=False)

        self.limite = options['limite']
        self.ia = DeepSeekLivraisonAI(api_key=cle, cache_secondes=0)
        self.mesures = []
        self.maintenant = timezone.now().replace(second=0, microsecond=0)
        self.aujourd_hui = timezone.localdate()
        self.ref = Referentiel()

        debut = time.perf_counter()
        resultats = {
            'date': timezone.localtime().strftime('%Y-%m-%d %H:%M'),
            'modele': self.ia.model,
            'recherche': self.evaluer_recherche(),
            'risque': self.evaluer_risque(),
            'messages': self.evaluer_messages(),
            'affectation': self.evaluer_affectation(),
            'moteur': self.controler_moteur(options['graine']),
            'cache': self.mesurer_cache(),
        }
        resultats['performance'] = self.synthese_performance()
        resultats['duree_totale_s'] = round(time.perf_counter() - debut, 1)

        sortie = Path(options['sortie'])
        sortie.mkdir(parents=True, exist_ok=True)
        horodatage = timezone.localtime().strftime('%Y%m%d_%H%M')
        chemin_json = sortie / f'evaluation_{horodatage}.json'
        chemin_json.write_text(json.dumps(resultats, ensure_ascii=False, indent=2, default=str), encoding='utf-8')
        chemin_html = sortie / f'evaluation_{horodatage}.html'
        chemin_html.write_text(rapport_html(resultats), encoding='utf-8')
        self.stdout.write(self.style.SUCCESS(f"Terminé en {resultats['duree_totale_s']} s"))
        self.stdout.write(f"  {chemin_json}\n  {chemin_html}")

    # ------------------------------------------------------------------
    def appel(self, fonction, executer):
        """Exécute un appel CargoLink AI et enregistre sa durée, ses jetons et un éventuel repli."""
        resultat = executer()
        mesure = dict(self.ia.dernier_appel)
        # Livraison clôturée : le modèle n'est volontairement pas appelé (ni repli, ni temps de réponse)
        mesure['fonction'] = f"{fonction}_non_requis" if mesure.get('non_requis') else fonction
        mesure['repli'] = resultat.get('source') != 'deepseek' and not mesure.get('non_requis')
        self.mesures.append(mesure)
        return resultat

    def charger(self, nom):
        return json.loads((DOSSIER / 'donnees' / nom).read_text(encoding='utf-8'))['cas'][:self.limite]

    # ------------------------------------------------------------------
    # 1. Recherche en langage naturel
    # ------------------------------------------------------------------
    def evaluer_recherche(self):
        self.stdout.write("1/6 Recherche en langage naturel...")
        entrepots = list(Entrepot.objects.all())
        ville_par_entrepot = {e.id: e.ville for e in entrepots}
        cas_resultats, paires_ia, paires_local = [], [], []
        for cas in self.charger('recherche.json'):
            attendues = m.paires_filtres(cas['attendu'], self.aujourd_hui, ville_par_entrepot)
            ia = self.appel('recherche', lambda: self.ia.interpreter_recherche(cas['texte'], entrepots))
            debut = time.perf_counter()
            local = recherche_locale(cas['texte'], entrepots)
            duree_locale = time.perf_counter() - debut
            p_ia = m.paires_filtres(ia['filtres'], self.aujourd_hui, ville_par_entrepot)
            p_local = m.paires_filtres(local['filtres'], self.aujourd_hui, ville_par_entrepot)
            paires_ia.append((attendues, p_ia))
            paires_local.append((attendues, p_local))
            cas_resultats.append({
                'id': cas['id'], 'categorie': cas['categorie'], 'texte': cas['texte'],
                'attendu': sorted(map(list, attendues)), 'ia': sorted(map(list, p_ia)), 'local': sorted(map(list, p_local)),
                'ia_exact': attendues == p_ia, 'local_exact': attendues == p_local,
                'ia_source': ia['source'], 'duree_locale_ms': round(duree_locale * 1000, 3),
            })
        par_categorie = {}
        for c in cas_resultats:
            cat = par_categorie.setdefault(c['categorie'], {'n': 0, 'ia': 0, 'local': 0})
            cat['n'] += 1
            cat['ia'] += c['ia_exact']
            cat['local'] += c['local_exact']
        return {
            'n': len(cas_resultats),
            'ia': m.evaluer_extraction(paires_ia),
            'local': m.evaluer_extraction(paires_local),
            'par_categorie': par_categorie,
            'cas': cas_resultats,
        }

    # ------------------------------------------------------------------
    # 2. Analyse de risque
    # ------------------------------------------------------------------
    def evaluer_risque(self):
        self.stdout.write("2/6 Analyse de risque...")
        attendus, predits_ia, predits_local, cas_resultats = [], [], [], []
        nombres_total, nombres_fondes = 0, 0.0
        for cas in self.charger('risque.json'):
            livraison = self.ref.construire(cas, self.maintenant)
            local = risque_local(livraison)
            ia = self.appel('risque', lambda: self.ia.analyser_risque(livraison))
            contexte = json.dumps(contexte_livraison(livraison), ensure_ascii=False, default=str) + json.dumps(local, ensure_ascii=False)
            for texte in ia['facteurs'] + ia['recommandations'] + [ia['resume']]:
                taux, n = m.nombres_fondes(texte, contexte)
                if n:
                    nombres_total += n
                    nombres_fondes += taux * n
            attendus.append(cas['attendu'])
            predits_ia.append(ia['niveau'])
            predits_local.append(local['niveau'])
            cas_resultats.append({
                'id': cas['id'], 'attendu': cas['attendu'], 'justification': cas['justification'],
                'ia': ia['niveau'], 'ia_score': ia['score'], 'local': local['niveau'], 'local_score': local['score'],
                'ia_facteurs': ia['facteurs'], 'ia_source': ia['source'],
            })
        return {
            'n': len(cas_resultats),
            'ia': m.metriques_classification(attendus, predits_ia, NIVEAUX),
            'local': m.metriques_classification(attendus, predits_local, NIVEAUX),
            'nombres_cites': nombres_total,
            'nombres_fondes': (nombres_fondes / nombres_total) if nombres_total else None,
            'cas': cas_resultats,
        }

    # ------------------------------------------------------------------
    # 3. Message au destinataire
    # ------------------------------------------------------------------
    def controles_message(self, resultat, livraison, langue, objectif):
        texte = resultat['message']
        contexte = json.dumps(contexte_livraison(livraison, pour_destinataire=True), ensure_ascii=False, default=str)
        heures = m.heures_fondees(texte, contexte)
        return {
            'langue': m.detecter_langue(texte) == langue,
            'reference_et_code': livraison.reference in texte and livraison.code_suivi in texte,
            'objectif': m.respecte_objectif(texte, objectif, langue),
            'heures_fondees': heures is None or heures == 1.0,
            'longueur': len(texte) <= 450,
        }

    def evaluer_messages(self):
        self.stdout.write("3/6 Messages au destinataire (45 messages)...")
        donnees = json.loads((DOSSIER / 'donnees' / 'messages.json').read_text(encoding='utf-8'))
        criteres = ['langue', 'reference_et_code', 'objectif', 'heures_fondees', 'longueur']
        totaux = {'ia': {c: 0 for c in criteres}, 'local': {c: 0 for c in criteres}}
        complets = {'ia': 0, 'local': 0}
        cas_resultats, n = [], 0
        for cas in donnees['cas'][:self.limite]:
            livraison = self.ref.construire(cas, self.maintenant)
            for langue in donnees['langues']:
                n += 1
                ia = self.appel('message', lambda: self.ia.rediger_message(livraison, langue, cas['objectif']))
                local = message_local(livraison, langue, cas['objectif'])
                c_ia = self.controles_message(ia, livraison, langue, cas['objectif'])
                c_local = self.controles_message(local, livraison, langue, cas['objectif'])
                for c in criteres:
                    totaux['ia'][c] += c_ia[c]
                    totaux['local'][c] += c_local[c]
                complets['ia'] += all(c_ia.values())
                complets['local'] += all(c_local.values())
                cas_resultats.append({
                    'id': cas['id'], 'langue': langue, 'objectif': cas['objectif'], 'controles_ia': c_ia,
                    'controles_local': c_local, 'message_ia': ia['message'], 'longueur_ia': len(ia['message']),
                    'ia_source': ia['source'],
                })
        return {
            'n': n,
            'taux_ia': {c: totaux['ia'][c] / n for c in criteres},
            'taux_local': {c: totaux['local'][c] / n for c in criteres},
            'complets_ia': complets['ia'] / n,
            'complets_local': complets['local'] / n,
            'longueur_mediane_ia': statistics.median(c['longueur_ia'] for c in cas_resultats),
            'cas': cas_resultats,
        }

    # ------------------------------------------------------------------
    # 4. Explication de l'affectation intelligente
    # ------------------------------------------------------------------
    def evaluer_affectation(self):
        self.stdout.write("4/6 Explications d'affectation...")
        moteur = MoteurAffectation()
        cas_resultats = []
        for cas in self.charger('affectation.json'):
            debut = self.maintenant + timedelta(hours=cas['depart_h'])
            fin = debut + timedelta(hours=cas['duree_h'])
            classement = moteur.recommander(
                poids_kg=cas['poids'], nb_palettes=cas['palettes'], type_marchandise=cas['marchandise'], debut=debut, fin=fin,
            )
            if not classement['success']:
                cas_resultats.append({'id': cas['id'], 'sans_solution': True})
                continue
            contexte = {'marchandise': cas['marchandise'], 'poids_kg': cas['poids'], 'nb_palettes': cas['palettes'],
                        'depart': timezone.localtime(debut).strftime('%d/%m/%Y %H:%M'),
                        'echeance': timezone.localtime(fin).strftime('%d/%m/%Y %H:%M')}
            ia = self.appel('explication', lambda: self.ia.expliquer_affectation(classement, contexte))
            premier = classement['recommandations'][0]
            texte = ' '.join([ia['synthese'], ia.get('alternative') or ''] + ia['vigilance'])
            nom_chauffeur = premier['chauffeur_label'].split()[-1]
            plaque, _, vehicule = premier['camion_label'].partition(' • ')
            modele = vehicule.split()[-1] if vehicule else plaque
            # Conversions d'unités légitimes (kg -> t) ajoutées aux données de référence
            conversions = {'poids_t': cas['poids'] / 1000, 'poids_t_arrondi': round(cas['poids'] / 1000)}
            taux, nombres = m.nombres_fondes(texte, json.dumps([classement, contexte, conversions], ensure_ascii=False, default=str))
            cas_resultats.append({
                'id': cas['id'], 'sans_solution': False,
                'premier_choix': f"{premier['chauffeur_label']} + {premier['camion_label']}",
                'consistant': nom_chauffeur in ia['synthese'] and (plaque in ia['synthese'] or modele in ia['synthese']),
                'nombres_cites': nombres, 'nombres_fondes': taux,
                'alertes_attendues': bool(premier['points_attention']),
                'alertes_donnees': bool(ia['vigilance']),
                'synthese': ia['synthese'], 'ia_source': ia['source'],
            })
        avec_solution = [c for c in cas_resultats if not c['sans_solution']]
        nombres = sum(c['nombres_cites'] for c in avec_solution)
        fondes = sum((c['nombres_fondes'] or 0) * c['nombres_cites'] for c in avec_solution)
        alertes_attendues = [c for c in avec_solution if c['alertes_attendues']]
        return {
            'n': len(cas_resultats),
            'avec_solution': len(avec_solution),
            'consistance': sum(c['consistant'] for c in avec_solution) / len(avec_solution) if avec_solution else None,
            'nombres_cites': nombres,
            'nombres_fondes': fondes / nombres if nombres else None,
            'alertes_couvertes': (sum(c['alertes_donnees'] for c in alertes_attendues) / len(alertes_attendues)) if alertes_attendues else None,
            'cas_avec_alertes': len(alertes_attendues),
            'cas': cas_resultats,
        }

    # ------------------------------------------------------------------
    # 5. Contrôle du moteur d'affectation (sans IA)
    # ------------------------------------------------------------------
    def controler_moteur(self, graine):
        self.stdout.write("5/6 Contrôle du moteur d'affectation (200 cas aléatoires)...")
        from camions.models import Camion
        from chauffeurs.models import Chauffeur

        hasard = random.Random(graine)
        moteur = MoteurAffectation()
        propositions = violations = sans_solution = 0
        durees = []
        for _ in range(200 if self.limite is None else 10):
            poids, palettes = hasard.randint(300, 30000), hasard.randint(1, 40)
            marchandise = hasard.choice(['STANDARD', 'STANDARD', 'FRIGORIFIQUE', 'ADR', 'GROS_VOLUME', 'PALETTES'])
            debut = self.maintenant + timedelta(hours=hasard.randint(1, 200))
            fin = debut + timedelta(hours=hasard.randint(1, 8))
            t = time.perf_counter()
            resultat = moteur.recommander(poids_kg=poids, nb_palettes=palettes, type_marchandise=marchandise, debut=debut, fin=fin)
            durees.append(time.perf_counter() - t)
            if not resultat['success']:
                sans_solution += 1
                continue
            for p in resultat['recommandations']:
                propositions += 1
                camion, chauffeur = Camion.objects.get(pk=p['camion_id']), Chauffeur.objects.get(pk=p['chauffeur_id'])
                erreurs = {}
                erreurs.update(regles.verifier_camion(camion, poids, palettes, marchandise))
                erreurs.update(regles.verifier_chauffeur(chauffeur, camion, marchandise, fin))
                erreurs.update(regles.conflits_planning(debut, fin, camion, chauffeur))
                violations += bool(erreurs)
        return {
            'cas': 200 if self.limite is None else 10, 'propositions': propositions, 'violations': violations,
            'taux_violation': violations / propositions if propositions else 0.0,
            'sans_solution': sans_solution,
            'duree_mediane_ms': round(statistics.median(durees) * 1000, 1),
            'duree_p95_ms': round(m.percentile(durees, 95) * 1000, 1),
        }

    # ------------------------------------------------------------------
    # 6. Cache et temps de réponse
    # ------------------------------------------------------------------
    def mesurer_cache(self):
        self.stdout.write("6/6 Effet du cache...")
        from django.core.cache import cache
        from livraisons.models import Livraison

        cache.clear()
        ia_cache = DeepSeekLivraisonAI(api_key=self.ia.api_key, cache_secondes=600)
        froids, chauds = [], []
        for livraison in Livraison.objects.filter(numero_bl__startswith='EVAL-S').order_by('id')[:8]:
            ia_cache.analyser_risque(livraison)
            if not ia_cache.dernier_appel.get('cache'):
                froids.append(ia_cache.dernier_appel['duree'])
            ia_cache.analyser_risque(livraison)
            if ia_cache.dernier_appel.get('cache'):
                chauds.append(ia_cache.dernier_appel['duree'])
        return {
            'n': len(froids),
            'sans_cache_mediane_s': statistics.median(froids) if froids else None,
            'avec_cache_mediane_ms': statistics.median(chauds) * 1000 if chauds else None,
            'succes_cache': len(chauds),
        }

    def synthese_performance(self):
        par_fonction = {}
        for nom in ('recherche', 'risque', 'message', 'explication'):
            appels = [x for x in self.mesures if x['fonction'] == nom]
            durees = [x['duree'] for x in appels if not x.get('erreur')]
            par_fonction[nom] = {
                'appels': len(appels),
                'mediane_s': statistics.median(durees) if durees else None,
                'p95_s': m.percentile(durees, 95),
                'max_s': max(durees) if durees else None,
                'timeouts': sum(1 for x in appels if x.get('erreur') == 'timeout'),
                'erreurs': sum(1 for x in appels if x.get('erreur')),
                'replis': sum(1 for x in appels if x['repli']),
                'jetons_moyens': statistics.mean(x['jetons'] for x in appels) if appels else 0,
            }
        toutes = [x['duree'] for x in self.mesures if not x.get('erreur')]
        return {
            'appels': len(self.mesures),
            'mediane_s': statistics.median(toutes) if toutes else None,
            'p95_s': m.percentile(toutes, 95),
            'jetons_total': sum(x['jetons'] for x in self.mesures),
            'par_fonction': par_fonction,
        }


# ----------------------------------------------------------------------
# Rapport HTML (lisible directement dans un navigateur)
# ----------------------------------------------------------------------
def pct(valeur):
    return '—' if valeur is None else f"{valeur * 100:.1f} %"


def rapport_html(r):
    def ligne(*cellules, entete=False):
        balise = 'th' if entete else 'td'
        return '<tr>' + ''.join(f'<{balise}>{escape(str(c))}</{balise}>' for c in cellules) + '</tr>'

    rech, risque, msg, aff, mot, perf, cache = (r[k] for k in ('recherche', 'risque', 'messages', 'affectation', 'moteur', 'performance', 'cache'))
    html = [
        '<!doctype html><html lang="fr"><head><meta charset="utf-8"><title>Évaluation CargoLink AI</title>',
        '<style>body{font-family:Segoe UI,Arial,sans-serif;max-width:900px;margin:2rem auto;padding:0 1rem;color:#1a1a1a}'
        'table{border-collapse:collapse;width:100%;margin:.5rem 0 1.5rem}th,td{border-bottom:1px solid #ddd;padding:4px 8px;text-align:left}'
        'th{border-bottom:2px solid #333}h2{color:#1f3a93}</style></head><body>',
        f"<h1>Évaluation CargoLink AI</h1><p>Date : {escape(r['date'])} — modèle : {escape(r['modele'])} — durée : {r['duree_totale_s']} s</p>",
        f"<h2>1. Recherche en langage naturel ({rech['n']} phrases)</h2><table>",
        ligne('Moteur', 'Précision', 'Rappel', 'F1', 'Correspondance exacte', entete=True),
        ligne('CargoLink AI', pct(rech['ia']['precision']), pct(rech['ia']['rappel']), pct(rech['ia']['f1']), pct(rech['ia']['exact'])),
        ligne('Moteur local', pct(rech['local']['precision']), pct(rech['local']['rappel']), pct(rech['local']['f1']), pct(rech['local']['exact'])),
        '</table>',
        f"<h2>2. Analyse de risque ({risque['n']} situations)</h2><table>",
        ligne('Moteur', 'Exactitude', 'Macro-F1', entete=True),
        ligne('CargoLink AI', pct(risque['ia']['exactitude']), pct(risque['ia']['macro_f1'])),
        ligne('Moteur local', pct(risque['local']['exactitude']), pct(risque['local']['macro_f1'])),
        '</table><table>', ligne('Attendu \\ Prédit (CargoLink AI)', *NIVEAUX, entete=True),
    ]
    for a in NIVEAUX:
        html.append(ligne(a, *(risque['ia']['matrice'][a][p] for p in NIVEAUX)))
    html += [
        f"</table><p>Nombres cités fondés sur les données : {pct(risque['nombres_fondes'])} ({risque['nombres_cites']} nombres).</p>",
        f"<h2>3. Messages au destinataire ({msg['n']} messages)</h2><table>",
        ligne('Critère', 'CargoLink AI', 'Modèle local', entete=True),
    ]
    for critere in msg['taux_ia']:
        html.append(ligne(critere, pct(msg['taux_ia'][critere]), pct(msg['taux_local'][critere])))
    html += [
        ligne('Tous les critères', pct(msg['complets_ia']), pct(msg['complets_local'])), '</table>',
        f"<h2>4. Explication de l'affectation ({aff['avec_solution']} cas)</h2><table>",
        ligne('Mesure', 'Résultat', entete=True),
        ligne('Premier choix correctement nommé', pct(aff['consistance'])),
        ligne('Nombres cités fondés', f"{pct(aff['nombres_fondes'])} ({aff['nombres_cites']} nombres)"),
        ligne('Alertes reprises quand il y en a', f"{pct(aff['alertes_couvertes'])} ({aff['cas_avec_alertes']} cas)"),
        '</table>',
        f"<h2>5. Moteur d'affectation (sans IA)</h2><p>{mot['cas']} cas aléatoires, {mot['propositions']} propositions, "
        f"{mot['violations']} violation(s) de règle ({pct(mot['taux_violation'])}), {mot['sans_solution']} cas sans solution, "
        f"{mot['duree_mediane_ms']} ms par calcul (médiane).</p>",
        f"<h2>6. Temps de réponse ({perf['appels']} appels)</h2><table>",
        ligne('Fonction', 'Appels', 'Médiane (s)', 'P95 (s)', 'Max (s)', 'Timeouts', 'Replis', 'Jetons moyens', entete=True),
    ]
    for nom, p in perf['par_fonction'].items():
        fmt = lambda v: '—' if v is None else f"{v:.2f}"
        html.append(ligne(nom, p['appels'], fmt(p['mediane_s']), fmt(p['p95_s']), fmt(p['max_s']), p['timeouts'], p['replis'], round(p['jetons_moyens'])))
    html += [
        f"</table><p>Cache : {fmt(cache['sans_cache_mediane_s'])} s sans cache, "
        f"{'—' if cache['avec_cache_mediane_ms'] is None else f'{cache['avec_cache_mediane_ms']:.2f}'} ms avec cache (médianes, {cache['n']} analyses).</p>",
        '</body></html>',
    ]
    return '\n'.join(html)
