from django import forms
from django.forms import widgets

from .models import Product


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = ('title', 'price', 'currency', 'published_date', 'url')
        widgets = {'title': forms.TextInput, 'currency': forms.TextInput}