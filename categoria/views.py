from django.shortcuts import render

# Create your views here.
import json
from decimal import Decimal

from django.utils import timezone
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth import login


from .models import Categoria
from .forms import CategoriaForm


from shared.mixins import (
    StaffRequiredMixin, ExportListMixin, DynamicColumnsMixin,
    ListFeaturesMixin, GenericDetailMixin,
)
from shared.decorators import audit_action
from shared.exports import export_excel, export_pdf
from shared.columns import columns_context, get_visible_columns, visible_export
from shared.money import compute_totals, money


class CategoriaListView(LoginRequiredMixin, ExportListMixin, ListView):
    model = Categoria
    template_name = 'categoria/categoria_list.html'
    context_object_name = 'categorias'
    paginate_by = 3

    export_filename = 'Categorias'
    export_title = 'Listado de Categoria'
    export_fields = [
        ('Nombre', 'nombre'),
        ('Descripción', 'descripcion'),
        ('Activo', lambda o: 'Sí' if o.activo else 'No'),
    ]


class CategoriaDetailView(LoginRequiredMixin, DetailView):
    model = Categoria
    template_name = 'categoria/categoria_detail.html'
    context_object_name = 'categoria'


class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'
    success_url = reverse_lazy('categoria:categoria_list')
    
class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'categoria/categoria_form.html'
    success_url = reverse_lazy('categoria:categoria_list')
    

class CategoriaDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Categoria 
    template_name = 'categoria/categoria_confirm_delete.html'
    success_url = reverse_lazy('categoria:categoria_list')
