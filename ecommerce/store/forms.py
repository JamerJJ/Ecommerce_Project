from django.forms import ModelForm
from .models import Order, Product
from django . contrib.auth.forms import UserCreationForm
from django import forms
from django.contrib.auth.models import User


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class CategoryForm(forms.Form):
    category = forms.ChoiceField(choices=Product.objects.values_list('category', 'category').distinct(), required=False)
