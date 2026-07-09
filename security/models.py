from django.db import models
from decimal import Decimal

# Create your models here.

class Cargo(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Nombre del Cargo')
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

