from django.urls import path

from . import views

urlpatterns = [
    path('products/list/', views.product_list, name='product_list'),
    path('products/list/atacado/', views.product_atacado_list, name='product_list_atacado'),
    path('products/product/add/', views.product_add, name='product_add'),
    path('products/product/<str:codigo>/', views.product_view, name='product_view'),
    path('products/product/create/<str:codigo>/', views.product_create, name='product_create'),
    path('products/product/update/<str:codigo>/', views.product_update, name='product_update'),
    path('products/json/', views.product_list_json, name='product_list_json'),
    path('products/json/<str:codigo>/', views.product_detail_json, name='product_detail_json'),
    path('products/json/public/<str:secret_key>/', views.api_product_list, name='api_product_list'),
    path('products/json/public/<str:codigo>/<str:secret_key>/', views.api_product_detail, name='api_product_detail'),
    path('api/products/', views.api_product_list_header_token, name='api_product_list_header_token'),
    path('api/product/<str:codigo>/', views.api_product_detail_header_token, name='api_product_detail_header_token'),
]
