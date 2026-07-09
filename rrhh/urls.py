from django.urls import path
from . import views

app_name = 'rrhh'

urlpatterns = [
    path('cargos/', views.CargoListView.as_view(), name='cargo_list'),
    path('cargos/create/', views.CargoCreateView.as_view(), name='cargo_create'),
    path('cargos/<int:pk>/edit/', views.CargoUpdateView.as_view(), name='cargo_update'),
    path('cargos/<int:pk>/delete/', views.CargoDeleteView.as_view(), name='cargo_delete'),

]