from django.urls import path

from . import views

urlpatterns = [
    path('add/<str:codigo>/', views.pedido_add_item, name='pedido_add_item'),
    path('aberto/', views.pedido_aberto, name='pedido_aberto'),
    path('checkout/<pk>/', views.pedido_checkout, name='pedido_checkout'),
    path('details/<pk>/', views.pedido_details, name='pedido_details'),
    path('export/pdf/<pk>/', views.pedido_export_pdf, name='pedido_export_pdf'),
    path('export/pdf/deliveryterm/<pk>/', views.pedido_delivery_term_pdf, name='pedido_export_delivery_term_pdf'),
    path('list/', views.pedidos_list, name='pedidos_list'),
]
