from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """
    Custom User model for GestiArt application.
    Uses email as the unique identifier for authentication.
    Includes user_type field to differentiate between admin, artisan, and secondary admin.
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('artisan', 'Artisan'),
        ('secondary_admin', 'Secondary Admin'),
    )
    username = None # Remove username field
    email = models.EmailField(unique=True, max_length=191)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='artisan')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text=(
            'The groups this user belongs to. A user will get all permissions ' 
            'granted to each of their groups.'
        ),
        related_name="user_groups", # Added related_name
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="user_permissions", # Added related_name
        related_query_name="user",
    )

    def __str__(self):
        return self.email

# users/models.py
# from django.db import models
# from django.contrib.auth.models import AbstractUser
# from django.utils.translation import gettext_lazy as _

# class User(AbstractUser):
#     """
#     Modèle utilisateur personnalisé qui étend le modèle utilisateur de base de Django.
#     """
#     class UserType(models.TextChoices):
#         ADMIN = 'admin', _('Administrateur')
#         SECONDARY_ADMIN = 'secondary_admin', _('Administrateur Secondaire')
#         ARTISAN = 'artisan', _('Artisan')
#         CLIENT = 'client', _('Client')

#     user_type = models.CharField(
#         _('Type d\'utilisateur'),
#         max_length=20,
#         choices=UserType.choices,
#         default=UserType.ARTISAN
#     )
#     phone = models.CharField(
#         _('Téléphone'),
#         max_length=20,
#         blank=True,
#         null=True
#     )
#     address = models.TextField(
#         _('Adresse'),
#         blank=True,
#         null=True
#     )
#     date_joined = models.DateTimeField(
#         _('Date d\'inscription'),
#         auto_now_add=True
#     )
#     is_verified = models.BooleanField(
#         _('Compte vérifié'),
#         default=False
#     )

#     class Meta:
#         verbose_name = _('Utilisateur')
#         verbose_name_plural = _('Utilisateurs')
#         ordering = ['-date_joined']

#     def __str__(self):
#         return self.get_full_name() or self.email

#     @property
#     def full_name(self):
#         """Retourne le nom complet de l'utilisateur."""
#         return f"{self.first_name} {self.last_name}".strip()

#     def is_artisan(self):
#         """Vérifie si l'utilisateur est un artisan."""
#         return self.user_type == self.UserType.ARTISAN

#     def is_admin_or_secondary(self):
#         """Vérifie si l'utilisateur est un administrateur ou un administrateur secondaire."""
#         return self.user_type in [self.UserType.ADMIN, self.UserType.SECONDARY_ADMIN]

# class ArtisanProfile(models.Model):
#     """
#     Profil étendu pour les artisans.
#     """
#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='artisan_profile',
#         limit_choices_to={'user_type': User.UserType.ARTISAN}
#     )
#     speciality = models.CharField(
#         _('Spécialité'),
#         max_length=100,
#         blank=True,
#         null=True
#     )
#     bio = models.TextField(
#         _('Biographie'),
#         blank=True,
#         null=True
#     )
#     shop_name = models.CharField(
#         _('Nom de la boutique'),
#         max_length=100,
#         blank=True,
#         null=True
#     )
#     shop_address = models.TextField(
#         _('Adresse de la boutique'),
#         blank=True,
#         null=True
#     )
#     is_featured = models.BooleanField(
#         _('Mise en avant'),
#         default=False,
#         help_text=_('Cocher pour mettre en avant cet artisan sur la page d\'accueil')
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _('Profil Artisan')
#         verbose_name_plural = _('Profils Artisans')

#     def __str__(self):
#         return f"Profil de {self.user.get_full_name() or self.user.email}"

# class ClientProfile(models.Model):
#     """
#     Profil étendu pour les clients.
#     """
#     user = models.OneToOneField(
#         User,
#         on_delete=models.CASCADE,
#         related_name='client_profile',
#         limit_choices_to={'user_type': User.UserType.CLIENT}
#     )
#     date_of_birth = models.DateField(
#         _('Date de naissance'),
#         null=True,
#         blank=True
#     )
#     preferences = models.JSONField(
#         _('Préférences'),
#         default=dict,
#         blank=True
#     )
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     class Meta:
#         verbose_name = _('Profil Client')
#         verbose_name_plural = _('Profils Clients')

#     def __str__(self):
#         return f"Profil client de {self.user.get_full_name() or self.user.email}"

# # Assurez-vous d'ajouter dans settings.py:
# # AUTH_USER_MODEL = 'users.User'