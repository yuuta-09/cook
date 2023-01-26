from django import forms
from cook.models import *

class IngredientForm(forms.ModelForm):
  class Meta:
    model = Ingredient
    fields = ('name', 'amout')
    labels = {
      'name': 'Name',
      'amout': 'Amount',
    }