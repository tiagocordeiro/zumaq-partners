from django.urls import path

from . import views

urlpatterns = [
    path('product/<str:codigo>/', views.product_view, name='product_view'),
    path('product/create/<str:codigo>/', views.product_create, name='product_create'),
    path('product/update/<str:codigo>/', views.product_update, name='product_update'),
]
