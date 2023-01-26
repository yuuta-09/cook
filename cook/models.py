from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
    

class Recipe(models.Model):
  name = models.CharField(max_length=50)
  description = models.TextField()
  posted_at = models.DateTimeField(default=timezone.now)
  user = models.ForeignKey(get_user_model(), related_name='recipe', on_delete=models.CASCADE)

  def __str__(self) -> str:
    return self.name
  

class Ingredient(models.Model):
  name = models.CharField(max_length=200)
  amout = models.CharField(max_length=100) # 量は単位まで入力するためCharField
  recipe = models.ForeignKey(Recipe, related_name='ingredients', on_delete=models.CASCADE)
  
  
  def __str__(self) -> str:
    return self.name