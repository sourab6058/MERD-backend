from django.db import models
from .zone import Zone

class ResidenceArea(models.Model):
    area_name = models.CharField(max_length=100, null=False)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)