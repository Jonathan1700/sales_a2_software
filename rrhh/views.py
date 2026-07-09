from django.shortcuts import render
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cargo
from .forms import CargoForm
from shared.mixins import (
    StaffRequiredMixin, ExportListMixin, DynamicColumnsMixin,
    ListFeaturesMixin, GenericDetailMixin,
)
from django.contrib.auth.decorators import login_required

# Create your views here.
class CargoListView(LoginRequiredMixin, ListView):
    model = Cargo
    template_name = 'rrhh/cargo_list.html'
    paginate_by = 3
    context_object_name = 'Cargo'
    

class CargoCreateView(LoginRequiredMixin, CreateView):
    model = Cargo
    form_class = CargoForm
    template_name = 'rrhh/cargo_form.html'
    success_url = reverse_lazy('rrhh:cargo_list')
    extra_context = {'page_title': 'Nuevo cargo', 'cargo_url': reverse_lazy('rrhh:cargo_list')}

class CargoUpdateView(LoginRequiredMixin, UpdateView):
    model = Cargo
    form_class = CargoForm
    template_name = 'rrhh/cargo_form.html'
    success_url = reverse_lazy('rrhh:cargo_list')
    extra_context = {'page_title': 'Editar Cargo', 'cargo_url': reverse_lazy('rrhh:cargo_list')}
    
    
class CargoDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Cargo
    template_name = 'rrhh/cargo_confirm_delete.html'
    success_url = reverse_lazy('rrhh:cargo_list')
