from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='recipe_index'),
  path('recipe/<int:recipe_id>/', views.show, name='recipe_show'),
  path('recipe/new/', views.new, name='recipe_new'),
  path('recipe/<int:recipe_id>/edit/', views.update_recipe, name='recipe_edit'),
  path('recipe/<int:ingredient_id>/edit/', views.update_ingredient),
]