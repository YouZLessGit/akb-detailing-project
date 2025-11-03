# core/urls.py

# from django.contrib import admin # Больше не нужно
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # path('admin/', admin.site.urls), # Эту строку комментируем или удаляем
    path('api/', include('api.urls')),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
