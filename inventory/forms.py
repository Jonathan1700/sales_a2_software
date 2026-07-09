from django import forms
from django.forms import inlineformset_factory
from .models import Categoria


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombres'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la categoria'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    