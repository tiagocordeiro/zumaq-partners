from django.urls import path

from . import views

urlpatterns = [
    path('', views.reports_dashboard, name='dashboard_report'),
    path('products/', views.products_report, name='products_report_all'),
    path('products/<str:status>/', views.products_report, name='products_report'),
    path('products/download/xls/', views.download_excel_products_data, name='products_excel_report'),
    path('pedidos/', views.pedidos_report, name='pedidos_report_all'),
    path('pedidos/<str:status>/', views.pedidos_report, name='pedidos_report'),
    path('parceiros/', views.parceiros_report, name='parceiros_report_all'),
]
