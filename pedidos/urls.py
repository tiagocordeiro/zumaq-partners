from django.urls import path

from . import views

urlpatterns = [
    path('add/<str:codigo>', views.pedido_add_item, name='pedido_add_item'),
]
