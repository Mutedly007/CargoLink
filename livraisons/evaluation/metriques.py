"""
Fonctions de calcul des métriques de l'évaluation CargoLink AI (indépendantes de Django).
"""
import math
import re
from datetime import timedelta

from livraisons.geo import normaliser_ville


# ------------------------------------------------------------------
# Précision / rappel / F1
# ------------------------------------------------------------------
def prf(vrais_positifs, faux_positifs, faux_negatifs):
    precision = vrais_positifs / (vrais_positifs + faux_positifs) if (vrais_positifs + faux_positifs) else 1.0
    rappel = vrais_positifs / (vrais_positifs + faux_negatifs) if (vrais_positifs + faux_negatifs) else 1.0
    f1 = 2 * precision * rappel / (precision + rappel) if (precision + rappel) else 0.0
    return {'precision': precision, 'rappel': rappel, 'f1': f1}


def resoudre_date(valeur, aujourd_hui):
    """Remplace les jetons relatifs (TODAY, WEEK_START...) par une date ISO."""
    if not valeur:
        return None
    lundi = aujourd_hui - timedelta(days=aujourd_hui.weekday())
    jetons = {
        'TODAY': aujourd_hui,
        'YESTERDAY': aujourd_hui - timedelta(days=1),
        'TOMORROW': aujourd_hui + timedelta(days=1),
        'WEEK_START': lundi,
        'WEEK_END': lundi + timedelta(days=6),
        'NEXT_WEEK_START': lundi + timedelta(days=7),
        'NEXT_WEEK_END': lundi + timedelta(days=13),
    }
    return jetons[valeur].isoformat() if valeur in jetons else str(valeur)[:10]


def paires_filtres(filtres, aujourd_hui, ville_par_entrepot):
    """
    Transforme un jeu de filtres en ensemble de paires « champ = valeur » comparables.
    Un entrepôt et une ville désignent tous deux un lieu : ils sont ramenés au même champ.
    """
    paires = set()
    for statut in filtres.get('statut') or []:
        paires.add(('statut', statut))
    lieu = filtres.get('ville')
    if not lieu and filtres.get('entrepot'):
        lieu = ville_par_entrepot.get(int(filtres['entrepot']))
    if lieu:
        paires.add(('lieu', normaliser_ville(lieu)))
    for champ in ('date_du', 'date_au'):
        if filtres.get(champ):
            paires.add((champ, resoudre_date(filtres[champ], aujourd_hui)))
    for champ in ('priorite', 'type_marchandise', 'type_livraison'):
        if filtres.get(champ):
            paires.add((champ, filtres[champ]))
    for champ in ('en_retard', 'avec_incident'):
        if filtres.get(champ) is True:
            paires.add((champ, True))
    if filtres.get('q'):
        paires.add(('q', normaliser_ville(filtres['q'])))
    return paires


def evaluer_extraction(resultats):
    """
    resultats : liste de (paires_attendues, paires_predites).
    Retourne les métriques micro (toutes paires confondues), par champ, et le taux de correspondance exacte.
    """
    tp = fp = fn = 0
    exact = 0
    par_champ = {}
    for attendues, predites in resultats:
        tp += len(attendues & predites)
        fp += len(predites - attendues)
        fn += len(attendues - predites)
        exact += attendues == predites
        champs = {p[0] for p in attendues | predites}
        for champ in champs:
            a = {p for p in attendues if p[0] == champ}
            p_ = {p for p in predites if p[0] == champ}
            compte = par_champ.setdefault(champ, [0, 0, 0])
            compte[0] += len(a & p_)
            compte[1] += len(p_ - a)
            compte[2] += len(a - p_)
    resume = prf(tp, fp, fn)
    resume['exact'] = exact / len(resultats) if resultats else 0.0
    resume['tp'], resume['fp'], resume['fn'] = tp, fp, fn
    resume['par_champ'] = {champ: dict(prf(*c), support=c[0] + c[2]) for champ, c in sorted(par_champ.items())}
    return resume


# ------------------------------------------------------------------
# Classification multi-classes
# ------------------------------------------------------------------
def matrice_confusion(attendus, predits, classes):
    matrice = {a: {p: 0 for p in classes} for a in classes}
    for a, p in zip(attendus, predits):
        matrice[a][p] += 1
    return matrice


def metriques_classification(attendus, predits, classes):
    matrice = matrice_confusion(attendus, predits, classes)
    par_classe = {}
    for c in classes:
        tp = matrice[c][c]
        fp = sum(matrice[a][c] for a in classes if a != c)
        fn = sum(matrice[c][p] for p in classes if p != c)
        par_classe[c] = dict(prf(tp, fp, fn), support=sum(matrice[c].values()))
    total = len(attendus)
    return {
        'matrice': matrice,
        'exactitude': sum(matrice[c][c] for c in classes) / total if total else 0.0,
        'macro_f1': sum(par_classe[c]['f1'] for c in classes) / len(classes),
        'par_classe': par_classe,
    }


# ------------------------------------------------------------------
# Contrôles de texte généré
# ------------------------------------------------------------------
MOTS_LANGUE = {
    'fr': {'votre', 'vos', 'nous', 'livraison', 'est', 'les', 'des', 'merci', 'bonjour', 'prévue', 'arrivée', 'cordialement'},
    'en': {'your', 'we', 'delivery', 'is', 'the', 'thank', 'hello', 'expected', 'arrival', 'shipment', 'regards'},
}


def detecter_langue(texte):
    lettres = [c for c in texte if c.isalpha()]
    if not lettres:
        return None
    arabe = sum(1 for c in lettres if '؀' <= c <= 'ۿ')
    if arabe / len(lettres) > 0.4:
        return 'ar'
    mots = set(re.findall(r"[a-zàâçéèêëîïôûùüÿœ']+", texte.lower()))
    score_fr = len(mots & MOTS_LANGUE['fr'])
    score_en = len(mots & MOTS_LANGUE['en'])
    return 'fr' if score_fr >= score_en else 'en'


MOTS_OBJECTIF = {
    'information': {'fr': ['prévu', 'en route', 'estimé', 'arriv', 'en cours', 'chemin'],
                    'en': ['expected', 'on its way', 'estimated', 'arriv', 'on the way', 'en route'],
                    'ar': ['متوقع', 'الطريق', 'وصول', 'يصل']},
    'retard': {'fr': ['retard'], 'en': ['delay', 'late'], 'ar': ['تأخ', 'تأخير']},
    'livree': {'fr': ['livré', 'livree', 'livrée', 'réceptionn'], 'en': ['delivered'], 'ar': ['تسليم', 'تم توصيل', 'سلمت', 'تم التسليم']},
}


def respecte_objectif(texte, objectif, langue):
    bas = texte.lower()
    return any(mot in bas for mot in MOTS_OBJECTIF[objectif][langue])


def heures_citees(texte):
    return re.findall(r'\b([01]?\d|2[0-3])[:hH]([0-5]\d)\b', texte)


def heures_fondees(texte, contexte_texte):
    """Part des heures citées (HH:MM) présentes dans les données transmises. None si aucune heure citée."""
    heures = heures_citees(texte)
    if not heures:
        return None
    presentes = sum(1 for h, m in heures if f"{int(h):02d}:{m}" in contexte_texte)
    return presentes / len(heures)


def nombres_fondes(texte, contexte_texte):
    """
    Part des nombres cités (hors petits entiers <= 3) qui apparaissent dans les données transmises.
    Mesure simple de l'invention de chiffres (hallucination numérique).
    """
    nombres = [n.replace(',', '.').replace(' ', '') for n in re.findall(r'\d+(?:[.,]\d+)?', texte)]
    nombres = [n for n in nombres if not (n.isdigit() and int(n) <= 3)]
    if not nombres:
        return None, 0
    base = contexte_texte.replace(' ', '')
    presents = 0
    for n in nombres:
        variantes = {n, n.rstrip('0').rstrip('.') if '.' in n else n}
        if n.endswith('.0'):
            variantes.add(n[:-2])
        presents += any(v in base for v in variantes)
    return presents / len(nombres), len(nombres)


# ------------------------------------------------------------------
# Temps de réponse
# ------------------------------------------------------------------
def percentile(valeurs, p):
    if not valeurs:
        return None
    valeurs = sorted(valeurs)
    rang = (len(valeurs) - 1) * p / 100
    bas, haut = math.floor(rang), math.ceil(rang)
    return valeurs[bas] + (valeurs[haut] - valeurs[bas]) * (rang - bas)
