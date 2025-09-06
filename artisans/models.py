from django.db import models
from users.models import User

class Artisan(models.Model):
    """
    Represents an Artisan in the GestiArt application.
    Each artisan is linked to a custom User and stores personal and professional details.
    Includes a profile image for the artisan.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='artisan_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    speciality = models.CharField(max_length=100)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='artisans_images/', blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the artisan.
        """
        return f"{self.first_name} {self.last_name}"
