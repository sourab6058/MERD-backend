from django.db import models
from django.core.validators import RegexValidator
from .residence_area import ResidenceArea
from .zone import Zone
from .nationality import Nationality
from django.conf import settings

def only_alpha():
    return [RegexValidator(r'^[a-zA-Z\s]*$', 'Only alpha characters are allowed.')]

class UserProfile(models.Model):
    ROLES = (
        ('U', 'User'),
        ('A', 'Admin')
    )
    nationality = models.ForeignKey(Nationality, on_delete=models.CASCADE, null = True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    household_members = models.IntegerField()
    city = models.CharField(max_length=100, null=False, validators=only_alpha())
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    role = models.CharField(max_length=1, choices=ROLES, null=False)
