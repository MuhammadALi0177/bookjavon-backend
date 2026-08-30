from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books.urls')),
]

# Media fayllarni xizmat qilish (DEBUG va production ham)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
