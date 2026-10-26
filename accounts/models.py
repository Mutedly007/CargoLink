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

    @property
    def is_admin(self):
        """Détermine si l'utilisateur a les prérogatives d'administrateur CargoLink."""
        if self.role == 'ADMIN':
            return True
        if self.user.is_superuser and self.user.username == 'admin':
            return True
        return False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Synchronisation automatique des permissions Django avec le rôle CargoLink
        if self.role == 'ADMIN':
            if not self.user.is_staff or not self.user.is_superuser:
                self.user.is_staff = True
                self.user.is_superuser = True
                self.user.save(update_fields=['is_staff', 'is_superuser'])
        else:
            # Si le rôle n'est plus ADMIN, révoquer les privilèges (sauf pour le compte root 'admin')
            if self.user.username != 'admin' and (self.user.is_staff or self.user.is_superuser):
                self.user.is_staff = False
                self.user.is_superuser = False
                self.user.save(update_fields=['is_staff', 'is_superuser'])



@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Crée automatiquement un profil lors de la création d'un utilisateur."""
    if created:
        UserProfile.objects.get_or_create(user=instance)
    else:
        if hasattr(instance, 'profile'):
            instance.profile.save()
