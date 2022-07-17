from django.core.files.storage import FileSystemStorage
from rest_framework.views import APIView
from django.http import JsonResponse, HttpResponse
import os
from django.conf import settings
from django.db.utils import IntegrityError
from wsgiref.util import FileWrapper

from retail_services.upload_data import read_date


from .submodels.category_expense import CategoryExpense
from .submodels.nationality import Nationality
from .submodels.city import City
from .submodels.category import Category
from .submodels.demographic_table import DemographicTable

from .serializers import CitySerializer, CategorySerializer

from .calculations import get_category_data, get_subcategory_data, get_subsubcategory_data, get_zones_consolidated_category_data, get_zones_consolidated_subcategory_data, get_zones_consolidated_subsubcategory_data, get_nationality_consolidated_category_data, get_nationality_consolidated_subcategory_data, get_nationality_consolidated_subsubcategory_data, get_population_count, get_nationality_distribution, get_income_level, get_category_capita, get_bachelors, get_labourers_percent, get_malls_data, get_cities_data, get_categories_data
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

        lastupdate = read_date()

        filter_list = []
        filter_list.append({"years": _years,
                            "months": _months,
                            "nationality": _nationalities,
                            "categories": CategorySerializer(categories, many=True).data,
                            "cities": CitySerializer(cities, many=True).data,
                            "date": lastupdate
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
        folder = "demographic_tables"
        table_id = request.GET.get("id", "")
        multiple_tables = request.GET.get("multiple_tables", "")
        print("multiple_tables", multiple_tables)

        if table_id:
            try:
                filepath = DemographicTable.objects.get(id=table_id).file_path
                print(filepath)
                excel_file = open(filepath, 'rb')
                response = HttpResponse(FileWrapper(
                    excel_file), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                return response
            except:
                return JsonResponse({"Error": "File does not exist"})
        elif multiple_tables:
            cities = request.GET.get("cities")
            print(cities)
            return JsonResponse({"cities": cities})
        else:
            excel_file_names = os.listdir(folder)
            print(excel_file_names)
            excel_files = []

            for file in excel_file_names:
                path = os.path.join(settings.MEDIA_ROOT, folder, file)
                id = DemographicTable.objects.get(file_path=path).id
                excel_files.append({"id": id, "file": file})

            return JsonResponse({"excel_files": excel_files})

    def post(self, request):
        folder = "demographic_tables"
        data = request.data
        if len(data) == 1:
            file_ids = data.get("files")
            for id in file_ids:
                dt = DemographicTable.objects.get(id=id)
                file_path = dt.file_path
                os.remove(file_path)
                dt.delete()
            return JsonResponse({"filesDeleted": data.get("files")})

        try:

            print(data)
            cities = data.get("cities")
            types = data.get("types")
            modes = data.get("displayModes")

            tables = []

            for city in cities:
                for type in types:
                    for mode in modes:
                        try:
                            dt = DemographicTable.objects.get(
                                city_id=city, type=type, mode=mode).id
                            tables.append({
                                "city": city,
                                "type": type,
                                "mode": mode,
                                "table_id": dt,
                                "message": "This is just id not table"
                            })
                        except:
                            tables.append({
                                "city": city,
                                "type": type,
                                "mode": mode,
                                "table_id": None,
                                "message": "No table with above attributes exists"
                            })
                            print("table for", city,
                                  type, mode, "does not exist")

            return JsonResponse({
                "data": tables
            })
        except:
            print("No multiple tables were asked")
            JsonResponse({"message": "No multiple tables were asked"})

        try:
            print("data ", data)
            city = int(data.get("city"))
            type = data.get("type")
            mode = data.get("mode")
            file = data.get("file")

            filename = f"{city}_{type}_{mode}.xlsx"
            try:
                dt = DemographicTable(
                    city_id=city,
                    type=type,
                    mode=mode,
                    file_path=os.path.join(
                        settings.MEDIA_ROOT, folder, filename)
                )
                dt.save()

                fs = FileSystemStorage(location=folder)

                fs.save(filename, file)
                file_url = fs.url(filename)
                print(folder+file_url)

                return JsonResponse({
                    'id': dt.id,
                    'file': filename
                })
            except IntegrityError:
                print("Error in uploading file")
                return JsonResponse({"Error": "File already exists in backend"})
        except:
            print("No file uploading asked")
            return JsonResponse({"msg": "No file uploading asked"})
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


class MallsInfo(APIView):
    folder = "maps"

    def get(self, request):
        mall_map = request.GET.get("mall_map")
        files = request.GET.get("files")
        if mall_map:
            try:
                filename = f"{mall_map}.pdf"
                filepath = os.path.join(
                    settings.MEDIA_ROOT, self.folder, filename)
                excel_file = open(filepath, 'rb')
                response = HttpResponse(FileWrapper(
                    excel_file), content_type='application/pdf')
                return response
            except:
                return JsonResponse({"Error": "No Such Map exists"})
        if files:
            print("files asked")
            mall_file_names = os.listdir(self.folder)
            print(mall_file_names)
            return JsonResponse({"files": mall_file_names})
        malls = []
        malls_data = get_malls_data()
        for mall in malls_data:
            if mall["name"] not in malls:
                malls.append(mall["name"])

        return JsonResponse({"malls": malls})

    def post(self, request):
        data = request.data
        print("data ", data)

        files = data.get("files")

        if files:
            for file in files:
                file_path = os.path.join(self.folder, file)
                os.remove(file_path)
            return JsonResponse({"files": files})

        mall = data.get("mall")
        file = data.get("file")

        filename = f"{mall}.pdf"

        fs = FileSystemStorage(location=self.folder)

        fs.save(filename, file)
        file_url = fs.url(filename)
        print(self.folder+file_url)

        mall_file_names = os.listdir(self.folder)
        print(mall_file_names)
        return JsonResponse({"files": mall_file_names})


class Cities(APIView):
    def get(self, _):
        cities = get_cities_data()
        return JsonResponse({"data": cities})


class Categories(APIView):
    def get(self, _):
        categories = get_categories_data()
        return JsonResponse({"data": categories})
