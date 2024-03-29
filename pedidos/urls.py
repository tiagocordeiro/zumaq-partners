from django.urls import path

from . import views

urlpatterns = [
    path('add/<str:codigo>/', views.pedido_add_item, name='pedido_add_item'),
    path('add/atacado/<str:codigo>/<int:quantidade>/', views.pedido_add_item_atacado, name='pedido_add_item_atacado'),
    path('aberto/', views.pedido_aberto, name='pedido_aberto'),
    path('checkout/<pk>/', views.pedido_checkout, name='pedido_checkout'),
    path('details/<pk>/', views.pedido_details, name='pedido_details'),
    path('export/pdf/<pk>/', views.pedido_export_pdf, name='pedido_export_pdf'),
    path('export/pdf/deliveryterm/<pk>/', views.pedido_delivery_term_pdf, name='pedido_export_delivery_term_pdf'),
    path('export/pdf/completo/<pk>/', views.pedido_delivery_term_with_order_pdf, name='pedido_export_complete_pdf'),
    path('list/', views.pedidos_list, name='pedidos_list'),
    path('list/separacao/', views.pedidos_list_separacao, name='pedidos_list_separacao'),
    path('list/separados/', views.pedidos_list_separados, name='pedidos_list_separados'),
    path('separacao/<pk>/', views.pedido_separacao, name='pedido_separacao'),
]
