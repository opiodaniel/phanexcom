from django.urls import path

from bsheet import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sort_by_month/', views.sort_by_month, name='sort_by_month'),
    path('record_amount/', views.record_amount, name='record_amount'),
]

