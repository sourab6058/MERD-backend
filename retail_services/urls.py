from django.urls import path
from . import views
from .upload_data import expense_upload, household_upload, city_reports, tourist_reports, download_brochure, delete_survey, delete_census, get_lastupdate

urlpatterns = [
    path('upload_data/', expense_upload, name='upload-data'),
    path('upload_census_data/', household_upload, name='upload-data-census'),
    path('city_reports/', city_reports, name='city-reports'),
    path('tourist_reports/', tourist_reports, name='tourist-reports'),
    path('brochurepdf/', download_brochure, name='download_brochure'),
    path('delete_survey/', delete_survey, name='delete_survey'),
    path('delete_census/', delete_census, name='delete_census'),
    path('lastupdate/', get_lastupdate, name='lastupdate'),
    path('demographic/', views.DemographicInfo.as_view(), name='demographic'),

    path('api/filter', views.FilterSecond.as_view(), name='filter-second'),
    path('cities', views.Cities.as_view(), name='cities'),
    path('categories', views.Categories.as_view(), name='categories'),
    # path('demographic_info/', views.DemographicInfo.as_view(), name='demographic'),
    path('catchments_info/malls/', views.MallsInfo.as_view(), name='catchments'),
    path('catchments_info/', views.CatchmentsInfo.as_view(), name='catchments'),
]
