import itertools
from django.forms import model_to_dict
from django.http import JsonResponse
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from wsgiref.util import FileWrapper
from rest_framework.views import APIView
from rest_framework.decorators import api_view

import xlrd
from tablib import Dataset
import re
import os

from retail_services.calculations import read_date, update_date

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
    if request.method == 'POST':
        print("POST")
        dataset = Dataset()
        data = request.data
        new_file = data.get('file')
        book = xlrd.open_workbook(file_contents=new_file.read())

        sheet = book.sheet_by_index(0)
        # headers
        header_list = []
        headers = sheet.row(0)
        for header_id, header in enumerate(headers):
            header_list.append(
                {"header_id": header_id, "header": header.value})
        count = 0
        for rowid in range(1, sheet.nrows):
            try:
                row = sheet.row(rowid)
                category_data = []
                subcategory_data = []
                subsubcategory_data = []
                spent_online_category_data = []
                spent_online_sub_category_data = []
                spent_online_sub_sub_category_data = []
                spent_incity_category_data = []
                spent_incity_sub_category_data = []
                spent_incity_sub_sub_category_data = []

                for collid, cell in enumerate(row):
                    if collid == 1:
                        nationality_name = cell.value
                        nationality_obj = Nationality.objects.get(
                            nationality__iexact=nationality_name)
                        print(nationality_name)
                        nationality_id = nationality_obj.id
                    if collid == 2:
                        household_member = cell.value
                    if collid == 3:
                        city = cell.value
                        city_obj = City.objects.get(city__iexact=city)
                        city_id = city_obj.id
                    if collid == 4:
                        zone = str(cell.value)
                        zone_id = Zone.objects.get(zone=zone, city=city_obj).id
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
                        print("count ", count)

                    for header in header_list:
                        if header['header_id'] == collid:
                            spent_online_category_header = header['header']
                            spent_online_category_in = re.findall(
                                r'^\bspent_online_category\b', spent_online_category_header, re.IGNORECASE)
                            if spent_online_category_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('spent_online_category '), re.IGNORECASE)
                                category_name = remove_header_tag.sub(
                                    '', spent_online_category_header)
                                print(category_name)
                                category_name = category_name.lstrip()
                                category_name = category_name.rstrip()
                                category_id = Category.objects.get(
                                    name__iexact=category_name).id
                                spent_online_category_data.append(
                                    {"id": category_id, "spent_online": cell.value})

                            spent_online_sub_category_header = header['header']
                            spent_online_sub_category_in = re.findall(
                                r'^\bspent_online_sub_category\b', spent_online_sub_category_header, re.IGNORECASE)
                            if spent_online_sub_category_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('spent_online_sub_category '), re.IGNORECASE)
                                sub_category_name = remove_header_tag.sub(
                                    '', spent_online_sub_category_header)
                                print(sub_category_name)
                                sub_category_name = sub_category_name.lstrip()
                                sub_category_name = sub_category_name.rstrip()
                                sub_category_id = SubCategory.objects.get(
                                    name__iexact=sub_category_name, category_id=category_id).id
                                spent_online_sub_category_data.append(
                                    {"id": sub_category_id, "spent_online": cell.value})

                            spent_online_sub_sub_category_header = header['header']
                            spent_online_sub_sub_category_in = re.findall(
                                r'^\bspent_online_sub_sub_category\b', spent_online_sub_sub_category_header, re.IGNORECASE)
                            if spent_online_sub_sub_category_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('spent_online_sub_sub_category '), re.IGNORECASE)
                                sub_sub_category_name = remove_header_tag.sub(
                                    '', spent_online_sub_sub_category_header)
                                print(sub_sub_category_name)
                                sub_sub_category_name = sub_sub_category_name.lstrip()
                                sub_sub_category_name = sub_sub_category_name.rstrip()
                                sub_sub_category_id = SubSubCategory.objects.get(
                                    name__iexact=sub_sub_category_name, sub_category_id=sub_category_id).id
                                spent_online_sub_sub_category_data.append(
                                    {"id": sub_sub_category_id, "spent_online": cell.value})

                            spent_incity_category_header = header['header']
                            spent_incity_category_in = re.findall(
                                r'^\bspent_incity_category\b', spent_incity_category_header, re.IGNORECASE)
                            if spent_incity_category_in != []:
                                print(spent_incity_category_header)
                                remove_header_tag = re.compile(
                                    re.escape('spent_incity_category '), re.IGNORECASE)
                                category_name = remove_header_tag.sub(
                                    '', spent_incity_category_header)
                                print(category_name)
                                category_name = category_name.lstrip()
                                category_name = category_name.rstrip()
                                category_id = Category.objects.get(
                                    name__iexact=category_name).id
                                print(category_id)
                                spent_incity_category_data.append(
                                    {"id": category_id, "spent_incity": cell.value})

                            spent_incity_sub_category_header = header['header']
                            spent_incity_sub_category_in = re.findall(
                                r'^\bspent_incity_sub_category\b', spent_incity_sub_category_header, re.IGNORECASE)
                            if spent_incity_sub_category_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('spent_incity_sub_category '), re.IGNORECASE)
                                sub_category_name = remove_header_tag.sub(
                                    '', spent_incity_sub_category_header)
                                print(sub_category_name)
                                sub_category_name = sub_category_name.lstrip()
                                sub_category_name = sub_category_name.rstrip()
                                sub_category_id = SubCategory.objects.get(
                                    name__iexact=sub_category_name, category_id=category_id).id
                                spent_incity_sub_category_data.append(
                                    {"id": sub_category_id, "spent_incity": cell.value})

                            spent_incity_sub_sub_category_header = header['header']
                            spent_incity_sub_sub_category_in = re.findall(
                                r'^\bspent_incity_sub_sub_category\b', spent_incity_sub_sub_category_header, re.IGNORECASE)
                            if spent_incity_sub_sub_category_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('spent_incity_sub_sub_category '), re.IGNORECASE)
                                sub_sub_category_name = remove_header_tag.sub(
                                    '', spent_incity_sub_sub_category_header)
                                print(sub_sub_category_name)
                                sub_sub_category_name = sub_sub_category_name.lstrip()
                                sub_sub_category_name = sub_sub_category_name.rstrip()
                                sub_sub_category_id = SubSubCategory.objects.get(
                                    name__iexact=sub_sub_category_name, sub_category_id=sub_category_id).id
                                spent_incity_sub_sub_category_data.append(
                                    {"id": sub_sub_category_id, "spent_incity": cell.value})

                    for header in header_list:
                        if header['header_id'] == collid:
                            category_header = header['header']
                            category_in = re.findall(
                                r'\bcategory\b', category_header, re.IGNORECASE)

                            category_name = None
                            sub_category_name = None
                            sub_sub_category_name = None
                            if category_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('category '), re.IGNORECASE)
                                category_name = remove_header_tag.sub(
                                    '', category_header)
                                category_name = category_name.lstrip()
                                category_name = category_name.rstrip()
                                print(category_name)
                                category_id = Category.objects.get(
                                    name__iexact=category_name).id
                                category_spent_online = 0
                                # for header in header_list:

                                category_data.append(
                                    {"id": category_id, "expense": cell.value})

                            sub_category_header = header['header']
                            subcategory_in = re.findall(
                                r'^\bsub_category\b', sub_category_header, re.IGNORECASE)
                            if subcategory_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('sub_category '), re.IGNORECASE)
                                sub_category_name = remove_header_tag.sub(
                                    '', sub_category_header)
                                sub_category_name = sub_category_name.lstrip()
                                sub_category_name = sub_category_name.rstrip()
                                print(sub_category_name)
                                subcategory = SubCategory.objects.get(
                                    name__iexact=sub_category_name, category_id=category_id)
                                subcategory_data.append(
                                    {"id": subcategory.id, "expense": cell.value, "category_id": category_id})

                            sub_sub_category_header = header['header']
                            subsubcategory_in = re.findall(
                                r'^\bsub_sub_category\b', sub_sub_category_header, re.IGNORECASE)
                            if subsubcategory_in != []:
                                remove_header_tag = re.compile(
                                    re.escape('sub_sub_category '), re.IGNORECASE)
                                sub_sub_category_name = remove_header_tag.sub(
                                    '', sub_sub_category_header)
                                sub_sub_category_name = sub_sub_category_name.lstrip()
                                sub_sub_category_name = sub_sub_category_name.rstrip()
                                print(sub_sub_category_name)
                                subsubcategory = SubSubCategory.objects.get(
                                    name__iexact=sub_sub_category_name, sub_category_id=subcategory.id)
                                subsubcategory_data.append(
                                    {"id": subsubcategory.id, "expense": cell.value, "subcategory_id": subsubcategory.sub_category_id})
                print(spent_incity_category_data)
                for category in category_data:
                    for category_spent_online in spent_online_category_data:
                        for category_spent_incity in spent_incity_category_data:
                            if category["id"] == category_spent_online["id"] == category_spent_incity["id"]:
                                expense = CategoryExpense(
                                    category_expense=category['expense'],
                                    spent_online=category_spent_online["spent_online"],
                                    spent_incity=category_spent_incity["spent_incity"],
                                    year=year,
                                    month=month,
                                    monthly_income=monthly_income,
                                    category_id=category['id'],
                                    city_id=city_id,
                                    household_members=household_member,
                                    nationality_id=nationality_id,
                                    zone_id=zone_id
                                )
                                expense.save()
                                # print("catg")

                for subcategory in subcategory_data:
                    for sub_category_spent_online in spent_online_sub_category_data:
                        for sub_category_spent_incity in spent_incity_sub_category_data:
                            if sub_category_spent_online["id"] == subcategory["id"] == sub_category_spent_incity["id"]:
                                sub_expense = SubCategoryExpense(
                                    subcategory_expense=subcategory['expense'],
                                    spent_online=sub_category_spent_online["spent_online"],
                                    spent_incity=sub_category_spent_incity["spent_incity"],
                                    year=year,
                                    month=month,
                                    monthly_income=monthly_income,
                                    sub_category_id=subcategory['id'],
                                    city_id=city_id,
                                    household_members=household_member,
                                    nationality_id=nationality_id,
                                    zone_id=zone_id
                                )
                                sub_expense.save()
                                # print("subcatg")

                for subsubcategory in subsubcategory_data:
                    for sub_sub_category_spent_online in spent_online_sub_sub_category_data:
                        for sub_sub_category_spent_incity in spent_incity_sub_sub_category_data:
                            if sub_sub_category_spent_online["id"] == subsubcategory["id"] == sub_sub_category_spent_incity["id"]:
                                sub_sub_expense = SubSubCategoryExpense(
                                    subsubcategory_expense=subsubcategory['expense'],
                                    spent_online=sub_sub_category_spent_online["spent_online"],
                                    spent_incity=sub_sub_category_spent_incity["spent_incity"],
                                    year=year,
                                    month=month,
                                    monthly_income=monthly_income,
                                    sub_sub_category_id=subsubcategory['id'],
                                    city_id=city_id,
                                    household_members=household_member,
                                    nationality_id=nationality_id,
                                    zone_id=zone_id
                                )
                                sub_sub_expense.save()
                                # print("subsubcatg")
            except Exception as e:
                print(e)
                error = None
                if category_name:
                    error = category_name
                if sub_category_name:
                    error = sub_category_name
                if sub_sub_category_name:
                    error = sub_sub_category_name
                return JsonResponse({'error': error})
                # print("category name ",category_name)
                # print("sub category name ",sub_category_name)
                # print("sub sub category name ",sub_sub_category_name)
                # return HttpResponse(category_name)

    return JsonResponse({'status': True})


@csrf_exempt
@api_view(['GET', 'POST'])
def household_upload(request):
    if request.method == 'GET':
        return HttpResponse("True")
    if request.method == 'POST':
        # try:
        dataset = Dataset()
        data = request.data
        new_file = data.get('file')
        book = xlrd.open_workbook(file_contents=new_file.read())

        sheet = book.sheet_by_index(0)
        # headers
        header_list = []
        headers = sheet.row(0)
        for header_id, header in enumerate(headers):
            header_list.append(
                {"header_id": header_id, "header": header.value})

        for rowid in range(1, sheet.nrows):
            row = sheet.row(rowid)
            nationality_data = []

            for collid, cell in enumerate(row):
                if collid == 0:  # city
                    city = cell.value
                    print(city)
                    city = City.objects.get(city__iexact=city)
                    print("city ", city.city)
                if collid == 1:  # zone
                    zone = str(cell.value)
                    print("zone ", zone)
                    zone_id = Zone.objects.get(zone=zone, city=city).id
                if collid == 2:  # year
                    year = cell.value
                if collid == 3:  # population
                    population = cell.value
                    # zone_id = Zone.objects.get(zone=zone).id
                if collid == 4:  # number of households
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
                            nationality_id = Nationality.objects.get(
                                nationality__iexact=nationality_header).id
                            nationality_data.append(
                                {"nationality_id": nationality_id, "population": population_percent})
                        except Exception as e:
                            pass
            _household = Household(
                city=city,
                year=year,
                population=population,
                household_number=households,
                zone_id=zone_id,
                family_percent=family_percent,
                bachelor_percent=bachelor_percent,
                labourer_percent=labourer_percent,
                first_half_year=first_half_year,
                second_half_year=second_half_year
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


@csrf_exempt
@api_view(['GET', 'POST'])
def city_reports(request):
    folder = 'reports/city_reports'
    folder_path = os.path.join(settings.MEDIA_ROOT, folder)
    if request.method == "GET":
        filename = request.GET.get('filename', '')
        if filename == 'all-files':
            reports = os.listdir(folder_path)
            print(reports)
            return JsonResponse({"reports": reports})
        else:
            filepath = os.path.join(settings.MEDIA_ROOT, folder, filename)
            print(filepath)
            short_report = open(filepath, 'rb')
            response = HttpResponse(FileWrapper(
                short_report), content_type='application/pdf')
            return response
    if request.method == "POST":
        data = request.data
        if data.get("operation") == 'delete':
            files_to_delete = data.get('filesToDelete')
            for file in files_to_delete:
                filepath = os.path.join(settings.MEDIA_ROOT, folder, file)
                os.remove(filepath)
            return JsonResponse({"reports": os.listdir(folder_path)})

        else:
            pdf_file = data.get("file")
            print(pdf_file.name)
            fs = FileSystemStorage(location=folder)
            filename = fs.save(pdf_file.name, pdf_file)
            file_url = fs.url(filename)
            print(folder+file_url)
            return JsonResponse({"filename": pdf_file.name})


@csrf_exempt
@api_view(['GET', 'POST'])
def tourist_reports(request):
    folder = 'reports/tourist_reports'
    folder_path = os.path.join(settings.MEDIA_ROOT, folder)
    if request.method == "GET":
        filename = request.GET.get('filename', '')
        if filename == 'all-files':
            reports = os.listdir(folder_path)
            print(reports)
            return JsonResponse({"reports": reports})
        else:
            filepath = os.path.join(settings.MEDIA_ROOT, folder, filename)
            print(filepath)
            short_report = open(filepath, 'rb')
            response = HttpResponse(FileWrapper(
                short_report), content_type='application/pdf')
            return response
    if request.method == "POST":
        data = request.data
        if data.get("operation") == 'delete':
            files_to_delete = data.get('filesToDelete')
            for file in files_to_delete:
                filepath = os.path.join(settings.MEDIA_ROOT, folder, file)
                os.remove(filepath)
            return JsonResponse({"reports": os.listdir(folder_path)})

        else:
            pdf_file = data.get("file")
            print(pdf_file.name)
            fs = FileSystemStorage(location=folder)
            filename = fs.save(pdf_file.name, pdf_file)
            file_url = fs.url(filename)
            print(folder+file_url)
            return JsonResponse({"filename": pdf_file.name})


@csrf_exempt
@api_view(['GET', 'POST'])
def download_brochure(request):
    folder = "brochure"
    filename = "brochure.pdf"
    if request.method == "GET":
        filepath = os.path.join(settings.MEDIA_ROOT, folder, filename)
        print(filepath)
        brochure_doc = open(filepath, 'rb')
        response = HttpResponse(FileWrapper(
            brochure_doc), content_type='application/pdf')
        return response


@csrf_exempt
@api_view(['GET', 'POST'])
def delete_survey(request):
    print(request.data)
    cities = request.data["cities"]
    zones = request.data["zones"]
    years = request.data["years"]
    months = request.data["months"]
    categories = request.data["categories"]
    subCategories = request.data["subCategories"]
    subSubCategories = request.data["subSubCategories"]
    nationalities = request.data["nationalities"]
    delete_args = {}
    if len(cities) > 0:
        delete_args['city_id__in'] = cities
    if len(zones) > 0:
        delete_args['zone__in'] = zones
    if len(years) > 0:
        delete_args['year__in'] = years
    if len(months) > 0:
        delete_args['month__in'] = months
    if len(nationalities) > 0:
        delete_args['nationality__in'] = nationalities

    cat_expenses = []
    sub_cat_expenses = []
    sub_sub_cat_expenses = []
    if len(categories) > 0:
        cat_expenses = CategoryExpense.objects.filter(
            **delete_args, category__in=categories)
        cat_expenses.delete()

    if len(subCategories) > 0:
        sub_cat_expenses = SubCategoryExpense.objects.filter(
            **delete_args, sub_category__in=subCategories)
        sub_cat_expenses.delete()
    if len(subSubCategories) > 0:
        sub_sub_cat_expenses = SubSubCategoryExpense.objects.filter(
            **delete_args, sub_sub_category__in=subSubCategories)
        sub_sub_cat_expenses.delete()
    if len(categories) == 0 and len(subCategories) == 0 and len(subSubCategories) == 0:
        cat_expenses = CategoryExpense.objects.filter(
            **delete_args)
        cat_expenses.delete()
        sub_cat_expenses = SubCategoryExpense.objects.filter(
            **delete_args)
        sub_cat_expenses.delete()
        sub_sub_cat_expenses = SubSubCategoryExpense.objects.filter(
            **delete_args)
        sub_sub_cat_expenses.delete()

    return JsonResponse({"data": "success"})


@csrf_exempt
@api_view(['GET', 'POST'])
def delete_census(request):
    cities = request.data["cities"]
    zones = request.data["zones"]
    categories = request.data["categories"]
    subCategories = request.data["subCategories"]
    subSubCategories = request.data["subSubCategories"]
    nationalities = request.data["nationalities"]
    for zone in zones:
        zone_data = Zone.objects.get(pk=zone)
        zone_data.delete()
    for nationality in nationalities:
        nat_data = Nationality.objects.get(pk=nationality)
        nat_data.delete()
    for city in cities:
        city_data = City.objects.get(pk=city)
        city_data.delete()

    for category in categories:
        cat_data = Category.objects.get(pk=category)
        cat_data.delete()

    for subcat in subCategories:
        subcat_data = SubCategory.objects.get(pk=subcat)
        subcat_data.delete()

    for subsubcat in subSubCategories:
        subsubcat_data = SubSubCategory.objects.get(pk=subsubcat)
        subsubcat_data.delete()

    tmpstmp = update_date()

    return JsonResponse({"data": "success", "date": tmpstmp})


def get_lastupdate(_):
    tmstmp = read_date()
    return JsonResponse({"lastupdate": tmstmp})
