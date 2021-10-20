from django.db import models
from .zone import Zone
from django.core.validators import RegexValidator
from .city import City

def only_alpha():
    return [RegexValidator(r'^[a-zA-Z\s]*$', 'Only alpha characters are allowed.')]

class Household(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=False)
    year = models.IntegerField()
    population = models.IntegerField()
    household_number = models.IntegerField()
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=False)
    family_percent = models.IntegerField(null=True, blank=True)
    bachelor_percent = models.IntegerField(null=True, blank=True)
    labourer_percent = models.IntegerField(null=True, blank=True)
    first_half_year = models.NullBooleanField()
    second_half_year = models.NullBooleanField()