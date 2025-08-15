from django.urls import path
from . import views

app_name = 'unit'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('main/', views.main_view, name='main'),
]