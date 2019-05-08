from django.urls import path

from . import views

urlpatterns = [
    path('products/', views.products_report, name='products_report_all'),
    path('products/<str:status>/', views.products_report, name='products_report'),
    path('dashboard/', views.reports_dashboard, name='dashboard_report'),
]
