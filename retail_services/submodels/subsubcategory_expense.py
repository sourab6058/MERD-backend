from django.db import models
from .sub_sub_category import SubSubCategory
from .nationality import Nationality
from .zone import Zone
from django.core.validators import RegexValidator
from .city import City


def only_alpha():
    return [RegexValidator(r'^[a-zA-Z\s]*$', 'Only alpha characters are allowed.')]


class SubSubCategoryExpense(models.Model):
    nationality = models.ForeignKey(
        Nationality, on_delete=models.CASCADE, null=True)
    subsubcategory_expense = models.DecimalField(
        max_digits=19, decimal_places=3)
    spent_online = models.DecimalField(
        max_digits=19, decimal_places=3, default=3)
    spent_incity = models.DecimalField(
        max_digits=19, decimal_places=3, default=70)
    year = models.IntegerField()
    month = models.IntegerField()
    monthly_income = models.DecimalField(max_digits=19, decimal_places=3)
    sub_sub_category = models.ForeignKey(
        SubSubCategory, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    household_members = models.IntegerField()
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, null=False)
