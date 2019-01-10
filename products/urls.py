from django.urls import path

from . import views

urlpatterns = [
    path('product/<str:codigo>/', views.view_product, name='view_product'),
]
