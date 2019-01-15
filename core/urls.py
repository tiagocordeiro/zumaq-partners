from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('parceiros/add/', views.parceiro_cadastro, name='parceiro_cadastro'),
    path('parceiros/list/', views.parceiro_list, name='parceiro_list'),
]
