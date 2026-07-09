from django import forms
from django.forms import inlineformset_factory
from .models import Cargo

class CargoForm(forms.ModelForm):
    class Meta:
        model = Cargo
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del cargo'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del cargo'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
     
