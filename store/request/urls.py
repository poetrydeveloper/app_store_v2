from django.urls import path
from . import views

app_name = 'request'

urlpatterns = [
    # Страница заявок
    path('', views.requests_view, name='requests_list'),

    # Обновление статуса заявки (POST через AJAX)
    path('change_status/', views.change_status, name='requests_change_status'),
]