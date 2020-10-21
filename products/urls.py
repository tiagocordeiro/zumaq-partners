from django.urls import path

from . import views

urlpatterns = [
    path('list/', views.product_list, name='product_list'),
    path('list/atacado/', views.product_atacado_list, name='product_list_atacado'),
    path('product/add/', views.product_add, name='product_add'),
    path('product/<str:codigo>/', views.product_view, name='product_view'),
    path('product/create/<str:codigo>/', views.product_create, name='product_create'),
    path('product/update/<str:codigo>/', views.product_update, name='product_update'),
    path('json/', views.product_list_json, name='product_list_json'),
    path('json/<str:codigo>/', views.product_detail_json, name='product_detail_json'),
]
