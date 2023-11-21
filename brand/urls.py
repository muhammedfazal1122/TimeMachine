from django.urls import path
from . import views

app_name = 'brand'


urlpatterns = [

    path('admn_brand_list', views.admn_brand_list, name='admn_brand_list'),


]


