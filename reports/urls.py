from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.products_report, name='products_report'),
]
