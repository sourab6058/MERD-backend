from django.db import models
from .country import Country


class City(models.Model):
    city = models.CharField(max_length=50, null=False)
    country = models.ForeignKey(
        Country, on_delete=models.CASCADE, related_name="city_name", null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.city
