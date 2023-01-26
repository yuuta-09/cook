from django.urls import path, include
from . import views

urlpatterns = [
  path('', views.top, name='home_top'),
]
