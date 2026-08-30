from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve


def media_serve(request, path=''):
    return static_serve(request, path, document_root=str(settings.MEDIA_ROOT))


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
]

# Media fayllarni xizmat qilish
urlpatterns += [
    path('media/<path:path>', media_serve, {'document_root': str(settings.MEDIA_ROOT)}),
]
