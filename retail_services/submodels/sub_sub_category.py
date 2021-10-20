from django.db import models
from .sub_category import SubCategory

class SubSubCategory(models.Model):
    name = models.CharField(max_length=100, null=False)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name="sub_category", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name