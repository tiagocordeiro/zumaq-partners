from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/update/', views.profile_update, name='profile_update'),
]
