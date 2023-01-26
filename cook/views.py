from django.shortcuts import render, redirect
from django.http import Http404
from cook.models import Recipe, Ingredient

def index(request):
  param = {
    "recipes": Recipe.objects.all()
  }
  
  return render(request, "cook/index.html", param)


def show(request, recipe_id):
  try:
    recipe = Recipe.objects.get(pk=recipe_id)
  except Recipe.DoesNotExist:
    raise Http404("Recipe does not exist.")
  
  param = {
    'recipe': recipe
  }
  
  return render(request, "cook/show.html", param)


def new(request):
  if request.method == 'POST':
    recipe = Recipe(name=request.POST['recipe_name'], description=request.POST['recipe_description'], user=request.user)
    recipe.save()
    
    # ingredientを複数登録
    ingredient = Ingredient(name=request.POST['ingredient_name'], amount=request.POST['ingredient_amount'], recipe=recipe)
    
    # paramsに渡す全てのingredient
    ingredients = Ingredient.objects.filter(recipe=recipe)
    
    params = {
      'recipe': recipe,
      'ingredients': ingredients
    }
    
    return render(request, "show.html", params)
  
  return render(request, "cook/new.html")


def update_recipe(request, recipe_id):
  try:
    recipe = Recipe.objects.get(pk=recipe_id)
  except Recipe.DoesNotExist:
    raise Http404("Recipe does not exist.")
  
  if request.method == 'POST':
    recipe.name = request.POST['name']
    recipe.description = request.POST['description']
    recipe.save()
  
  param = {
    'recipe': recipe
  }
  
  return render(request, "cook/edit.html", param)


def update_ingredient(request, ingredient_id):
  try:
    ingredient = Ingredient.objects.get(pk=ingredient_id)
  except Ingredient.DoesNotExist:
    raise Http404("Ingredient does not exist.")
  
  if request.method == 'POST':
    ingredient.name = request.POST['name']
    ingredient.amout = request.POST['amount']
    ingredient.save()
    return redirect('recipe_show', ingredient.recipe.id)
  
  return render("cook/ingredient/edit.html")