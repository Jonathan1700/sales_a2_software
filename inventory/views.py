from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Categoria
from .forms import CategoriaForm
from shared.mixins import (
    StaffRequiredMixin, ExportListMixin, DynamicColumnsMixin,
    ListFeaturesMixin, GenericDetailMixin,
)
from django.contrib.auth.decorators import login_required

# Create your views here.
class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = 'inventory/categoria_list.html'
    paginate_by = 3
    context_object_name = 'categoria'
    

class CategoriaDetailView(LoginRequiredMixin, DetailView):
    model = Categoria
    template_name = 'inventory/categoria_detail.html'
    context_object_name = 'categoria'
    
class CategoriaCreateView(LoginRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventory/categoria_form.html'
    success_url = reverse_lazy('inventory:categoria_list')
    extra_context = {'page_title': 'Nueva categoria', 'empleado_url': reverse_lazy('inventory:categoria_list')}

    
class CategoriaUpdateView(LoginRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = 'inventory/categoria_form.html'
    success_url = reverse_lazy('inventory:categoria_list')
    extra_context = {'page_title': 'Editar Categoria', 'categoria_url': reverse_lazy('inventory:categoria_list')}
    
class CategoriaDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Categoria
    template_name = 'inventory/categoria_confirm_delete.html'
    success_url = reverse_lazy('inventory:categoria_list')


    