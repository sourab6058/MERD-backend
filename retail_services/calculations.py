from django.db.models import Sum, Count, F, Value, ExpressionWrapper
from datetime import datetime
from django.db.models import Q
from django.db import models
import os
from django.conf import settings


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
from .submodels.mall import Mall


# def sort_json(year_data):
#     print('sort ',year_data[0]['cities'])
#     workflows = year_data[0]["cities"][0]["categories"][0]["data"][0]['zone']
#     return sorted(workflows, key=lambda d: d["name"])
# return workflows

def get_nationality_consolidated_category_data(nationality_id, zones, months, years, categories, cities, purchase_mode, place_of_purchase):
    print("nation ", cities)
    distinct_data = []
    nationality_data = []

    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            print("city ", city)
            category_data = []
            for category in categories:
                zone_data = []
                _zones = Zone.objects.filter(
                    id__in=zones, city_id=city).order_by('zone')
                print("zones ", _zones)
                for zone in _zones:
                    zone_category_expense = CategoryExpense.objects.filter(zone_id=zone.id,
                                                                           month__in=months,
                                                                           nationality_id__in=nationality_id,
                                                                           category_id=category,
                                                                           city_id=city,
                                                                           year=year
                                                                           ).values('nationality__nationality',
                                                                                    'nationality__id',
                                                                                    'category__name',
                                                                                    'year',
                                                                                    'city',
                                                                                    'month',
                                                                                    'zone_id'
                                                                                    ).annotate(total_category_expense=Sum('category_expense'), total_online=Sum(F('spent_online')*F('category_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_category_expense')-F('total_online'), output_field=models.DecimalField()),
                                                                                               total_category_expense_incity=Sum(F('category_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('category_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_category_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                               total_category_expense_outcity=ExpressionWrapper(F('total_category_expense')-F('total_category_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                               nationality_count=Count('nationality')).order_by('zone__zone')
                    month_data = []
                    total_market_size = 0
                    expenditure_mode = 'total_category_expense'
                    if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                        expenditure_mode = 'total_category_expense'
                    elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                        expenditure_mode = 'total_online'
                    elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                        expenditure_mode = 'total_offline'
                    elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                        expenditure_mode = 'total_category_expense_incity'
                    elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                        expenditure_mode = 'total_category_expense_outcity'
                    elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                        expenditure_mode = 'total_online_incity'
                    elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                        expenditure_mode = 'total_online_outcity'
                    elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                        expenditure_mode = 'total_offline_incity'
                    elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                        expenditure_mode = 'total_offline_outcity'
                    for expense in zone_category_expense:
                        if expense[expenditure_mode] is not None:
                            try:
                                single_household_expense = int(
                                    expense[expenditure_mode]/expense['nationality_count'])

                                if int(year) == 2020:
                                    if int(expense['month']) <= 6:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                    else:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                else:
                                    total_household = Household.objects.filter(
                                        zone_id=expense['zone_id'], year=year, city_id=city).first()

                                nationality_obj = HouseholdNationality.objects.filter(
                                    household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                household_nationality_count = int(
                                    (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                market_size = household_nationality_count * \
                                    float(single_household_expense)

                                nationality_obj = Nationality.objects.get(
                                    id=expense['nationality__id'])
                                total_market_size = market_size+total_market_size

                                month_data.append({"month": expense['month'],
                                                   "market_size": market_size})
                            except Exception as e:
                                total_market_size = 0

                    _zone = Zone.objects.get(id=zone.id, city_id=city)
                    zone_data.append({"zone": _zone.zone,
                                      # "month":month_data,
                                      "total_market_size": total_market_size})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "data": zone_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    # year_data = sort_json(year_data)

    return year_data


def get_nationality_consolidated_subcategory_data(nationality_id, zones, months, years, subcategories, cities, purchase_mode, place_of_purchase):
    distinct_data = []

    categories = []
    subcategory_data = []
    for subcategory in subcategories:
        subcategory = SubCategory.objects.get(id=subcategory)
        if subcategory.category.id not in categories:
            categories.append(subcategory.category.id)

    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                subcategory_data = []
                _subcategories = SubCategory.objects.filter(
                    id__in=subcategories, category_id=category)
                for subcategory in _subcategories:
                    zone_data = []
                    _zones = Zone.objects.filter(id__in=zones, city_id=city)
                    for zone in _zones:
                        zone_category_expense = SubCategoryExpense.objects.filter(zone_id=zone,
                                                                                  month__in=months,
                                                                                  nationality_id__in=nationality_id,
                                                                                  sub_category_id=subcategory.id,
                                                                                  sub_category__category_id=category,
                                                                                  city=city,
                                                                                  year=year
                                                                                  ).values('nationality__nationality',
                                                                                           'nationality__id',
                                                                                           'sub_category__name',
                                                                                           'sub_category__id',
                                                                                           'month',
                                                                                           'year',
                                                                                           'zone_id'
                                                                                           ).annotate(total_subcategory_expense=Sum('subcategory_expense'), total_online=Sum(F('spent_online')*F('subcategory_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_subcategory_expense')-F('total_online'), output_field=models.DecimalField()),
                                                                                                      total_subcategory_expense_incity=Sum(F('subcategory_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('subcategory_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_subcategory_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                      total_subcategory_expense_outcity=ExpressionWrapper(F('total_subcategory_expense')-F('total_subcategory_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                      nationality_count=Count('nationality')).order_by('nationality_id', 'month')
                        month_data = []
                        total_market_size = 0
                        expenditure_mode = 'total_subcategory_expense'
                        if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_subcategory_expense'
                        elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_online'
                        elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_offline'
                        elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_subcategory_expense_incity'
                        elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_subcategory_expense_outcity'
                        elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_online_incity'
                        elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_online_outcity'
                        elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_offline_incity'
                        elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_offline_outcity'
                        for expense in zone_category_expense:
                            if expense[expenditure_mode] is not None:
                                try:
                                    single_household_expense = int(
                                        expense[expenditure_mode]/expense['nationality_count'])

                                    if int(year) == 2020:
                                        if int(expense['month']) <= 6:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                        else:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                    else:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city).first()
                                    # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=expense['year'],city_id=city).first()

                                    nationality_obj = HouseholdNationality.objects.filter(
                                        household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                    household_nationality_count = int(
                                        (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                    market_size = household_nationality_count * \
                                        float(single_household_expense)
                                    total_market_size = market_size+total_market_size
                                except:
                                    month_data = []
                        _zone = Zone.objects.get(id=zone.id, city_id=city)
                        zone_data.append({"zone": _zone.zone,
                                          # "month":month_data,
                                          "total_market_size": total_market_size})
                    subcategory_name = SubCategory.objects.get(
                        id=subcategory.id).name
                    subcategory_data.append({"subcategory": subcategory_name,
                                            "data": zone_data})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "subcategories": subcategory_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    return year_data


def get_nationality_consolidated_subsubcategory_data(nationality_id, zones, months, years, subsubcategories, cities, purchase_mode, place_of_purchase):
    distinct_data = []
    categories = []
    subcategories = []
    subsubcategory_data = []
    for subsubcategory in subsubcategories:
        subsubcategory = SubSubCategory.objects.get(id=subsubcategory)
        if subsubcategory.sub_category.id not in subcategories:
            subcategories.append(subsubcategory.sub_category.id)
        if subsubcategory.sub_category.category.id not in categories:
            categories.append(subsubcategory.sub_category.category.id)
    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                subcategory_data = []
                _subcategories = SubCategory.objects.filter(
                    id__in=subcategories, category_id=category)
                for subcategory in _subcategories:
                    subsubcategory_data = []
                    _subsubcategories = SubSubCategory.objects.filter(
                        id__in=subsubcategories, sub_category_id=subcategory.id)
                    for subsubcategory in _subsubcategories:
                        zone_data = []
                        _zones = Zone.objects.filter(
                            id__in=zones, city_id=city)
                        for zone in _zones:
                            zone_category_expense = SubSubCategoryExpense.objects.filter(zone_id=zone.id,
                                                                                         month__in=months,
                                                                                         nationality_id__in=nationality_id,
                                                                                         sub_sub_category_id=subsubcategory.id,
                                                                                         sub_sub_category__sub_category_id=subcategory.id,
                                                                                         sub_sub_category__sub_category__category_id=category,
                                                                                         city=city,
                                                                                         year=year
                                                                                         ).values('nationality__nationality',
                                                                                                  'nationality__id',
                                                                                                  'sub_sub_category__name',
                                                                                                  'sub_sub_category__id',
                                                                                                  'month',
                                                                                                  'year',
                                                                                                  'zone_id'
                                                                                                  ).annotate(total_subsubcategory_expense=Sum('subsubcategory_expense'), total_online=Sum(F('spent_online')*F('subsubcategory_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_subsubcategory_expense')-F('total_online'), output_field=models.DecimalField()),
                                                                                                             total_subsubcategory_expense_incity=Sum(F('subsubcategory_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('subsubcategory_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_subsubcategory_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                             total_subsubcategory_expense_outcity=ExpressionWrapper(F('total_subsubcategory_expense')-F('total_subsubcategory_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                             nationality_count=Count('nationality')).order_by('nationality_id', 'month')
                            month_data = []
                            total_market_size = 0
                            expenditure_mode = 'total_subsubcategory_expense'
                            if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                                expenditure_mode = 'total_subsubcategory_expense'
                            elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                                expenditure_mode = 'total_online'
                            elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                                expenditure_mode = 'total_offline'
                            elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                                expenditure_mode = 'total_subsubcategory_expense_incity'
                            elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                                expenditure_mode = 'total_subsubcategory_expense_outcity'
                            elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                                expenditure_mode = 'total_online_incity'
                            elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                                expenditure_mode = 'total_online_outcity'
                            elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                                expenditure_mode = 'total_offline_incity'
                            elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                                expenditure_mode = 'total_offline_outcity'
                            for expense in zone_category_expense:
                                if expense[expenditure_mode] is not None:
                                    # try:
                                    single_household_expense = int(
                                        expense[expenditure_mode]/expense['nationality_count'])
                                    if int(year) == 2020:
                                        if int(expense['month']) <= 6:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                        else:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                    else:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city).first()
                                    # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=expense['year'],city_id=city).first()

                                    nationality_obj = HouseholdNationality.objects.filter(
                                        household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                    household_nationality_count = int(
                                        (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                    market_size = household_nationality_count * \
                                        float(single_household_expense)
                                    total_market_size = market_size+total_market_size
                                    # except:
                                    #     total_market_size=0
                            _zone = Zone.objects.get(id=zone.id, city_id=city)
                            zone_data.append({"zone": _zone.zone,
                                              # "month":month_data,
                                              "total_market_size": total_market_size})
                        subsubcategory_name = SubSubCategory.objects.get(
                            id=subsubcategory.id).name
                        subsubcategory_data.append({"subsubcategory": subsubcategory_name,
                                                    "data": zone_data})
                    subcategory_name = SubCategory.objects.get(
                        id=subcategory.id).name
                    subcategory_data.append({"subcategory": subcategory_name,
                                            "subsubcategories": subsubcategory_data})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "subcategories": subcategory_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    return year_data


def get_zones_consolidated_category_data(nationality_id, zones, months, years, categories, cities, purchase_mode, place_of_purchase):
    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                zone_category_expense = CategoryExpense.objects.filter(zone_id__in=zones,
                                                                       month__in=months,
                                                                       nationality_id__in=nationality_id,
                                                                       category_id=category,
                                                                       year=year,
                                                                       city_id=city).values('nationality__nationality',
                                                                                            'nationality__id',
                                                                                            'month',
                                                                                            'zone',
                                                                                            'year',
                                                                                            'city__city',
                                                                                            'category__name').annotate(total_category_expense=Sum('category_expense'), total_online=Sum(F('spent_online')*F('category_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_category_expense')-F('total_online'), output_field=models.DecimalField()),
                                                                                                                       total_category_expense_incity=Sum(F('category_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('category_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_category_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                                       total_category_expense_outcity=ExpressionWrapper(F('total_category_expense')-F('total_category_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                                       nationality_count=Count('nationality')).order_by('month')

                market_size_data = []
                _month = []
                total_market_size = 0
                expenditure_mode = 'total_category_expense'
                if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                    expenditure_mode = 'total_category_expense'
                elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                    expenditure_mode = 'total_online'
                elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                    expenditure_mode = 'total_offline'
                elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                    expenditure_mode = 'total_category_expense_incity'
                elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                    expenditure_mode = 'total_category_expense_outcity'
                elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                    expenditure_mode = 'total_online_incity'
                elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                    expenditure_mode = 'total_online_outcity'
                elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                    expenditure_mode = 'total_offline_incity'
                elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                    expenditure_mode = 'total_offline_outcity'
                for expense in zone_category_expense:
                    if expense[expenditure_mode] is not None:
                        # try:
                        single_household_expense = int(
                            expense[expenditure_mode]/expense['nationality_count'])
                        if int(year) == 2020:
                            if int(expense['month']) <= 6:
                                total_household = Household.objects.filter(
                                    zone_id=expense['zone'], year=year, city_id=city, first_half_year=True).first()
                            else:
                                total_household = Household.objects.filter(
                                    zone_id=expense['zone'], year=year, city_id=city, second_half_year=True).first()
                        else:
                            total_household = Household.objects.filter(
                                zone_id=expense['zone'], year=year, city_id=city).first()
                        # total_household = Household.objects.filter(zone_id = expense['zone'], year=expense['year']).first()

                        hn = HouseholdNationality.objects.filter(
                            household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                        household_nationality_count = int(
                            (total_household.household_number/100)*hn.nationality_percentage)

                        month_market_size = household_nationality_count * \
                            float(single_household_expense)
                        total_market_size = total_market_size + month_market_size
                        # except:
                        #     total_market_size=0
                print("total market size ", total_market_size)
                _category = Category.objects.filter(id=category).first()
                category_data.append({"total_market_size": total_market_size,
                                      "category": _category.name})
            _city = City.objects.filter(id=city).first()
            city_data.append({"city": _city.city,
                              "market_data": category_data})
        year_data.append({"year": year,
                          "data": city_data})

    return year_data


def get_zones_consolidated_subcategory_data(nationality_id, zones, months, years, subcategories, cities, purchase_mode, place_of_purchase):
    distinct_data = []
    print("zones")
    categories = []
    subcategory_data = []
    for subcategory in subcategories:
        subcategory = SubCategory.objects.get(id=subcategory)
        if subcategory.category.id not in categories:
            categories.append(subcategory.category.id)

    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                subcategory_data = []
                _subcategories = SubCategory.objects.filter(
                    id__in=subcategories, category_id=category)
                for subcategory in _subcategories:
                    zone_category_expense = SubCategoryExpense.objects.filter(zone_id__in=zones,
                                                                              month__in=months,
                                                                              nationality_id__in=nationality_id,
                                                                              sub_category_id=subcategory.id,
                                                                              sub_category__category_id=category,
                                                                              city=city,
                                                                              year=year
                                                                              ).values('nationality__nationality',
                                                                                       'nationality__id',
                                                                                       'sub_category__name',
                                                                                       'sub_category__id',
                                                                                       'month',
                                                                                       'year',
                                                                                       'zone_id'
                                                                                       ).annotate(total_subcategory_expense=Sum('subcategory_expense'), total_online=Sum(F('spent_online')*F('subcategory_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_subcategory_expense')-F('total_online'), output_field=models.DecimalField()),
                                                                                                  total_subcategory_expense_incity=Sum(F('subcategory_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('subcategory_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_subcategory_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                  total_subcategory_expense_outcity=ExpressionWrapper(F('total_subcategory_expense')-F('total_subcategory_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                  nationality_count=Count('nationality')).order_by('nationality_id', 'month')
                    month_data = []
                    total_market_size = 0
                    expenditure_mode = 'total_subcategory_expense'
                    if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                        expenditure_mode = 'total_subcategory_expense'
                    elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                        expenditure_mode = 'total_online'
                    elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                        expenditure_mode = 'total_offline'
                    elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                        expenditure_mode = 'total_subcategory_expense_incity'
                    elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                        expenditure_mode = 'total_subcategory_expense_outcity'
                    elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                        expenditure_mode = 'total_online_incity'
                    elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                        expenditure_mode = 'total_online_outcity'
                    elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                        expenditure_mode = 'total_offline_incity'
                    elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                        expenditure_mode = 'total_offline_outcity'
                    for expense in zone_category_expense:
                        if expense[expenditure_mode] is not None:
                            try:
                                single_household_expense = int(
                                    expense[expenditure_mode]/expense['nationality_count'])

                                if int(year) == 2020:
                                    if int(expense['month']) <= 6:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                    else:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                else:
                                    total_household = Household.objects.filter(
                                        zone_id=expense['zone_id'], year=year, city_id=city).first()
                                # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=expense['year'],city_id=city).first()

                                nationality_obj = HouseholdNationality.objects.filter(
                                    household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                household_nationality_count = int(
                                    (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                market_size = household_nationality_count * \
                                    float(single_household_expense)
                                total_market_size = market_size+total_market_size
                            except:
                                month_data = []

                    subcategory_name = SubCategory.objects.get(
                        id=subcategory.id).name
                    subcategory_data.append({"subcategory": subcategory_name,
                                            "total_market_size": total_market_size})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "subcategories": subcategory_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    return year_data


def get_zones_consolidated_subsubcategory_data(nationality_id, zones, months, years, subsubcategories, cities, purchase_mode, place_of_purchase):
    distinct_data = []
    categories = []
    subcategories = []
    subsubcategory_data = []
    for subsubcategory in subsubcategories:
        subsubcategory = SubSubCategory.objects.get(id=subsubcategory)
        if subsubcategory.sub_category.id not in subcategories:
            subcategories.append(subsubcategory.sub_category.id)
        if subsubcategory.sub_category.category.id not in categories:
            categories.append(subsubcategory.sub_category.category.id)
    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                subcategory_data = []
                _subcategories = SubCategory.objects.filter(
                    id__in=subcategories, category_id=category)
                for subcategory in _subcategories:
                    subsubcategory_data = []
                    _subsubcategories = SubSubCategory.objects.filter(
                        id__in=subsubcategories, sub_category_id=subcategory.id)
                    for subsubcategory in _subsubcategories:
                        zone_category_expense = SubSubCategoryExpense.objects.filter(zone_id__in=zones,
                                                                                     month__in=months,
                                                                                     nationality_id__in=nationality_id,
                                                                                     sub_sub_category_id=subsubcategory.id,
                                                                                     sub_sub_category__sub_category_id=subcategory.id,
                                                                                     sub_sub_category__sub_category__category_id=category,
                                                                                     city=city,
                                                                                     year=year
                                                                                     ).values('nationality__nationality',
                                                                                              'nationality__id',
                                                                                              'sub_sub_category__name',
                                                                                              'sub_sub_category__id',
                                                                                              'month',
                                                                                              'year',
                                                                                              'zone_id'
                                                                                              ).annotate(total_subsubcategory_expense=Sum('subsubcategory_expense'), total_online=Sum(F('spent_online')*F('subsubcategory_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_subsubcategory_expense')-F('total_online'), output_field=models.DecimalField()),
                                                                                                         total_subsubcategory_expense_incity=Sum(F('subsubcategory_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('subsubcategory_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_subsubcategory_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                         total_subsubcategory_expense_outcity=ExpressionWrapper(F('total_subsubcategory_expense')-F('total_subsubcategory_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                         nationality_count=Count('nationality')).order_by('nationality_id', 'month')
                        month_data = []
                        total_market_size = 0
                        expenditure_mode = 'total_subsubcategory_expense'
                        if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_subsubcategory_expense'
                        elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_online'
                        elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_offline'
                        elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_subsubcategory_expense_incity'
                        elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_subsubcategory_expense_outcity'
                        elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_online_incity'
                        elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_online_outcity'
                        elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_offline_incity'
                        elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_offline_outcity'
                        for expense in zone_category_expense:
                            if expense[expenditure_mode] is not None:
                                try:
                                    single_household_expense = int(
                                        expense[expenditure_mode]/expense['nationality_count'])

                                    if int(year) == 2020:
                                        if int(expense['month']) <= 6:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                        else:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                    else:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city).first()

                                    # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=expense['year'],city_id=city).first()

                                    nationality_obj = HouseholdNationality.objects.filter(
                                        household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                    household_nationality_count = int(
                                        (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                    market_size = household_nationality_count * \
                                        float(single_household_expense)
                                    total_market_size = market_size+total_market_size
                                except:
                                    month_data = []
                        subsubcategory_name = SubSubCategory.objects.get(
                            id=subsubcategory.id).name
                        subsubcategory_data.append({"subsubcategory": subsubcategory_name,
                                                    "total_market_size": total_market_size})
                    subcategory_name = SubCategory.objects.get(
                        id=subcategory.id).name
                    subcategory_data.append({"subcategory": subcategory_name,
                                            "subsubcategories": subsubcategory_data})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "subcategories": subcategory_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    return year_data


def get_category_data(nationality_id, zones, months, years, categories, cities, purchase_mode, place_of_purchase):
    distinct_data = []
    nationality_data = []
    print(place_of_purchase)

    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                nationality_data = []
                for nationality in nationality_id:
                    zone_data = []
                    _zones = Zone.objects.filter(
                        id__in=zones, city_id=city).order_by('zone')
                    for zone in _zones:
                        zone_category_expense = CategoryExpense.objects.filter(zone_id=zone.id,
                                                                               month__in=months,
                                                                               nationality_id=nationality,
                                                                               category_id=category,
                                                                               city_id=city,
                                                                               year=year
                                                                               ).values('nationality__nationality',
                                                                                        'nationality__id',
                                                                                        'category__name',
                                                                                        'year',
                                                                                        'city',
                                                                                        'month',
                                                                                        'zone_id',
                                                                                        ).annotate(total_category_expense=Sum('category_expense'), total_online=Sum(F('spent_online')*F('category_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_category_expense') - F('total_online'), output_field=models.DecimalField()),
                                                                                                   total_category_expense_incity=Sum(F('category_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('category_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_category_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                   total_category_expense_outcity=ExpressionWrapper(F('total_category_expense')-F('total_category_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                   nationality_count=Count(
                                                                                                       'nationality')
                                                                                                   )

                        print(zone_category_expense)

                        month_data = []
                        total_market_size = 0
                        expenditure_mode = 'total_category_expense'
                        if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_category_expense'
                        elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_online'
                        elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                            expenditure_mode = 'total_offline'
                        elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_category_expense_incity'
                        elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_category_expense_outcity'
                        elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_online_incity'
                        elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_online_outcity'
                        elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                            expenditure_mode = 'total_offline_incity'
                        elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                            expenditure_mode = 'total_offline_outcity'
                        for expense in zone_category_expense:
                            if expense[expenditure_mode] is not None:
                                try:
                                    single_household_expense = int(
                                        expense[expenditure_mode]/expense['nationality_count'])

                                    if int(year) == 2020:
                                        if int(expense['month']) <= 6:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                        else:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                    else:
                                        total_household = Household.objects.filter(
                                            zone_id=expense['zone_id'], year=year, city_id=city).first()
                                    # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=year,city_id=city).first()

                                    nationality_obj = HouseholdNationality.objects.filter(
                                        household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                    household_nationality_count = int(
                                        (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                    market_size = household_nationality_count * \
                                        float(single_household_expense)

                                    nationality_obj = Nationality.objects.get(
                                        id=expense['nationality__id'])
                                    total_market_size = market_size+total_market_size

                                    month_data.append({"month": expense['month'],
                                                       "market_size": market_size})
                                except Exception as e:
                                    month_data = []
                        _zone = Zone.objects.get(id=zone.id, city_id=city)
                        zone_data.append({"zone": _zone.zone,
                                          "month": month_data,
                                          "total_market_size": total_market_size})

                    total_zone_market_size = 0
                    for _data in zone_data:
                        total_zone_market_size = int(
                            _data['total_market_size']) + total_zone_market_size
                    nationality = Nationality.objects.get(
                        id=nationality).nationality
                    nationality_data.append({"nationality": nationality,
                                            "data": zone_data,
                                             "total_zone_market_size": total_zone_market_size})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "nationality": nationality_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})

    return year_data


def get_subcategory_data(nationality_id, zones, months, years, subcategories, cities, purchase_mode, place_of_purchase):
    distinct_data = []

    categories = []
    subcategory_data = []
    for subcategory in subcategories:
        subcategory = SubCategory.objects.get(id=subcategory)
        if subcategory.category.id not in categories:
            categories.append(subcategory.category.id)

    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                subcategory_data = []
                _subcategories = SubCategory.objects.filter(
                    id__in=subcategories, category_id=category)
                for subcategory in _subcategories:
                    nationality_data = []
                    for nationality in nationality_id:
                        zone_data = []
                        _zones = Zone.objects.filter(
                            id__in=zones, city_id=city)
                        for zone in _zones:
                            zone_category_expense = SubCategoryExpense.objects.filter(zone_id=zone.id,
                                                                                      month__in=months,
                                                                                      nationality_id=nationality,
                                                                                      sub_category_id=subcategory.id,
                                                                                      sub_category__category_id=category,
                                                                                      city=city,
                                                                                      year=year
                                                                                      ).values('nationality__nationality',
                                                                                               'nationality__id',
                                                                                               'sub_category__name',
                                                                                               'sub_category__id',
                                                                                               'month',
                                                                                               'year',
                                                                                               'zone_id'
                                                                                               ).annotate(total_subcategory_expense=Sum('subcategory_expense'), total_online=Sum(F('spent_online')*F('subcategory_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_subcategory_expense') - F('total_online'), output_field=models.DecimalField()),
                                                                                                          total_subcategory_expense_incity=Sum(F('subcategory_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('subcategory_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_subcategory_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                          total_subcategory_expense_outcity=ExpressionWrapper(F('total_subcategory_expense')-F('total_subcategory_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                          nationality_count=Count(
                                                                                                   'nationality')).order_by('nationality_id', 'month')
                            month_data = []
                            total_market_size = 0
                            expenditure_mode = 'total_subcategory_expense'
                            if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                                expenditure_mode = 'total_subcategory_expense'
                            elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                                expenditure_mode = 'total_online'
                            elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                                expenditure_mode = 'total_offline'
                            elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                                expenditure_mode = 'total_subcategory_expense_incity'
                            elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                                expenditure_mode = 'total_subcategory_expense_outcity'
                            elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                                expenditure_mode = 'total_online_incity'
                            elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                                expenditure_mode = 'total_online_outcity'
                            elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                                expenditure_mode = 'total_offline_incity'
                            elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                                expenditure_mode = 'total_offline_outcity'
                            for expense in zone_category_expense:
                                if expense[expenditure_mode] is not None:
                                    try:
                                        single_household_expense = int(
                                            expense[expenditure_mode]/expense['nationality_count'])

                                        if int(year) == 2020:
                                            if int(expense['month']) <= 6:
                                                total_household = Household.objects.filter(
                                                    zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                            else:
                                                total_household = Household.objects.filter(
                                                    zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                        else:
                                            total_household = Household.objects.filter(
                                                zone_id=expense['zone_id'], year=year, city_id=city).first()
                                        # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=expense['year'],city_id=city).first()

                                        nationality_obj = HouseholdNationality.objects.filter(
                                            household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                        household_nationality_count = int(
                                            (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                        market_size = household_nationality_count * \
                                            float(single_household_expense)
                                        total_market_size = market_size+total_market_size

                                        month_data.append({"month": expense['month'],
                                                           "market_size": market_size})
                                    except:
                                        month_data = []
                            _zone = Zone.objects.get(id=zone.id, city_id=city)
                            zone_data.append({"zone": _zone.zone,
                                              "month": month_data,
                                              "total_market_size": total_market_size})
                        total_zone_market_size = 0
                        for _data in zone_data:
                            total_zone_market_size = int(
                                _data['total_market_size']) + total_zone_market_size
                        nationality = Nationality.objects.get(
                            id=nationality).nationality
                        nationality_data.append({"nationality": nationality,
                                                "data": zone_data,
                                                 "total_zone_market_size": total_zone_market_size})
                    subcategory_name = SubCategory.objects.get(
                        id=subcategory.id).name
                    subcategory_data.append({"subcategory": subcategory_name,
                                            "nationalities": nationality_data})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "subcategories": subcategory_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    return year_data


def get_subsubcategory_data(nationality_id, zones, months, years, subsubcategories, cities, purchase_mode, place_of_purchase):
    distinct_data = []
    categories = []
    subcategories = []
    subsubcategory_data = []
    for subsubcategory in subsubcategories:
        subsubcategory = SubSubCategory.objects.get(id=subsubcategory)
        if subsubcategory.sub_category.id not in subcategories:
            subcategories.append(subsubcategory.sub_category.id)
        if subsubcategory.sub_category.category.id not in categories:
            categories.append(subsubcategory.sub_category.category.id)
    year_data = []
    for year in years:
        city_data = []
        for city in cities:
            category_data = []
            for category in categories:
                subcategory_data = []
                _subcategories = SubCategory.objects.filter(
                    id__in=subcategories, category_id=category)
                for subcategory in _subcategories:
                    subsubcategory_data = []
                    _subsubcategories = SubSubCategory.objects.filter(
                        id__in=subsubcategories, sub_category_id=subcategory.id)
                    for subsubcategory in _subsubcategories:
                        nationality_data = []
                        for nationality in nationality_id:
                            zone_data = []
                            _zones = Zone.objects.filter(
                                id__in=zones, city_id=city)
                            for zone in _zones:
                                zone_category_expense = SubSubCategoryExpense.objects.filter(zone_id=zone.id,
                                                                                             month__in=months,
                                                                                             nationality_id=nationality,
                                                                                             sub_sub_category_id=subsubcategory.id,
                                                                                             sub_sub_category__sub_category_id=subcategory.id,
                                                                                             sub_sub_category__sub_category__category_id=category,
                                                                                             city=city,
                                                                                             year=year
                                                                                             ).values('nationality__nationality',
                                                                                                      'nationality__id',
                                                                                                      'sub_sub_category__name',
                                                                                                      'sub_sub_category__id',
                                                                                                      'month',
                                                                                                      'year',
                                                                                                      'zone_id'
                                                                                                      ).annotate(total_subsubcategory_expense=Sum('subsubcategory_expense'), total_online=Sum(F('spent_online')*F('subsubcategory_expense')*Value(0.01), output_field=models.DecimalField()), total_offline=ExpressionWrapper(F('total_subsubcategory_expense') - F('total_online'), output_field=models.DecimalField()),
                                                                                                                 total_subsubcategory_expense_incity=Sum(F('subsubcategory_expense')*F('spent_incity')*Value(0.01)), total_online_incity=Sum(F('spent_online')*F('spent_incity')*F('subsubcategory_expense')*Value(0.0001), output_field=models.DecimalField()), total_offline_incity=ExpressionWrapper(F('total_subsubcategory_expense_incity')-F('total_online_incity'), output_field=models.DecimalField()),
                                                                                                                 total_subsubcategory_expense_outcity=ExpressionWrapper(F('total_subsubcategory_expense')-F('total_subsubcategory_expense_incity'), output_field=models.DecimalField()), total_online_outcity=ExpressionWrapper(F('total_online')-F('total_online_incity'), output_field=models.DecimalField()), total_offline_outcity=ExpressionWrapper(F('total_offline')-F('total_offline_incity'), output_field=models.DecimalField()),
                                                                                                                 nationality_count=Count(
                                                                                                          'nationality')).order_by('nationality_id', 'month')
                                month_data = []
                                total_market_size = 0
                                if len(purchase_mode) == 2 and len(place_of_purchase) == 2:
                                    expenditure_mode = 'total_subsubcategory_expense'
                                elif purchase_mode[0] == 'online' and len(place_of_purchase) == 2:
                                    expenditure_mode = 'total_online'
                                elif purchase_mode[0] == 'offline' and len(place_of_purchase) == 2:
                                    expenditure_mode = 'total_offline'
                                elif len(purchase_mode) == 2 and place_of_purchase[0] == 'in':
                                    expenditure_mode = 'total_subsubcategory_expense_incity'
                                elif len(purchase_mode) == 2 and place_of_purchase[0] == 'out':
                                    expenditure_mode = 'total_subsubcategory_expense_outcity'
                                elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'in':
                                    expenditure_mode = 'total_online_incity'
                                elif purchase_mode[0] == 'online' and place_of_purchase[0] == 'out':
                                    expenditure_mode = 'total_online_outcity'
                                elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'in':
                                    expenditure_mode = 'total_offline_incity'
                                elif purchase_mode[0] == 'offline' and place_of_purchase[0] == 'out':
                                    expenditure_mode = 'total_offline_outcity'
                                for expense in zone_category_expense:
                                    if expense[expenditure_mode] is not None:
                                        try:
                                            single_household_expense = int(
                                                expense[expenditure_mode]/expense['nationality_count'])

                                            if int(year) == 2020:
                                                if int(expense['month']) <= 6:
                                                    total_household = Household.objects.filter(
                                                        zone_id=expense['zone_id'], year=year, city_id=city, first_half_year=True).first()
                                                else:
                                                    total_household = Household.objects.filter(
                                                        zone_id=expense['zone_id'], year=year, city_id=city, second_half_year=True).first()
                                            else:
                                                total_household = Household.objects.filter(
                                                    zone_id=expense['zone_id'], year=year, city_id=city).first()
                                            # total_household = Household.objects.filter(zone_id = expense['zone_id'], year=expense['year'],city_id=city).first()

                                            nationality_obj = HouseholdNationality.objects.filter(
                                                household_id=total_household.id, nationality_id=expense['nationality__id']).first()

                                            household_nationality_count = int(
                                                (total_household.household_number/100)*nationality_obj.nationality_percentage)

                                            market_size = household_nationality_count * \
                                                float(single_household_expense)
                                            total_market_size = market_size+total_market_size

                                            month_data.append({"month": expense['month'],
                                                               "market_size": market_size})
                                        except:
                                            month_data = []
                                _zone = Zone.objects.get(
                                    id=zone.id, city_id=city)
                                zone_data.append({"zone": _zone.zone,
                                                  "month": month_data,
                                                  "total_market_size": total_market_size})
                            total_zone_market_size = 0
                            for _data in zone_data:
                                total_zone_market_size = int(
                                    _data['total_market_size']) + total_zone_market_size
                            nationality = Nationality.objects.get(
                                id=nationality).nationality
                            nationality_data.append({"nationality": nationality,
                                                    "data": zone_data,
                                                     "total_zone_market_size": total_zone_market_size})
                        subsubcategory_name = SubSubCategory.objects.get(
                            id=subsubcategory.id).name
                        subsubcategory_data.append({"subsubcategory": subsubcategory_name,
                                                    "nationalities": nationality_data})
                    subcategory_name = SubCategory.objects.get(
                        id=subcategory.id).name
                    subcategory_data.append({"subcategory": subcategory_name,
                                            "subsubcategories": subsubcategory_data})
                category = Category.objects.get(id=category).name
                category_data.append({"category": category,
                                      "subcategories": subcategory_data})
            city = City.objects.get(id=city).city
            city_data.append({"city": city,
                              "categories": category_data})
        year_data.append({"year": year,
                          "cities": city_data})
    return year_data


# def get_category_data(nationality_id, zones, months, years, categories, cities):
#     distinct_data=[]

#     zone_category_expense = CategoryExpense.objects.filter(zone_id__in = zones,
#                                             month__in = months,
#                                             nationality_id__in = nationality_id,
#                                             category_id__in = categories,
#                                             city__in = cities,
#                                             year__in=years
#                                             ).values('nationality__nationality',
#                                             'nationality__id',
#                                             'category__name',
#                                             'month',
#                                             'year',
#                                             'zone_id'\
#                                             ).annotate(category_expense = Sum('category_expense'), nationality_count = Count('nationality'))


#     for expense in zone_category_expense:

#         if expense['category_expense'] is not None:

#             single_household_expense = int(expense['category_expense']/expense['nationality_count'])

#             total_household = Household.objects.get(zone_id = expense['zone_id'], year=expense['year'])

#             nationality = HouseholdNationality.objects.get(household_id = total_household.id, nationality_id = expense['nationality__id'])

#             household_nationality_count = int((total_household.household_number/100)*nationality.nationality_percentage)

#             market_size = household_nationality_count * float(single_household_expense)

#             nationality = Nationality.objects.get(id = expense['nationality__id'])

#             distinct_data.append({'zone' : expense['zone_id'],
#                 'nationality':nationality.nationality,
#                 'month':expense['month'], 'year':expense['year'],
#                 'category': expense['category__name'],
#                 'market_size':market_size})

#     return distinct_data

# def get_subcategory_data(nationality_id, zones, months, years, subcategories, cities):
#     categories=[]
#     subcategory_data=[]
#     for subcategory in subcategories:
#         subcategory = SubCategory.objects.get(id=subcategory)
#         if subcategory.category.id not in categories:
#             categories.append(subcategory.category.id)
#     for category in categories:
#         data=[]
#         for subcategory in subcategories:
#             zone_category_expense = SubCategoryExpense.objects.filter(zone_id__in = zones,
#                                                     month__in = months,
#                                                     nationality_id__in = nationality_id,
#                                                     sub_category_id = subcategory,
#                                                     city__in = cities,
#                                                     sub_category__category_id=category,
#                                                     year__in=years
#                                                     ).values('nationality__nationality',
#                                                     'nationality__id',
#                                                     'sub_category__name',
#                                                     'sub_category__category_id',
#                                                     'month',
#                                                     'year',
#                                                     'zone_id'\
#                                                     ).annotate(subcategory_expense = Sum('subcategory_expense'), nationality_count = Count('nationality')).order_by('nationality_id','month')

#             for expense in zone_category_expense:
#                 if expense['subcategory_expense'] is not None:

#                     single_household_expense = int(expense['subcategory_expense']/expense['nationality_count'])

#                     total_household = Household.objects.get(zone_id = expense['zone_id'], year=expense['year'])

#                     nationality = HouseholdNationality.objects.get(household_id = total_household.id, nationality_id = expense['nationality__id'])

#                     household_nationality_count = int((total_household.household_number/100)*nationality.nationality_percentage)

#                     market_size = household_nationality_count * float(single_household_expense)

#                     nationality = Nationality.objects.get(id = expense['nationality__id'])

#                     data.append({'zone' : expense['zone_id'],
#                         'nationality':nationality.nationality,
#                         'month':expense['month'], 'year':expense['year'],
#                         'subcategory': expense['sub_category__name'],
#                         'market_size':market_size})

#         total_market_size=0
#         for d in data:
#             total_market_size=total_market_size+int(d['market_size'])

#         category_name=Category.objects.get(id=category).name
#         subcategory_data.append({"category":category_name,
#                                 "total":total_market_size,
#                                 "data":data})

#     return subcategory_data

# def get_subsubcategory_data(nationality_id, zones, months, years, subsubcategories, cities):
#     categories=[]
#     subcategories=[]
#     subsubcategory_data=[]
#     for subsubcategory in subsubcategories:
#         subsubcategory = SubSubCategory.objects.get(id=subsubcategory)
#         if subsubcategory.sub_category.id not in subcategories:
#             subcategories.append(subsubcategory.sub_category.id)
#         if subsubcategory.sub_category.category.id not in categories:
#             categories.append(subsubcategory.sub_category.category.id)

#     for category in categories:
#         subcategory_data=[]
#         for subcategory in subcategories:
#             data=[]
#             for subsubcategory in subsubcategories:
#                 zone_category_expense = SubSubCategoryExpense.objects.filter(zone_id__in = zones,
#                                                         month__in = months,
#                                                         nationality_id__in = nationality_id,
#                                                         sub_sub_category_id = subsubcategory,
#                                                         sub_sub_category__sub_category_id=subcategory,
#                                                         city__in = cities,
#                                                         year__in=years
#                                                         ).values('nationality__nationality',
#                                                         'nationality__id',
#                                                         'sub_sub_category__name',
#                                                         'sub_sub_category__sub_category_id',
#                                                         'month',
#                                                         'year',
#                                                         'zone_id'\
#                                                         ).annotate(subsubcategory_expense = Sum('subsubcategory_expense'), nationality_count = Count('nationality')).order_by('nationality_id','month')

#                 for expense in zone_category_expense:
#                     if expense['subsubcategory_expense'] is not None:

#                         single_household_expense = int(expense['subsubcategory_expense']/expense['nationality_count'])

#                         total_household = Household.objects.get(zone_id = expense['zone_id'], year=expense['year'])

#                         nationality = HouseholdNationality.objects.get(household_id = total_household.id, nationality_id = expense['nationality__id'])

#                         household_nationality_count = int((total_household.household_number/100)*nationality.nationality_percentage)

#                         market_size = household_nationality_count * float(single_household_expense)

#                         nationality = Nationality.objects.get(id = expense['nationality__id'])

#                         data.append({'zone' : expense['zone_id'],
#                             'nationality':nationality.nationality,
#                             'month':expense['month'], 'year':expense['year'],
#                             'subsubcategory': expense['sub_sub_category__name'],
#                             'market_size':market_size})

#             total_market_size=0
#             for d in data:
#                 total_market_size=total_market_size+int(d['market_size'])

#             subcategory_name=SubCategory.objects.get(id=subcategory).name
#             subcategory_data.append({"subcategory":subcategory_name,
#                                     "total":total_market_size,
#                                     "data":data})

#         category_name=Category.objects.get(id=category).name
#         subsubcategory_data.append({"category":category_name,
#                                 "subcategory":subcategory_data})

#     return subsubcategory_data

# def get_zone_data(nationality_id, zones, months, years, category_id, city):
#     zone_data = []
#     for year in years:
#         for month in months:
#             zone_category_expense = CategoryExpense.objects.filter(zone_id__in = zones,
#                     month = months,
#                     nationality_id__in = nationality_id,
#                     category_id__in = category_id,
#                     city__in = city,
#                     year=years
#                     ).values('nationality__nationality',
#                     'nationality__id',
#                     'category__name',
#                     ).annotate(category_expense = Sum('category_expense'), nationality_count = Count('nationality'))

#             for expense in zone_category_expense:

#                 if expense['category_expense'] is not None:

#                     single_household_expense = int(expense['category_expense']/expense['nationality_count'])

#                     total_market_size = 0
#                     for zone in zones:
#                         total_household = Household.objects.get(zone_id = zone, year=year)

#                         nationality = HouseholdNationality.objects.get(household_id = total_household.id, nationality_id = expense['nationality__id'])

#                         household_nationality_count = int((total_household.household_number/100)*nationality.nationality_percentage)


#                         zone_market_size = household_nationality_count * float(single_household_expense)
#                         total_market_size = total_market_size + zone_market_size

#                         nationality = Nationality.objects.get(id = expense['nationality__id'])

#                     zone_data.append({'zone' : zones,
#                         'nationality':nationality.nationality,
#                         'month':month, 'year':year,
#                         'category': expense['category__name'],
#                         'category_expense': expense['category_expense'],
#                         'market_size':total_market_size})

#     return zone_data

# def get_month_data(nationalities, zones, months, years, categories, cities):
#     month_data = []
#     for nationality in nationalities:
#         for category in categories:
#             for year in years:
#                 city_data=[]
#                 for city in cities:
#                     zone_data=[]
#                     for zone in zones:
#                         total_market_size = 0
#                         zone_category_expense = CategoryExpense.objects.filter(zone_id = zone,
#                         month__in = months,
#                         nationality_id = nationality,
#                         category_id = category,
#                         year=year,
#                         city_id__in = city).values('nationality__nationality',
#                         'nationality__id',
#                         'month',
#                         'city__city',
#                         'category__name').annotate(category_expense = Sum('category_expense'), nationality_count = Count('nationality')).order_by('month')

#                         market_size_data=[]
#                         _month=[]
#                         for expense in zone_category_expense:
#                             if expense['category_expense'] is not None:
#                                 single_household_expense = int(expense['category_expense']/expense['nationality_count'])

#                                 total_household = Household.objects.get(zone_id = zone, year=year)

#                                 nationality = HouseholdNationality.objects.get(household_id = total_household.id, nationality_id = expense['nationality__id'])

#                                 household_nationality_count = int((total_household.household_number/100)*nationality.nationality_percentage)

#                                 month_market_size = household_nationality_count * float(single_household_expense)
#                                 total_market_size = total_market_size + month_market_size

#                                 nationality = Nationality.objects.get(id = expense['nationality__id'])
#                                 _month.append(expense['month'])
#                                 market_size_data.append(month_market_size)

#                         zone_data.append({"zone":zone,
#                                         "market_size":market_size_data,
#                                         "months":_month,
#                                         "total_market_size":total_market_size})

#                     category_name = Category.objects.get(id=category).name
#                     city_data.append({'nationality':nationality.nationality,
#                         'category': category_name,
#                         'zone' : zone_data,
#                         'year':year,
#                         })
#             city_name=City.objects.get(id=city).city
#             month_data.append({"city":city_name,
#                                 "data":city_data})

#     return month_data

def get_population_count(cities, zones, years, nationalities):
    city_data = []
    for city in cities:
        for year in years:
            _zones = Zone.objects.filter(id__in=zones, city_id=city)
            total_zone_population = 0
            zone_data = []
            for zone in _zones:
                populations = Household.objects.filter(
                    zone_id=zone, city_id=city, year=year)
                nationality_distribution_data = []
                for pop in populations:
                    nationality_household = HouseholdNationality.objects.filter(
                        household=pop, nationality_id__in=nationalities)
                    for nationality in nationality_household:
                        nationality_population = int(
                            pop.population * (nationality.nationality_percentage/100))
                        nationality_distribution_data.append(
                            {"nationality": nationality.nationality.nationality, "nationality_population": nationality_population})
                _zone = Zone.objects.filter(id=zone.id).first()
                zone_data.append(
                    {'zone': _zone.zone, 'data': nationality_distribution_data})
            _city = City.objects.get(id=city)
            city_data.append({"city": _city.city,
                              'year': year,
                              'category': 'population',
                              'zone_data': zone_data, })

    return city_data


def get_nationality_distribution(cities, zones, years, nationalities):
    city_data = []
    for city in cities:
        for year in years:
            _zones = Zone.objects.filter(
                id__in=zones, city_id=city).order_by('id')
            zone_data = []
            for zone in _zones:
                nationality_distribution_data = []
                households = Household.objects.filter(
                    zone_id=zone.id, city_id=city, year=year)
                for household in households:
                    nationality_household = HouseholdNationality.objects.filter(
                        household=household, nationality_id__in=nationalities)
                    for nationality in nationality_household:
                        nationality_distribution_data.append(
                            {"nationality": nationality.nationality.nationality, "percentage": nationality.nationality_percentage})
                _zone = Zone.objects.filter(id=zone.id).first()
                zone_data.append(
                    {"zone": _zone.zone, "nationality_data": nationality_distribution_data})
            _city = City.objects.get(id=city)
            city_data.append({"city": _city.city,
                              'year': year,
                              "category": "nationality_distribution",
                              'zone_data': zone_data})

    return city_data


def get_income_level(cities, zones, years, nationalities):
    city_data = []
    for city in cities:
        for year in years:
            _zones = Zone.objects.filter(
                id__in=zones, city_id=city).order_by('id')
            zone_data = []
            for zone in _zones:
                total_income = []
                for nat in nationalities:
                    incomes = CategoryExpense.objects.filter(zone_id=zone.id, year=year, city_id=city, nationality_id=nat).values(
                        'nationality__nationality', 'nationality__id').annotate(income_sum=Sum('monthly_income')).order_by("nationality__nationality")
                    if incomes:
                        for income in incomes:
                            total_income.append(
                                {"nationality": income['nationality__nationality'], "income": income['income_sum']})
                    else:
                        _nat = Nationality.objects.get(id=nat)
                        total_income.append(
                            {"nationality": _nat.nationality, "income": 0})

                _zone = Zone.objects.filter(id=zone.id).first()
                zone_data.append(
                    {"zone": _zone.zone, "total_income": total_income})

            nationality_object = Nationality.objects.all().distinct(
                'nationality', 'id').order_by('nationality')
            _nationalities = []
            for nationality in nationality_object:
                _nationalities.append(nationality.nationality)

            _city = City.objects.get(id=city)
            city_data.append({"city": _city.city,
                              "year": year,
                              "category": "income_level",
                              "nationality_list": _nationalities,
                              "zone_data": zone_data})

    return city_data


def get_category_capita(cities, zones, years, categories, nationalities):
    city_data = []
    for city in cities:
        for year in years:
            for category in categories:
                _zones = Zone.objects.filter(
                    id__in=zones, city_id=city).order_by('id')
                zone_data = []
                for zone in _zones:
                    category_capita = CategoryExpense.objects.filter(zone_id__in=zones,
                                                                     category_id=category,
                                                                     city_id=city,
                                                                     year=year,
                                                                     nationality_id__in=nationalities).values('city_id', 'year', 'category__name', 'nationality__nationality').annotate(category_expense_sum=Sum("category_expense")).order_by("nationality__nationality")
                    category_data = []
                    for _category in category_capita:
                        category_data.append(
                            {"nationality": _category['nationality__nationality'], "category_expense": _category['category_expense_sum']})
                    _zone = Zone.objects.filter(id=zone.id).first()
                    zone_data.append(
                        {"zone": _zone.zone, "category_data": category_data})
                cat_name = Category.objects.get(id=category)
                _city = City.objects.get(id=city)
                city_data.append({"city": _city.city,
                                  "year": year,
                                  "category": cat_name.name,
                                  "category_data": zone_data, })

    return city_data


def get_bachelors(cities, zones, years):
    city_data = []
    for city in cities:
        for year in years:
            bachelors = Household.objects.filter(
                zone_id__in=zones, city_id=city, year=year)
            bachelor_data = []
            for bachelor in bachelors:
                bachelor_data.append({"zone": bachelor.zone.zone,
                                      "bachelor_percent": bachelor.bachelor_percent})

            _city = City.objects.get(id=city)
            city_data.append({"city": _city.city,
                              "year": year,
                              "category": "bachelor",
                              "zone_data": bachelor_data, })

    return city_data


def get_labourers_percent(cities, zones, years):
    city_data = []
    for city in cities:
        for year in years:
            labourers = Household.objects.filter(
                zone_id__in=zones, city_id=city, year=year)
            labourer_data = []
            for labourer in labourers:
                labourer_data.append({"zone": labourer.zone.zone,
                                      "labourer_percent": labourer.labourer_percent})

            _city = City.objects.get(id=city)
            city_data.append({"city": _city.city,
                              "year": year,
                              "category": "labourer",
                              "zone_data": labourer_data, })

    return city_data

# function to search requested malls data (catchment zones they cover)


def get_malls_data():
    malls = Mall.objects.all()
    mall_data = []
    for mall in malls:
        mall_data.append({
            "id": mall.id,
            "name": mall.name,
            "city": mall.city.id,
            "zone": mall.zone.id,
        })
    return mall_data


def get_cities_data():
    cities = City.objects.all()
    data = []
    for city in cities:
        data.append({
            "id": city.id,
            "name": city.city
        })
    return data


def get_categories_data():
    categories = Category.objects.all()
    data = []
    for category in categories:
        data.append({
            "id": category.id,
            "name": category.name
        })
    return data


def update_date():
    with open(os.path.join(settings.MEDIA_ROOT, "lastupdate.txt"), "w") as f:
        tmstmp = datetime.now().timestamp()
        f.write(str(tmstmp))
        return tmstmp


def read_date():
    with open(os.path.join(settings.MEDIA_ROOT, "lastupdate.txt"), "r") as f:
        print(f.read())
        f.seek(0)
        return f.read()
