from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from cook.models import Recipe, Ingredient
from django.forms import inlineformset_factory
from cook.forms import IngredientForm
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin


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
NUM_OF_FORMS = 3
class IngredientNew(LoginRequiredMixin, FormView):
  template_name = 'cook/ingredient/new.html'
  
  def get_form_class(self):
    return inlineformset_factory(Recipe, Ingredient, form=IngredientForm, extra=NUM_OF_FORMS, max_num=10)

  def get_success_url(self):
    return reverse('ingredient_new', kwargs={'recipe_id': self.kwargs['recipe_id']})
    
  def get_recipe(self):
    recipe = Recipe.objects.get(pk=self.kwargs['recipe_id'])
    return recipe

  def form_valid(self, form):
    recipe = self.get_recipe()
    if recipe.user == self.request.user:
      form.instance = recipe
      form.save()
      return redirect('recipe_show', self.kwargs['recipe_id'])
    else:
      return render(self.request, 'error/http401.html', {'errors': ['投稿者のみが材料を追加できます。']}, status=401)

  @method_decorator(login_required)
  def dispatch(self, request, *args, **kwargs):
    return super().dispatch(request, *args, **kwargs)

  # POSTリクエストの時の処理
  def post(self, request, *args, **kwargs):
    global NUM_OF_FORMS
    recipe = self.get_recipe()
    
    # フォームを追加するボタンが押されたとき
    if 'button_add' in request.POST:
      NUM_OF_FORMS += 1 # formの数を増やす
      request.session['form_data'] = request.POST # 現在のフォームデータを保存
      request.session.modified = True
      print(NUM_OF_FORMS)
      return redirect('ingredient_new', recipe.id)
    
    # フォームの数をリセットするボタンが押されたとき
    elif 'button_reset' in request.POST:
      NUM_OF_FORMS = 3 # formの数をリセット
      return redirect('ingredient_new', recipe.id)
    
    # 決定ボタンが押されたとき
    else:
      form_class = self.get_form_class()
      formset = form_class(
        data=self.request.POST, 
        instance=recipe, 
        queryset=Ingredient.objects.none()
      )
      NUM_OF_FORMS = 3 # フォームの数をリセット
      # formが有効かの判定
      if formset.is_valid():
        if check_user(request, recipe.user):
          formset.save()
        else:
          return render(request, 'error/http401.html', {'errors': ['投稿者のみが材料を追加できます。']}, status=401)
      else:
        return HttpResponse("Error.")
      return redirect('recipe_show', self.kwargs['recipe_id'])
    
  
  def get(self, request, *args, **kwargs):
    recipe = self.get_recipe()
    form_data = request.session.get('form_data', None)
    form_class = self.get_form_class()
    if form_data:
      form_data['ingredients-TOTAL_FORMS'] = NUM_OF_FORMS
      # フォームを追加するボタンが押されたときに保存された値を元にフォームを作成
      formset = form_class(
          data=form_data,
          instance=recipe,
          queryset=Ingredient.objects.none()
      )
      del request.session['form_data']
    else:
      # 初期状態では3つのフォームを作成
      formset = form_class(
          instance=recipe,
          queryset=Ingredient.objects.none()
      )

    return render(request, self.template_name, {'form': formset})


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