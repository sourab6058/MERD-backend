from django.db import models
from smart_selects.db_fields import GroupedForeignKey
from .city import City
from .nationality import Nationality


class DemographicTable(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    type = models.CharField(max_length=100, null=False)
    mode = models.CharField(max_length=100, null=False)
    file_path = models.CharField(max_length=100, null=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
