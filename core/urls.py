from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('parceiros/cadastro/', views.parceiro_cadastro, name='parceiro_cadastro'),
    path('parceiros/new/', views.parceiro_create, name='parceiro_create'),
    path('parceiros/list/', views.parceiro_list, name='parceiro_list'),
    path('parceiros/details/<pk>/', views.parceiro_details, name='parceiro_details'),
    path('parceiros/blocked/<pk>/', views.parceiro_blocked_details, name='parceiro_blocked_details'),
]
