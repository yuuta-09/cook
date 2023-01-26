from django.urls import path
from . import views

urlpatterns = [
  path('my-page', views.my_page, name="user_my_page"),
]