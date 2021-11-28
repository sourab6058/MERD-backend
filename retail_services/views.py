from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.db.models import Sum, Count
from rest_framework.views import APIView
from django.http import JsonResponse

from .submodels.zone import Zone
from .submodels.category_expense import CategoryExpense
from .submodels.user_profile import UserProfile
from .submodels.category import Category
from .submodels.household import Household
from .submodels.household_nationality import HouseholdNationality
from .submodels.nationality import Nationality
from .submodels.city import City
from .submodels.sub_category import SubCategory
from .submodels.sub_sub_category import SubSubCategory
from .submodels.subcategory_expense import SubCategoryExpense
from .submodels.subsubcategory_expense import SubSubCategoryExpense

from .serializers import ZoneSerializer, CitySerializer, CategorySerializer

from .calculations import get_category_data, get_subcategory_data, get_subsubcategory_data, get_zones_consolidated_category_data, get_zones_consolidated_subcategory_data, get_zones_consolidated_subsubcategory_data, get_nationality_consolidated_category_data, get_nationality_consolidated_subcategory_data, get_nationality_consolidated_subsubcategory_data, get_population_count, get_nationality_distribution, get_income_level, get_category_capita, get_bachelors, get_labourers_percent, get_malls_data
# Create your views here.


class FilterSecond(APIView):
    def get(self, request):
        print("localhost")
        years = CategoryExpense.objects.all().distinct('year').order_by('year')
        _years = []
        for year in years:
            _years.append(year.year)

        months = CategoryExpense.objects.all().distinct('month')
        _months = []
        for month in months:
            _months.append(month.month)

        nationalities = Nationality.objects.all().distinct(
            'nationality', 'id').order_by('nationality')
        _nationalities = []
        for nationality in nationalities:
            _nationalities.append(
                {"nationality": nationality.nationality, "id": nationality.id})

        categories = Category.objects.all()

        cities = City.objects.all().order_by('city')

        filter_list = []
        filter_list.append({"years": _years,
                            "months": _months,
                            "nationality": _nationalities,
                            "categories": CategorySerializer(categories, many=True).data,
                            "cities": CitySerializer(cities, many=True).data,
                            })

        return JsonResponse({"filters": filter_list})

    def post(self, request):
        data = request.data
        nationality_id = data.get('nationalities')
        zones = data.get('zones')
        months = data.get('months')
        years = data.get('years')
        categories = data.get('categories', None)
        subcategories = data.get('subCategories', None)
        subsubcategories = data.get('subSubCategories', None)
        cities = data.get('cities')
        filter_type = data.get('filter_type', None)
        first_half_year = data.get('first_half_year', None)
        second_half_year = data.get('second_half_year', None)
        purchase_mode = data.get('purchaseMode')
        place_of_purchase = data.get('placeOfPurchase')
        results = []
        if filter_type == 'zones':
            if categories != []:
                results.append(get_zones_consolidated_category_data(
                    nationality_id, zones, months, years, categories, cities, purchase_mode, place_of_purchase))

            if subcategories != []:
                results.append(get_zones_consolidated_subcategory_data(
                    nationality_id, zones, months, years, subcategories, cities, purchase_mode, place_of_purchase))

            if subsubcategories != []:
                results.append(get_zones_consolidated_subsubcategory_data(
                    nationality_id, zones, months, years, subsubcategories, cities, purchase_mode, place_of_purchase))

        elif filter_type == 'nationality':
            if categories != []:
                print("inside")
                results.append(get_nationality_consolidated_category_data(
                    nationality_id, zones, months, years, categories, cities, purchase_mode, place_of_purchase))

            if subcategories != []:
                results.append(get_nationality_consolidated_subcategory_data(
                    nationality_id, zones, months, years, subcategories, cities, purchase_mode, place_of_purchase))

            if subsubcategories != []:
                results.append(get_nationality_consolidated_subsubcategory_data(
                    nationality_id, zones, months, years, subsubcategories, cities, purchase_mode, place_of_purchase))

        elif filter_type == 'distinct':
            if categories != []:
                results.append(get_category_data(
                    nationality_id, zones, months, years, categories, cities, purchase_mode, place_of_purchase))

            if subcategories != []:
                results.append(get_subcategory_data(
                    nationality_id, zones, months, years, subcategories, cities, purchase_mode, place_of_purchase))

            if subsubcategories != []:
                results.append(get_subsubcategory_data(
                    nationality_id, zones, months, years, subsubcategories, cities, purchase_mode, place_of_purchase))
        # elif button == 'Month':
        #     result = get_month_data(nationality_id, zones, months, year, category_id, city)

        return JsonResponse({"results": results})


class DemographicInfo(APIView):
    def get(self, request):
        data = request.data
        print("data", data)
        return JsonResponse({'status': True})

    def post(self, request):
        data = request.data
        print("data ", data)
        cities = data.get('cities')
        zones = data.get('zones')
        years = data.get('years')
        categories = data.get('categories')
        nationalities = data.get('nationalities')
        income_check = data.get('income_checked')
        nationality_distribution = data.get('nationality_checked')
        age_distribution = data.get('age_checked')
        bachelors = data.get('families_checked')
        labourers = data.get('labourers_checked')
        capita = data.get('capita_checked')
        population = data.get('population_checked')

        result = None
        nationality_distribution_data = None
        income_level = None
        capita_data = None
        bachelors_data = None
        labourers_data = None
        if population == True:
            result = get_population_count(cities, zones, years, nationalities)
        if nationality_distribution == True:
            nationality_distribution_data = get_nationality_distribution(
                cities, zones, years, nationalities)
        if income_check == True:
            income_level = get_income_level(
                cities, zones, years, nationalities)
        if capita == True:
            capita_data = get_category_capita(
                cities, zones, years, categories, nationalities)
        if bachelors == True:
            bachelors_data = get_bachelors(cities, zones, years)
        if labourers == True:
            labourers_data = get_labourers_percent(cities, zones, years)

        return JsonResponse({"population": result,
                            "nationality_distribution": nationality_distribution_data,
                             "income_check": income_level,
                             "capita": capita_data,
                             "bachelors": bachelors_data,
                             "labourers": labourers_data})


class CatchmentsInfo(APIView):
    def get(self, _):
        malls_data = get_malls_data()
        return JsonResponse({"data": malls_data})
        
