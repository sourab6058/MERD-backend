from django.db import models
from .household import Household
from .nationality import Nationality

class HouseholdNationality(models.Model):
    nationality_percentage = models.IntegerField()
    nationality = models.ForeignKey(Nationality, on_delete = models.CASCADE, null=False)
    household = models.ForeignKey(Household, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)