from django.db import models
from .category import Category
from django.core.validators import RegexValidator
from .nationality import Nationality
from .zone import Zone
from .city import City
from smart_selects.db_fields import GroupedForeignKey


def only_alpha():
    return [RegexValidator(r'^[a-zA-Z\s]*$', 'Only alpha characters are allowed.')]


class CategoryExpense(models.Model):
    nationality = models.ForeignKey(
        Nationality, on_delete=models.CASCADE, null=True)

    category_expense = models.DecimalField(max_digits=19, decimal_places=3)
    spent_online = models.DecimalField(max_digits=19, decimal_places=3)
    year = models.IntegerField()
    month = models.IntegerField()
    monthly_income = models.DecimalField(max_digits=19, decimal_places=3)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    household_members = models.IntegerField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    zone = GroupedForeignKey(Zone, "city")
