from django.urls import path
from . import views

urlpatterns = [
  path('', views.index, name='recipe_index'),
  path('recipe/<int:recipe_id>/', views.show, name='recipe_show'),
  path('recipe/new/', views.recipe_new, name='recipe_new'),
  path('recipe/<int:recipe_id>/edit/', views.update_recipe, name='recipe_edit'),
  path('recipe/<int:recipe_id>/destroy', views.destroy_recipe, name='recipe_destroy'),
  path('recipe/<int:recipe_id>/ingredient/new', views.IngredientNew.as_view(), name='ingredient_new'),
  path('recipe/ingredient/<int:ingredient_id>/edit/', views.update_ingredient, name='ingredient_edit'),
  path('recip/ingredient/<int:ingredient_id>/destroy', views.destroy_ingredient, name='ingredient_destroy'),
]