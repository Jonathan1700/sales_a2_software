from django import forms
from django.forms import inlineformset_factory

from .models import Purchase, PurchaseDetail


class PurchaseForm(forms.ModelForm):
    """Formulario para la cabecera de compra."""
    class Meta:
        model = Purchase
        fields = ['supplier', 'document_number']
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-select'}),
            'document_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
# Formset: múltiples líneas de detalle dentro de UNA compra
PurchaseDetailFormSet = inlineformset_factory(   # <-- 2b (debajo, fuera de la clase)
    Purchase,
    PurchaseDetail,
    fields=['product', 'quantity', 'unit_cost'],
    extra=3,
    can_delete=True,
    widgets={
        'product': forms.Select(attrs={'class': 'form-select'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        'unit_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
    },
)