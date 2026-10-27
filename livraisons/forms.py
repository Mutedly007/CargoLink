from django import forms
from django.db.models import Q

from camions.models import Camion
from chauffeurs.models import Chauffeur
from creneaux.models import Creneau
from entrepots.models import Entrepot

from . import geo, regles
from .models import IncidentLivraison, Livraison

FORMAT_DATETIME = '%Y-%m-%dT%H:%M'
TAILLE_MAX_IMAGE = 5 * 1024 * 1024


class CamionChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, camion):
        return (
            f"{camion.immatriculation} • {camion.get_type_camion_display()} • "
            f"{camion.capacite_tonnage:g} t / {camion.capacite_palettes} pal. • {camion.get_etat_display()}"
        )


class ChauffeurChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, chauffeur):
        return f"{chauffeur.nom_complet} • Permis {chauffeur.categorie_permis} • {chauffeur.get_statut_display()}"


class CreneauChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, creneau):
        return (
            f"{creneau.reference} • {creneau.quai.numero} • {creneau.date_creneau:%d/%m} "
            f"{creneau.heure_debut:%H:%M}-{creneau.heure_fin:%H:%M} ({creneau.get_statut_display()})"
        )


def _datetime_widget():
    return forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-input'}, format=FORMAT_DATETIME)


class LivraisonForm(forms.ModelForm):
    """
    Création / modification d'une livraison (planificateur).
    Les listes de camions, chauffeurs et créneaux ne proposent que les ressources utilisables ;
    les règles R1 à R10 sont ensuite vérifiées par Livraison.clean().
    """
    date_depart_prevue = forms.DateTimeField(
        label="Départ prévu", widget=_datetime_widget(), input_formats=[FORMAT_DATETIME]
    )
    date_livraison_prevue = forms.DateTimeField(
        label="Échéance de livraison", required=False, widget=_datetime_widget(), input_formats=[FORMAT_DATETIME],
        help_text="Laisser vide pour la calculer automatiquement à partir de la distance estimée."
    )
    camion = CamionChoiceField(
        queryset=Camion.objects.none(), required=False, label="Camion",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_camion'})
    )
    chauffeur = ChauffeurChoiceField(
        queryset=Chauffeur.objects.none(), required=False, label="Chauffeur",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_chauffeur'})
    )
    creneau_chargement = CreneauChoiceField(
        queryset=Creneau.objects.none(), required=False, label="Créneau de chargement",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_creneau_chargement'})
    )
    creneau_dechargement = CreneauChoiceField(
        queryset=Creneau.objects.none(), required=False, label="Créneau de déchargement",
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_creneau_dechargement'})
    )

    class Meta:
        model = Livraison
        fields = [
            'type_livraison', 'priorite', 'entrepot_origine', 'entrepot_destination',
            'destinataire_nom', 'destinataire_telephone', 'destinataire_email', 'adresse_livraison', 'ville_livraison',
            'type_marchandise', 'description_marchandise', 'nb_palettes', 'poids_kg', 'numero_bl', 'consignes',
            'date_depart_prevue', 'date_livraison_prevue',
            'camion', 'chauffeur', 'creneau_chargement', 'creneau_dechargement',
        ]
        widgets = {
            'type_livraison': forms.RadioSelect(attrs={'class': 'type-radio'}),
            'priorite': forms.Select(attrs={'class': 'form-select'}),
            'entrepot_origine': forms.Select(attrs={'class': 'form-select', 'id': 'id_entrepot_origine'}),
            'entrepot_destination': forms.Select(attrs={'class': 'form-select', 'id': 'id_entrepot_destination'}),
            'destinataire_nom': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Société Délice Sousse'}),
            'destinataire_telephone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+216 -- --- ---'}),
            'destinataire_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contact@client.tn'}),
            'adresse_livraison': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Rue, zone industrielle...'}),
            'ville_livraison': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Sousse', 'list': 'villes-connues'}),
            'type_marchandise': forms.Select(attrs={'class': 'form-select', 'id': 'id_type_marchandise'}),
            'description_marchandise': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Pièces automobiles, électroménager...'}),
            'nb_palettes': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'id': 'id_nb_palettes'}),
            'poids_kg': forms.NumberInput(attrs={'class': 'form-input', 'min': 0, 'placeholder': 'Ex: 18000', 'id': 'id_poids_kg'}),
            'numero_bl': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'N° BL / CMR'}),
            'consignes': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Précautions, horaires de réception du client...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        instance = self.instance
        self.fields['entrepot_origine'].queryset = Entrepot.objects.filter(statut='ACTIF').order_by('nom')
        self.fields['entrepot_destination'].queryset = Entrepot.objects.filter(statut='ACTIF').order_by('nom')
        self.fields['entrepot_destination'].required = False

        camions = ~Q(etat__in=regles.ETATS_CAMION_BLOQUANTS)
        chauffeurs = ~Q(statut='INACTIF')
        if instance.pk and instance.camion_id:
            camions |= Q(pk=instance.camion_id)
        if instance.pk and instance.chauffeur_id:
            chauffeurs |= Q(pk=instance.chauffeur_id)
        self.fields['camion'].queryset = Camion.objects.filter(camions).order_by('immatriculation')
        self.fields['chauffeur'].queryset = Chauffeur.objects.filter(chauffeurs).order_by('nom', 'prenom')

        ouverts = Q(statut__in=('EN_ATTENTE', 'CONFIRME'))
        charg = Creneau.objects.filter(type_operation='CHARGEMENT').select_related('quai', 'entrepot')
        decharg = Creneau.objects.filter(type_operation='DECHARGEMENT').select_related('quai', 'entrepot')
        if instance.pk and instance.creneau_chargement_id:
            charg = charg.filter(ouverts | Q(pk=instance.creneau_chargement_id))
        else:
            charg = charg.filter(ouverts)
        if instance.pk and instance.creneau_dechargement_id:
            decharg = decharg.filter(ouverts | Q(pk=instance.creneau_dechargement_id))
        else:
            decharg = decharg.filter(ouverts)
        self.fields['creneau_chargement'].queryset = charg.order_by('date_creneau', 'heure_debut')
        self.fields['creneau_dechargement'].queryset = decharg.order_by('date_creneau', 'heure_debut')

    def clean_poids_kg(self):
        poids = self.cleaned_data.get('poids_kg')
        if poids is not None and poids <= 0:
            raise forms.ValidationError("Le poids doit être strictement positif.")
        return poids

    def clean(self):
        cleaned = super().clean()
        depart = cleaned.get('date_depart_prevue')
        if depart and not cleaned.get('date_livraison_prevue'):
            # Échéance calculée automatiquement : départ + durée de trajet estimée (geo.py)
            origine = cleaned.get('entrepot_origine')
            if cleaned.get('type_livraison') == 'INTER_ENTREPOT':
                destination = cleaned.get('entrepot_destination')
                ville_arrivee = destination.ville if destination else ''
            else:
                ville_arrivee = cleaned.get('ville_livraison', '')
            camion = cleaned.get('camion')
            duree = geo.duree_trajet(
                geo.distance_km(origine.ville if origine else '', ville_arrivee),
                camion.type_camion if camion else 'SEMI_REMORQUE'
            )
            if duree:
                cleaned['date_livraison_prevue'] = depart + duree
                self.instance.date_livraison_prevue = cleaned['date_livraison_prevue']
            else:
                self.add_error(
                    'date_livraison_prevue',
                    "Ville non reconnue pour le calcul automatique : saisissez l'échéance manuellement."
                )
        return cleaned


class PreuveLivraisonForm(forms.Form):
    """Preuve de livraison (POD) : saisie mobile par le chauffeur ou le gestionnaire de destination."""
    receptionnaire_nom = forms.CharField(
        max_length=150, label="Nom du réceptionnaire",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Nom et prénom de la personne qui réceptionne'})
    )
    signature_data = forms.CharField(required=False, widget=forms.HiddenInput(attrs={'id': 'id_signature_data'}))
    photo_preuve = forms.ImageField(
        required=False, label="Photo de preuve (optionnelle si signature)",
        widget=forms.ClearableFileInput(attrs={'class': 'form-input', 'accept': 'image/*', 'capture': 'environment'})
    )
    livraison_conforme = forms.BooleanField(required=False, initial=True, label="Marchandise reçue conforme")
    reserves = forms.CharField(
        required=False, label="Réserves éventuelles",
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Ex: 1 palette filmée abîmée'})
    )
    note_satisfaction = forms.TypedChoiceField(
        required=False, coerce=int, empty_value=None, label="Satisfaction du destinataire",
        choices=[('', '— Non renseignée —')] + [(i, f"{i} / 5") for i in range(5, 0, -1)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def clean_photo_preuve(self):
        photo = self.cleaned_data.get('photo_preuve')
        if photo and photo.size > TAILLE_MAX_IMAGE:
            raise forms.ValidationError("La photo ne doit pas dépasser 5 Mo.")
        return photo

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('signature_data') and not cleaned.get('photo_preuve'):
            raise forms.ValidationError("Une signature ou une photo de preuve est obligatoire (règle R11).")
        if not cleaned.get('livraison_conforme') and not cleaned.get('reserves', '').strip():
            self.add_error('reserves', "Décrivez les réserves pour une livraison non conforme.")
        return cleaned


class IncidentForm(forms.ModelForm):
    class Meta:
        model = IncidentLivraison
        fields = ['type_incident', 'gravite', 'description', 'photo']
        widgets = {
            'type_incident': forms.Select(attrs={'class': 'form-select'}),
            'gravite': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Que se passe-t-il ? Où êtes-vous ?'}),
            'photo': forms.ClearableFileInput(attrs={'class': 'form-input', 'accept': 'image/*', 'capture': 'environment'}),
        }

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and getattr(photo, 'size', 0) > TAILLE_MAX_IMAGE:
            raise forms.ValidationError("La photo ne doit pas dépasser 5 Mo.")
        return photo


class MotifForm(forms.Form):
    motif = forms.CharField(
        label="Motif", widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Précisez la raison...'})
    )


class EchecForm(MotifForm):
    type_incident = forms.ChoiceField(
        label="Cause de l'échec",
        choices=[
            ('REFUS_CLIENT', 'Refus du destinataire'),
            ('ADRESSE_INTROUVABLE', 'Adresse introuvable / Destinataire absent'),
            ('DOMMAGE', 'Marchandise endommagée'),
            ('AUTRE', 'Autre'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class ReaffectationForm(forms.Form):
    camion = CamionChoiceField(
        queryset=Camion.objects.exclude(etat__in=regles.ETATS_CAMION_BLOQUANTS).order_by('immatriculation'),
        required=False, label="Nouveau camion", widget=forms.Select(attrs={'class': 'form-select'})
    )
    chauffeur = ChauffeurChoiceField(
        queryset=Chauffeur.objects.exclude(statut='INACTIF').order_by('nom'),
        required=False, label="Nouveau chauffeur", widget=forms.Select(attrs={'class': 'form-select'})
    )
    ancien_camion_en_panne = forms.BooleanField(
        required=False, label="Passer l'ancien camion en maintenance (panne)"
    )
    commentaire = forms.CharField(
        required=False, max_length=150, label="Commentaire",
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ex: Panne moteur à Enfidha'})
    )

    def clean(self):
        cleaned = super().clean()
        if not cleaned.get('camion') and not cleaned.get('chauffeur'):
            raise forms.ValidationError("Choisissez au moins un nouveau camion ou un nouveau chauffeur.")
        return cleaned
