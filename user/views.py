from django.shortcuts import render, HttpResponse
from cook.models import Recipe
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required
def my_page(request):
  user = request.user
  recipes = Recipe.objects.filter(user_id = user.id)
  params = {
    'user': user,
    'recipes': recipes,
  }
  
  return render(request, 'user/myPage.html', params)