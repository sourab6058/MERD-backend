from django.contrib import admin
from .submodels.category import Category
from .submodels.residence_area import ResidenceArea
from .submodels.user_profile import UserProfile
from .submodels.sub_category import SubCategory
from .submodels.sub_sub_category import SubSubCategory
from .submodels.category_expense import CategoryExpense
from .submodels.zone import Zone
from .submodels.household import Household
from .submodels.nationality import Nationality
from .submodels.household_nationality import HouseholdNationality
from .submodels.subcategory_expense import SubCategoryExpense
from .submodels.subsubcategory_expense import SubSubCategoryExpense
from .submodels.city import City
from .submodels.mall import Mall
from .submodels.country import Country

#from .resource import ZoneResource
from import_export.admin import ImportExportModelAdmin

# Register your models here.


class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name')


admin.site.register(Category, CategoryAdmin)


class ResidenceAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'area_name')


admin.site.register(ResidenceArea, ResidenceAreaAdmin)


class UserProfileAdmin(ImportExportModelAdmin):
    list_display = ('id', 'nationality', 'city')


admin.site.register(UserProfile, UserProfileAdmin)


class ZoneAdmin(ImportExportModelAdmin):
    list_display = ('id', 'zone', 'city')


admin.site.register(Zone, ZoneAdmin)


class CategoryExpenseAdmin(ImportExportModelAdmin):
    list_display = ('id', 'category_expense', 'monthly_income',
                    'year', 'month', 'nationality', 'category', 'city', 'zone')


admin.site.register(CategoryExpense, CategoryExpenseAdmin)


class HouseholdAdmin(ImportExportModelAdmin):
    list_display = ('id', 'zone', 'city', 'population',
                    'household_number', 'year')


admin.site.register(Household, HouseholdAdmin)


class NationalityAdmin(admin.ModelAdmin):
    list_display = ('id', 'nationality')


admin.site.register(Nationality, NationalityAdmin)


class HouseholdNationalityAdmin(ImportExportModelAdmin):
    list_display = ('id', 'nationality_percentage', 'nationality')


admin.site.register(HouseholdNationality, HouseholdNationalityAdmin)


class SubCategoryExpenseAdmin(ImportExportModelAdmin):
    list_display = ('id', 'subcategory_expense', 'monthly_income',
                    'year', 'month', 'nationality', 'city', 'zone', 'sub_category')


admin.site.register(SubCategoryExpense, SubCategoryExpenseAdmin)


class SubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'category')

    def category(self, obj):
        return obj.category.name


admin.site.register(SubCategory, SubCategoryAdmin)


class SubSubCategoryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'name', 'sub_category', 'category')

    def subcategory(self, obj):
        return obj.sub_category.name

    def category(self, obj):
        return obj.sub_category.category.name


admin.site.register(SubSubCategory, SubSubCategoryAdmin)


class SubSubCategoryExpenseAdmin(admin.ModelAdmin):
    list_display = ('id', 'subsubcategory_expense', 'monthly_income',
                    'year', 'month', 'nationality', 'city', 'zone', 'sub_sub_category')


admin.site.register(SubSubCategoryExpense, SubSubCategoryExpenseAdmin)


class CityAdmin(admin.ModelAdmin):
    list_display = ('id', 'city', "country")


admin.site.register(City, CityAdmin)


class MallAdmin(ImportExportModelAdmin):
    list_display = ('id', 'city', 'name', 'zone', 'area_covered')


admin.site.register(Mall, MallAdmin)


class CountryAdmin(ImportExportModelAdmin):
    list_display = ('id', 'country', )


admin.site.register(Country, CountryAdmin)
