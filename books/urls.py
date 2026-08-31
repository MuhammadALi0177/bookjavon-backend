from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import telegram_bot

router = DefaultRouter()
router.register(r'books', views.BookViewSet, basename='book')
router.register(r'chat-rooms', views.ChatRoomViewSet, basename='chatroom')

urlpatterns = [
    path('', include(router.urls)),
    path('cities/', views.CityListView.as_view(), name='city-list'),
    path('districts/', views.DistrictListView.as_view(), name='district-list'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('my-books/', views.MyBooksView.as_view(), name='my-books'),
    path('favorites/', views.FavoritesView.as_view(), name='favorites'),
    path('init/', views.webapp_init, name='webapp-init'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('setup-admin/', views.setup_admin, name='setup-admin'),
    path('stats/', views.stats_view, name='stats'),
    path('ping/', views.ping_view, name='ping'),
    path('telegram/webhook/', telegram_bot.telegram_webhook, name='telegram-webhook'),
    path('telegram/set-webhook/', telegram_bot.set_webhook, name='set-webhook'),
]
