from django.db import models

class Category(models.Model):
    """
    Represents a product category in the GestiArt application.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Returns a string representation of the category.
        """
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
