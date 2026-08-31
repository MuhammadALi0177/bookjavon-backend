from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve as static_serve
import os


def media_serve(request, path=''):
    return static_serve(request, path, document_root=str(settings.MEDIA_ROOT))


def frontend_serve(request, path=''):
    """Frontend SPA — barcha non-API route'larni index.html ga yo'naltirish"""
    frontend_dir = os.path.join(settings.BASE_DIR, 'static', 'frontend')
    # Agar fayl mavjud bo'lsa — to'g'ridan-to'g'ri xizmat qilish
    file_path = os.path.join(frontend_dir, path)
    if path and os.path.isfile(file_path):
        return static_serve(request, path, document_root=frontend_dir)
    # Yo'q bo'lsa — index.html qaytarish (SPA routing)
    return static_serve(request, 'index.html', document_root=frontend_dir)


urlpatterns = [
    path('api/', include('books.urls')),
]

# Media fayllarni xizmat qilish
urlpatterns += [
    path('media/<path:path>', media_serve, {'document_root': str(settings.MEDIA_ROOT)}),
]

# Frontend — barcha qolgan route'larni SPA ga yo'naltirish
# Assets fayllar
urlpatterns += [
    re_path(r'^assets/(?P<path>.*)$', static_serve, {'document_root': os.path.join(settings.BASE_DIR, 'static', 'frontend', 'assets')}),
]

# SPA catch-all — oxirida turishi shart
urlpatterns += [
    re_path(r'^(?!api/|media/|assets/).*$', frontend_serve),
]
