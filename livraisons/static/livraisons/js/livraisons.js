/* ==============================================================================
   CARGOLINK - MODULE LIVRAISONS (EYA) : interactions côté navigateur
   Recherche IA, estimation de trajet, affectation intelligente, analyse de risque,
   message destinataire, signature de preuve de livraison.
   Les réponses IA sont insérées avec textContent (jamais innerHTML) : aucun HTML
   provenant d'un modèle n'est interprété par le navigateur.
   ============================================================================== */
(function () {
    'use strict';

    function csrfToken() {
        const champ = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return champ ? champ.value : '';
    }

    async function postJSON(url, donnees) {
        const corps = new FormData();
        Object.entries(donnees).forEach(([cle, valeur]) => {
            if (valeur !== undefined && valeur !== null) corps.append(cle, valeur);
        });
        const reponse = await fetch(url, {
            method: 'POST',
            headers: { 'X-CSRFToken': csrfToken(), 'X-Requested-With': 'XMLHttpRequest' },
            body: corps,
            credentials: 'same-origin',
        });
        return reponse.json();
    }

    function element(tag, classe, texte) {
        const el = document.createElement(tag);
        if (classe) el.className = classe;
        if (texte !== undefined) el.textContent = texte;
        return el;
    }

    function remplirListe(ul, items, vide) {
        ul.replaceChildren();
        (items && items.length ? items : [vide]).forEach((t) => ul.appendChild(element('li', '', t)));
    }

    function occupe(bouton, actif) {
        if (!bouton) return;
        bouton.disabled = actif;
        bouton.dataset.label = bouton.dataset.label || bouton.innerHTML;
        if (actif) bouton.textContent = 'Analyse en cours…';
        else bouton.innerHTML = bouton.dataset.label;
    }

    /* --------------------------------------------------------------
       Recherche en langage naturel (tableau de bord)
       -------------------------------------------------------------- */
    const formIA = document.getElementById('aiSearchForm');
    if (formIA) {
        formIA.addEventListener('submit', async (e) => {
            e.preventDefault();
            const texte = document.getElementById('aiSearchInput').value.trim();
            if (!texte) return;
            const bouton = formIA.querySelector('button');
            occupe(bouton, true);
            try {
                const res = await postJSON(formIA.dataset.url, { texte });
                if (res.success) window.location.href = res.url;
                else alert(res.message || 'Recherche impossible.');
            } catch (err) {
                alert('Service de recherche indisponible.');
            } finally {
                occupe(bouton, false);
            }
        });
    }

    /* --------------------------------------------------------------
       Formulaire de livraison
       -------------------------------------------------------------- */
    const form = document.getElementById('livraisonForm');
    if (form) {
        const champ = (nom) => form.querySelector(`[name="${nom}"]`);
        const typeChoisi = () => (form.querySelector('input[name="type_livraison"]:checked') || {}).value;

        function basculerType() {
            const inter = typeChoisi() === 'INTER_ENTREPOT';
            form.querySelectorAll('.bloc-inter').forEach((b) => { b.hidden = !inter; });
            form.querySelectorAll('.bloc-client').forEach((b) => { b.hidden = inter; });
            estimer();
        }

        // Estimation distance / durée / CO2 et échéance suggérée
        const zoneEstimation = document.getElementById('estimation');
        const boutonEta = document.getElementById('btnAppliquerEta');
        let echeanceSuggeree = null;

        async function estimer() {
            const params = new URLSearchParams({
                origine: champ('entrepot_origine').value || '',
                destination: typeChoisi() === 'INTER_ENTREPOT' ? (champ('entrepot_destination').value || '') : '',
                ville: typeChoisi() === 'CLIENT' ? (champ('ville_livraison').value || '') : '',
                camion: champ('camion').value || '',
                depart: champ('date_depart_prevue').value || '',
            });
            if (!params.get('origine')) { zoneEstimation.hidden = true; return; }
            try {
                const res = await (await fetch(`${form.dataset.urlEstimation}?${params}`)).json();
                if (!res.success) { zoneEstimation.hidden = true; return; }
                const h = Math.floor(res.duree_minutes / 60);
                const m = String(res.duree_minutes % 60).padStart(2, '0');
                zoneEstimation.querySelector('[data-est="distance"]').textContent = `${res.distance_km} km`;
                zoneEstimation.querySelector('[data-est="duree"]').textContent = h ? `${h} h ${m}` : `${res.duree_minutes} min`;
                zoneEstimation.querySelector('[data-est="co2"]').textContent = `${res.co2_kg} kg`;
                echeanceSuggeree = res.echeance_suggeree;
                boutonEta.hidden = !echeanceSuggeree;
                zoneEstimation.hidden = false;
            } catch (err) {
                zoneEstimation.hidden = true;
            }
        }
        if (boutonEta) {
            boutonEta.addEventListener('click', () => {
                if (echeanceSuggeree) champ('date_livraison_prevue').value = echeanceSuggeree;
            });
        }

        // Créneaux ouverts de l'entrepôt sélectionné (module Créneaux)
        async function chargerCreneaux(nomChampEntrepot, nomChampCreneau, typeOperation) {
            const entrepot = champ(nomChampEntrepot).value;
            const select = champ(nomChampCreneau);
            const actuel = select.value;
            select.replaceChildren(element('option', '', '— Aucun créneau (à réserver plus tard) —'));
            select.firstChild.value = '';
            if (!entrepot) return;
            const res = await (await fetch(`${form.dataset.urlCreneaux}?entrepot=${entrepot}&type=${typeOperation}`)).json();
            res.creneaux.forEach((c) => {
                const opt = element('option', '', c.label);
                opt.value = c.id;
                if (String(c.id) === actuel) opt.selected = true;
                select.appendChild(opt);
            });
        }

        form.querySelectorAll('input[name="type_livraison"]').forEach((r) => r.addEventListener('change', basculerType));
        champ('entrepot_origine').addEventListener('change', () => {
            chargerCreneaux('entrepot_origine', 'creneau_chargement', 'CHARGEMENT');
            estimer();
        });
        champ('entrepot_destination').addEventListener('change', () => {
            chargerCreneaux('entrepot_destination', 'creneau_dechargement', 'DECHARGEMENT');
            estimer();
        });
        ['ville_livraison', 'camion', 'date_depart_prevue'].forEach((n) => champ(n).addEventListener('change', estimer));
        basculerType();

        // Affectation intelligente camion + chauffeur
        const panneau = document.getElementById('assignPanel');
        const liste = document.getElementById('assignList');
        const synthese = document.getElementById('assignSynthese');
        const exclusions = document.getElementById('assignExclusions');

        function choisir(proposition) {
            champ('camion').value = proposition.camion_id;
            champ('chauffeur').value = proposition.chauffeur_id;
            estimer();
            liste.querySelectorAll('.liv-assign-item').forEach((i) => i.classList.remove('best'));
        }

        async function affecter(bouton) {
            const donnees = {
                ia: bouton.dataset.ia,
                livraison_pk: form.dataset.livraisonPk,
                type_livraison: typeChoisi(),
            };
            ['entrepot_origine', 'entrepot_destination', 'ville_livraison', 'date_depart_prevue', 'date_livraison_prevue',
             'poids_kg', 'nb_palettes', 'type_marchandise', 'priorite'].forEach((n) => { donnees[n] = champ(n).value; });
            occupe(bouton, true);
            try {
                const res = await postJSON(form.dataset.urlAssign, donnees);
                panneau.hidden = false;
                liste.replaceChildren();
                synthese.replaceChildren();
                if (!res.success && !res.exclusions_camions) {
                    synthese.textContent = res.message;
                    exclusions.hidden = true;
                    return;
                }
                const exp = res.explication || {};
                if (exp.synthese) {
                    const source = element('span', 'liv-source', exp.source === 'deepseek' ? 'CargoLink AI' : 'Moteur local');
                    synthese.append(source, ' ', exp.synthese);
                    if (exp.alternative) synthese.append(element('div', 'liv-small liv-muted', exp.alternative));
                    (exp.vigilance || []).forEach((v) => synthese.append(element('div', 'liv-small liv-warning-text', '• ' + v)));
                } else if (res.message) {
                    synthese.textContent = res.message;
                }
                (res.recommandations || []).forEach((p, index) => {
                    const item = element('div', 'liv-assign-item' + (index === 0 ? ' best' : ''));
                    const score = element('div', 'liv-score');
                    score.style.setProperty('--score', p.score);
                    score.appendChild(element('span', '', p.score));
                    const corps = element('div');
                    corps.appendChild(element('h4', '', `${p.chauffeur_label} + ${p.camion_label}`));
                    corps.appendChild(element('div', 'liv-small liv-muted',
                        `${p.camion_type} • Permis ${p.chauffeur_permis}` + (p.remplissage_pct !== null ? ` • Remplissage ${p.remplissage_pct} %` : '')));
                    const tags = element('div', 'liv-tags');
                    p.points_forts.forEach((t) => tags.appendChild(element('span', 'liv-tag plus', t)));
                    p.points_attention.forEach((t) => tags.appendChild(element('span', 'liv-tag moins', t)));
                    corps.appendChild(tags);
                    const choix = element('button', 'btn btn-outline btn-sm', 'Utiliser');
                    choix.type = 'button';
                    choix.addEventListener('click', () => { choisir(p); item.classList.add('best'); });
                    item.append(score, corps, choix);
                    liste.appendChild(item);
                });
                const exclus = [...(res.exclusions_camions || []), ...(res.exclusions_chauffeurs || [])];
                exclusions.hidden = exclus.length === 0;
                if (exclus.length) {
                    exclusions.querySelector('summary').textContent = `${exclus.length} ressource(s) écartée(s) par les règles`;
                    remplirListe(exclusions.querySelector('ul'), exclus.map((x) => `${x.label} : ${x.motif}`), '');
                }
            } catch (err) {
                panneau.hidden = false;
                synthese.textContent = "Affectation intelligente indisponible pour le moment.";
            } finally {
                occupe(bouton, false);
            }
        }
        ['btnSmartAssign', 'btnSmartAssignIA'].forEach((id) => {
            const b = document.getElementById(id);
            if (b) b.addEventListener('click', () => affecter(b));
        });
    }

    /* --------------------------------------------------------------
       Détail : analyse de risque IA
       -------------------------------------------------------------- */
    const panneauRisque = document.getElementById('risquePanel');
    const boutonRisque = document.getElementById('btnAnalyseIA');
    if (panneauRisque && boutonRisque) {
        boutonRisque.addEventListener('click', async () => {
            occupe(boutonRisque, true);
            try {
                const r = await postJSON(panneauRisque.dataset.url, {});
                const bloc = panneauRisque.querySelector('[data-role="risque"]');
                bloc.className = `liv-risk ${r.niveau}`;
                bloc.querySelector('.liv-risk-gauge').style.setProperty('--score', r.score);
                bloc.querySelector('[data-role="score"]').textContent = r.score;
                bloc.querySelector('[data-role="niveau"]').textContent = `Risque ${r.niveau === 'eleve' ? 'élevé' : r.niveau}`;
                bloc.querySelector('[data-role="resume"]').textContent = r.resume;
                remplirListe(panneauRisque.querySelector('[data-role="facteurs"]'), r.facteurs, 'Aucun facteur de risque détecté.');
                remplirListe(panneauRisque.querySelector('[data-role="recommandations"]'), r.recommandations, 'Aucune action requise.');
                panneauRisque.querySelector('[data-role="source"]').textContent = r.source === 'deepseek' ? 'CargoLink AI' : 'Moteur local';
            } catch (err) {
                alert("Analyse indisponible pour le moment.");
            } finally {
                occupe(boutonRisque, false);
            }
        });
    }

    /* --------------------------------------------------------------
       Détail : message au destinataire (FR / AR / EN)
       -------------------------------------------------------------- */
    const panneauMessage = document.getElementById('messagePanel');
    const boutonMessage = document.getElementById('btnMessageIA');
    if (panneauMessage && boutonMessage) {
        boutonMessage.addEventListener('click', async () => {
            occupe(boutonMessage, true);
            try {
                const langue = document.getElementById('msgLangue').value;
                const r = await postJSON(panneauMessage.dataset.url, {
                    langue, objectif: document.getElementById('msgObjectif').value,
                });
                const texte = document.getElementById('msgTexte');
                document.getElementById('msgObjet').value = r.objet;
                texte.value = r.message;
                texte.dir = langue === 'ar' ? 'rtl' : 'ltr';
                document.getElementById('msgSource').textContent = r.source === 'deepseek' ? 'Rédigé par CargoLink AI' : 'Modèle local';
                document.getElementById('msgResultat').hidden = false;
            } catch (err) {
                alert("Rédaction indisponible pour le moment.");
            } finally {
                occupe(boutonMessage, false);
            }
        });
    }

    // Boutons « Copier »
    document.querySelectorAll('[data-copy]').forEach((bouton) => {
        bouton.addEventListener('click', async () => {
            const cible = document.querySelector(bouton.dataset.copy);
            if (!cible) return;
            try {
                await navigator.clipboard.writeText(cible.value);
            } catch (err) {
                cible.select();
                document.execCommand('copy');
            }
            const initial = bouton.innerHTML;
            bouton.textContent = 'Copié';
            setTimeout(() => { bouton.innerHTML = initial; }, 1500);
        });
    });

    /* --------------------------------------------------------------
       Preuve de livraison : signature au doigt (canvas)
       -------------------------------------------------------------- */
    const canvas = document.getElementById('signaturePad');
    if (canvas) {
        const ctx = canvas.getContext('2d');
        const indice = document.getElementById('signatureHint');
        let dessine = false;
        let enCours = false;

        function redimensionner() {
            const ratio = window.devicePixelRatio || 1;
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width * ratio;
            canvas.height = rect.height * ratio;
            ctx.scale(ratio, ratio);
            ctx.lineWidth = 2.4;
            ctx.lineCap = 'round';
            ctx.lineJoin = 'round';
            ctx.strokeStyle = '#0f172a';
        }
        function position(e) {
            const rect = canvas.getBoundingClientRect();
            return { x: e.clientX - rect.left, y: e.clientY - rect.top };
        }
        canvas.addEventListener('pointerdown', (e) => {
            enCours = true;
            canvas.setPointerCapture(e.pointerId);
            const p = position(e);
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
        });
        canvas.addEventListener('pointermove', (e) => {
            if (!enCours) return;
            const p = position(e);
            ctx.lineTo(p.x, p.y);
            ctx.stroke();
            dessine = true;
            indice.hidden = true;
        });
        ['pointerup', 'pointerleave', 'pointercancel'].forEach((ev) => canvas.addEventListener(ev, () => { enCours = false; }));

        document.getElementById('btnEffacerSignature').addEventListener('click', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            dessine = false;
            indice.hidden = false;
        });
        document.getElementById('podForm').addEventListener('submit', () => {
            document.getElementById('id_signature_data').value = dessine ? canvas.toDataURL('image/png') : '';
        });
        redimensionner();
    }
})();
