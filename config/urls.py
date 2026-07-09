from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('purchases/', include('purchasing.urls')),
    path('security/', include('security.urls')),
    path('rrhh/', include('rrhh.urls')),
    path('categoria/', include('categoria.urls')),

    path('', include('billing.urls')),
]



# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
