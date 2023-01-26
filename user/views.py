from django.shortcuts import render
from cook.models import Recipe

# Create your views here.
def my_page(request):
  user = request.user
  recipes = Recipe.objects.filter(user_id=user.id)
  params = {
    'user': user,
    'recipes': recipes,
  }
  
  return render(request, 'user/myPage.html', params)