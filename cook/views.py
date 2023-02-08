from django.shortcuts import render, redirect
from django.http import Http404
from cook.models import Recipe, Ingredient
from django.forms import inlineformset_factory
from cook.forms import IngredientForm
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import FormView
from django.urls import reverse
from django import forms


# recipe
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
  
  params = {
    'recipe': recipe,
    'ingredients': recipe.ingredients.all()
  }
  
  return render(request, "cook/show.html", params)


@login_required
def recipe_new(request):
  if request.method == 'POST':
    recipe = Recipe(name=request.POST['name'], description=request.POST['description'].rstrip(), user=request.user)
    recipe.save()
    
    return redirect("recipe_show", recipe.id)
  
  return render(request, "cook/new.html")


@login_required
def update_recipe(request, recipe_id):
  try:
    recipe = Recipe.objects.get(pk=recipe_id)
  except Recipe.DoesNotExist:
    raise Http404("Recipe does not exist.")
  
  if request.method == 'POST':
    recipe.name = request.POST['name']
    recipe.description = request.POST['description'].rstrip()
    if check_user(request, recipe.user):
      recipe.save()
    else:
      return render(request, 'error/http401.html', {'errors': ['投稿者のみが投稿できます。']}, status=401)
    return redirect('recipe_show', recipe.id)
  
  
  param = {
    'recipe': recipe
  }
  
  return render(request, "cook/edit.html", param)


@login_required
def destroy_recipe(request, recipe_id):
  try:
    recipe = Recipe.objects.get(pk=recipe_id)
  except Ingredient.DoesNotExist:
    raise Http404("Recipe does not exist.")
  
  if request.method == 'POST':
    if check_user(request, recipe.user):
      recipe.delete()
    else:
      return render(request, 'error/http401.html', {'errors': ['投稿者のみが削除できます。']}, status=401)
    
  return redirect('recipe_index')


# ingredient
FORM_VALUES = {}
INGREDIENT_FORM_NUMBER = 3


class IngredientNew(FormView):
  def get_success_url(self):
    return reverse('ingredient_new', kwargs={'recipe_id': self.kwargs['recipe_id']})

  def get_recipe(self):
    recipe = Recipe.objects.get(self.kwargs['recipe_id'])
    return recipe

  def get_data(self):
    return self.request.POST

  template_name = 'cook/ingredient/new.html'
  recipe = get_recipe
  success_url = get_success_url
  IngredientFormSet = inlineformset_factory(
    parent_model=Recipe,
    model=Ingredient,
    form=IngredientForm,
    extra=3,
    max_num=10,
  )
  form_class=IngredientFormSet

  def get_form_kwargs(self, *args, **kwargs):
    kwargs = super().get_form_kwargs(*args, **kwargs)
    print(FORM_VALUES)
    if FORM_VALUES:
      kwargs['data'] = FORM_VALUES
    return kwargs

  def post(self, request, *args, **kwargs):
    global FORM_VALUES
    global INGREDIENT_FORM_NUMBER
    if 'button_add' in request.POST:
      INGREDIENT_FORM_NUMBER += 1
      FORM_VALUES = request.POST.copy()
      FORM_VALUES['ingredients-TOTAL_FORMS'] = INGREDIENT_FORM_NUMBER
      print(FORM_VALUES)
    elif 'button_reset' in request.POST:
      INGREDIENT_FORM_NUMBER = 3
      FORM_VALUES['ingredients-TOTAL_FORMS'] = INGREDIENT_FORM_NUMBER
    else:
      formset = self.form_class(data=self.request.POST, instance = self.recipe, queryset=Ingredient.objects.none())
      if formset.is_valid():
        if check_user(request, self.recipe.user):
          formset.save()
        else:
          return render(request, 'error/http401.html', {'errors': ['投稿者のみが材料を追加できます。']}, status=401)
      else:
        return Http404("Error.")
      return redirect('recipe_show', self.kwargs['recipe_id'])
    return super().post(request, args, kwargs)


@login_required
def ingredient_new(request, recipe_id):
  recipe = Recipe.objects.get(pk=recipe_id)
  IngredientFormSet = inlineformset_factory(parent_model=Recipe, model=Ingredient, form=IngredientForm, extra=10)
  if request.method == 'POST':
    formset = IngredientFormSet(data=request.POST, instance=recipe,queryset=Ingredient.objects.none())  
    if formset.is_valid():
      if check_user(request, recipe.user):
        formset.save()
      else:
        return render(request, 'error/http401.html', {'errors': ['投稿者のみが材料の追加をできます。']}, status=401)
      return redirect("recipe_show", recipe.id)
    else:
      raise Http404("error")

  else:
    formset = IngredientFormSet(instance=recipe, queryset=Ingredient.objects.none())

  params = {
    'recipe': recipe,
    'formset': formset
  }

  return render(request, "cook/ingredient/new.html", params)


@login_required
def update_ingredient(request, ingredient_id):
  try:
    ingredient = Ingredient.objects.get(pk=ingredient_id)
  except Ingredient.DoesNotExist:
    raise Http404("Ingredient does not exist.")

  if request.method == 'POST':
    ingredient.name = request.POST['name']
    ingredient.amout = request.POST['amount']
    if check_user(request, published_user=ingredient.recipe.user):
      ingredient.save()
    else:
      return render(request, 'error/http401.html', {'errors': ['投稿者のみが材料の更新ができます。']}, status=401)
    return redirect('recipe_show', ingredient.recipe.id)

  param = {
    'ingredient': ingredient
  }

  return render(request, "cook/ingredient/edit.html", param)

@login_required
def destroy_ingredient(request, ingredient_id):
  try:
    ingredient = Ingredient.objects.get(pk=ingredient_id)
  except Ingredient.DoesNotExist:
    raise Http404("Ingredient does not exist.")

  if request.method == 'POST':
    if check_user(request, ingredient.recipe.user):
      ingredient.delete()
    else:
      return render(request, 'error/http401.html', {'errors': ['投稿者のみが材料の削除をできます。']}, status=401)

  return redirect('recipe_show', ingredient.recipe.id)



# my funcs
def check_user(request, published_user) -> bool:
  if request.user == published_user:
    return True
  else:
    return False