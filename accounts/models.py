from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    Profil utilisateur étendu gérant les rôles dans CargoLink :
    - Gestionnaire d'Entrepôt (Entreprise, Quais, Stocks)
    - Transporteur / Chauffeur (Flotte, Camions, Livraisons)
    - Planificateur de Créneaux (Logistique, Réservations)
    - Administrateur Système
    """
    ROLE_CHOICES = [
        ('ENTREPOT', "Gestionnaire d'Entrepôt"),
        ('TRANSPORTEUR', "Transporteur / Chauffeur"),
        ('PLANIFICATEUR', "Planificateur de Créneaux"),
        ('ADMIN', "Administrateur Plateforme"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ENTREPOT')
    telephone = models.CharField(max_length=30, blank=True, help_text="Numéro de téléphone")
    entreprise = models.CharField(max_length=150, blank=True, help_text="Société / Organisation")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Profil Utilisateur"
        verbose_name_plural = "Profils Utilisateurs"

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.get_role_display()})"

    @property
    def display_name(self):
        full_name = self.user.get_full_name()
        return full_name if full_name else self.user.username

    @property
    def initials(self):
        first = self.user.first_name[:1] if self.user.first_name else self.user.username[:1]
        last = self.user.last_name[:1] if self.user.last_name else ""
        return (first + last).upper()


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil lors de la création d'un utilisateur."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
