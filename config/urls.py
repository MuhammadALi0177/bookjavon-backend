from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.views.static import serve as static_serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
]

# Media fayllarni xizmat qilish
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # Production'da ham media fayllarni xizmat qilish
    def serve_media(request, path=''):  
        return static_serve(request, path, document_root=str(settings.MEDIA_ROOT))
    urlpatterns += [
        path('media/<path:path>', serve_media),
    ]
