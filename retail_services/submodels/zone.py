from django.db import models
from .city import City

class Zone(models.Model):
    zone = models.CharField(max_length=100,null=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="city_name", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{}".format(self.zone)