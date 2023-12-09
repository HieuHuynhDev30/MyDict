from django.urls import path

from . import views

app_name = 'lookup'

urlpatterns = [
    path('', views.lookup, name='lookup')
]
