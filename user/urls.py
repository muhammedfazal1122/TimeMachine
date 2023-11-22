from django.urls import path
from . import views
app_name = 'user'


urlpatterns = [
    path('manage_address/', views.manage_address, name='manage_address'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('add_address/', views.add_address, name='add_address'),
    path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
    path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),

    path('admn_sales_report/', views.admn_sales_report, name='admn_sales_report'),

]
