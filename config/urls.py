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

# Media fayllarni xizmat qilish — DEBUG va production ham
media_root = str(settings.MEDIA_ROOT)
if os.path.exists(media_root):
    urlpatterns += [
        path('media/<path:path>', lambda request, path: static_serve(request, path, document_root=media_root)),
    ]
