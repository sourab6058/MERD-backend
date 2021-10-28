from rest_framework import serializers
from .submodels.city import City
from .submodels.zone import Zone
from .submodels.category import Category
from .submodels.sub_category import SubCategory
from .submodels.sub_sub_category import SubSubCategory
from .submodels.mall import Mall


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ("id", "zone")


class CitySerializer(serializers.ModelSerializer):
    zone = ZoneSerializer(source="city_name", many=True)

    class Meta:
        model = City
        fields = ("id", "city", 'zone')


class SubSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubSubCategory
        fields = ('id', 'name')


class SubCategorySerializer(serializers.ModelSerializer):
    sub_sub_category = SubSubCategorySerializer(
        source="sub_category", many=True)

    class Meta:
        model = SubCategory
        fields = ('id', 'name', 'sub_sub_category')


class CategorySerializer(serializers.ModelSerializer):
    sub_category = SubCategorySerializer(source="category", many=True)

    class Meta:
        model = Category
        fields = ('id', 'name', 'sub_category')


class MallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mall
        fields = ('id', 'name', 'zone')
