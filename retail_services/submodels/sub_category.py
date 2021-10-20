from django.db import models
from .category import Category

class SubCategory(models.Model):
    name = models.CharField(max_length=100, null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="category", null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name