from django import forms
from cook.models import *

class IngredientForm(forms.ModelForm):
  class Meta:
    model = Ingredient
    fields = ('name', 'amout')
    labels = {
      'name': '材料名',
      'amout': '量',
    }