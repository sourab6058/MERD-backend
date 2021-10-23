from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.decorators import api_view

import xlrd
from tablib import Dataset
import re

from .submodels.category_expense import CategoryExpense
from .submodels.user_profile import UserProfile
from .submodels.category import Category
from .submodels.household import Household
from .submodels.household_nationality import HouseholdNationality
from .submodels.nationality import Nationality
from .submodels.city import City
from .submodels.zone import Zone
from .submodels.sub_category import SubCategory
from .submodels.subcategory_expense import SubCategoryExpense
from .submodels.sub_sub_category import SubSubCategory
from .submodels.subsubcategory_expense import SubSubCategoryExpense
import logging


@csrf_exempt
@api_view(['GET', 'POST'])
def expense_upload(request):
    if request.method == 'GET':
        return HttpResponse("True")
    if request.method=='POST':
        dataset=Dataset()
        data=request.data
        new_file = data.get('file')
        book = xlrd.open_workbook(file_contents=new_file.read())

        sheet = book.sheet_by_index(0)
        #headers
        header_list=[]
        headers=sheet.row(0)
        for header_id, header in enumerate(headers):
            header_list.append({"header_id":header_id, "header":header.value})
        count = 0
        for rowid in range(1,sheet.nrows):
            try:
                row=sheet.row(rowid)
                category_data=[]
                subcategory_data=[]
                subsubcategory_data=[]
                for collid, cell in enumerate(row):
                    if collid == 1:
                        nationality_name=cell.value
                        nationality_obj = Nationality.objects.get(nationality__iexact=nationality_name)
                        nationality_id = nationality_obj.id
                    if collid == 2:
                        household_member=cell.value
                    if collid == 3:
                        city=cell.value
                        city_obj = City.objects.get(city__iexact=city)
                        city_id = city_obj.id
                    if collid == 4:
                        zone=str(int(cell.value))
                        zone_id = Zone.objects.get(zone=zone,city=city_obj).id
                    if collid == 6:
                        monthly_income = cell.value
                    if collid == 7:
                        year = cell.value
                    if collid == 8:
                        month = cell.value
                        # city = City.objects.get(city=city_name)
                        # city_id = city.id
                        # print(city_id)
                        count = count + 1
                        print("count ",count)

                    for header in header_list:
                        if header['header_id'] == collid:
                            category_header = header['header']
                            category_in = re.findall(r'\bcategory\b', category_header, re.IGNORECASE)
                            category_name=None
                            sub_category_name=None
                            sub_sub_category_name=None
                            if category_in != []:
                                remove_header_tag = re.compile(re.escape('category '), re.IGNORECASE)
                                category_name = remove_header_tag.sub('',category_header)
                                category_name = category_name.lstrip()
                                category_name = category_name.rstrip()
                                category_id=Category.objects.get(name__iexact=category_name).id
                                category_data.append({"id":category_id,"expense":cell.value})

                            sub_category_header=header['header']
                            subcategory_in = re.findall(r'^\bsub_category\b', sub_category_header, re.IGNORECASE)
                            if subcategory_in != []:
                                remove_header_tag = re.compile(re.escape('sub_category '),re.IGNORECASE)
                                sub_category_name = remove_header_tag.sub('',sub_category_header)
                                sub_category_name = sub_category_name.lstrip()
                                sub_category_name = sub_category_name.rstrip()
                                subcategory = SubCategory.objects.get(name__iexact = sub_category_name, category_id = category_id)
                                subcategory_data.append({"id":subcategory.id,"expense":cell.value,"category_id":subcategory.id})

                            sub_sub_category_header=header['header']
                            subsubcategory_in = re.findall(r'^\bsub_sub_category\b', sub_sub_category_header, re.IGNORECASE)
                            if subsubcategory_in != []:
                                remove_header_tag = re.compile(re.escape('sub_sub_category '),re.IGNORECASE)
                                sub_sub_category_name = remove_header_tag.sub('',sub_sub_category_header)
                                sub_sub_category_name = sub_sub_category_name.lstrip()
                                sub_sub_category_name = sub_sub_category_name.rstrip()
                                subsubcategory = SubSubCategory.objects.get(name__iexact = sub_sub_category_name, sub_category_id=subcategory.id)
                                subsubcategory_data.append({"id":subsubcategory.id,"expense":cell.value,"subcategory_id":subsubcategory.sub_category_id})

                for category in category_data:
                    expense = CategoryExpense(
                        category_expense = category['expense'],
                        year = year,
                        month=month,
                        monthly_income=monthly_income,
                        category_id = category['id'],
                        city_id=city_id,
                        household_members=household_member,
                        nationality_id = nationality_id,
                        zone_id = zone_id
                    )
                    expense.save()

                for subcategory in subcategory_data:
                    sub_expense = SubCategoryExpense(
                        subcategory_expense = subcategory['expense'],
                        year = year,
                        month=month,
                        monthly_income=monthly_income,
                        sub_category_id = subcategory['id'],
                        city_id=city_id,
                        household_members=household_member,
                        nationality_id = nationality_id,
                        zone_id = zone_id
                    )

                    sub_expense.save()

                for subsubcategory in subsubcategory_data:
                    sub_sub_expense = SubSubCategoryExpense(
                        subsubcategory_expense = subsubcategory['expense'],
                        year = year,
                        month=month,
                        monthly_income=monthly_income,
                        sub_sub_category_id = subsubcategory['id'],
                        city_id=city_id,
                        household_members=household_member,
                        nationality_id = nationality_id,
                        zone_id = zone_id
                    )
                    sub_sub_expense.save()
            except Exception as e:
                error = None
                if category_name:
                    error = category_name
                if sub_category_name:
                    error = sub_category_name
                if sub_sub_category_name:
                    error = sub_sub_category_name
                return JsonResponse({'error':error})
                # print("category name ",category_name)
                # print("sub category name ",sub_category_name)
                # print("sub sub category name ",sub_sub_category_name)
                # return HttpResponse(category_name)

    return JsonResponse({'status':True})

@csrf_exempt
@api_view(['GET', 'POST'])
def household_upload(request):
    if request.method == 'GET':
        return HttpResponse("True")
    if request.method=='POST':
        # try:
        dataset=Dataset()
        data=request.data
        new_file = data.get('file')
        book = xlrd.open_workbook(file_contents=new_file.read())

        sheet = book.sheet_by_index(0)
        #headers
        header_list=[]
        headers=sheet.row(0)
        for header_id, header in enumerate(headers):
            header_list.append({"header_id":header_id, "header":header.value})
    
        for rowid in range(1,sheet.nrows):
            row=sheet.row(rowid)
            nationality_data=[]

            for collid, cell in enumerate(row):
                if collid == 0:#city
                    city=cell.value
                    print(city)
                    city = City.objects.get(city__iexact=city)
                    print("city ",city.city)
                if collid == 1:#zone
                    zone=str(int(cell.value))
                    print("zone ",zone)
                    zone_id = Zone.objects.get(zone=zone,city=city).id
                if collid == 2:#year
                    year = cell.value
                if collid == 3:#population
                    population=cell.value
                    # zone_id = Zone.objects.get(zone=zone).id
                if collid == 4:#number of households
                    households = cell.value
                if collid == 5:
                    family_percent = cell.value
                if collid == 6:
                    bachelor_percent = cell.value
                if collid == 7:
                    labourer_percent = cell.value
                if collid == 8:
                    first_half_year = cell.value
                    if first_half_year == 1:
                        first_half_year = True
                    else:
                        first_half_year = False
                if collid == 9:
                    second_half_year = cell.value
                    if second_half_year is not None or second_half_year != '':
                        if second_half_year == 1:
                            second_half_year = True
                        else:
                            second_half_year = False

                for header in header_list:
                    if header['header_id'] == collid:
                        nationality_header = header['header']
                        population_percent = cell.value
                        try:
                            nationality_id = Nationality.objects.get(nationality__iexact=nationality_header).id
                            nationality_data.append({"nationality_id":nationality_id, "population":population_percent})
                        except Exception as e:
                            pass
            _household=Household(
                city=city,
                year=year,
                population=population,
                household_number=households,
                zone_id=zone_id,
                family_percent=family_percent,
                bachelor_percent=bachelor_percent,
                labourer_percent=labourer_percent,
                first_half_year = first_half_year,
                second_half_year = second_half_year
            )
            _household.save()

            for nationality in nationality_data:
                hn = HouseholdNationality(
                    nationality_percentage=nationality['population'],
                    household=_household,
                    nationality_id=nationality['nationality_id']
                )
                hn.save()
            
        return HttpResponse("True")
        
        # except Exception as e:
        #     return HttpResponse("error")