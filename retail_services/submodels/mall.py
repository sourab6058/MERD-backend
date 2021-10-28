from django.db import models
from smart_selects.db_fields import GroupedForeignKey
from .city import City
from .zone import Zone


class Mall(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=100, null=False)
    zone = GroupedForeignKey(Zone, "city")
    area_covered = models.DecimalField(
        max_digits=19, decimal_places=3)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
