from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User, City, District, Category, Book, BookImage,
    Favorite, ChatRoom, Message
)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'full_name', 'email', 'phone', 'city', 'is_staff', 'created_at']
    search_fields = ['full_name', 'username', 'email']
    list_filter = ['city', 'is_staff', 'is_active']

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Qo\'shimcha', {
            'fields': ('telegram_id', 'telegram_username', 'full_name', 'phone', 'avatar', 'city', 'district'),
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Qo\'shimcha', {
            'fields': ('full_name', 'email'),
        }),
    )


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active']
    list_filter = ['is_active']


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'is_active']
    list_filter = ['city', 'is_active']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon', 'is_active']


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'status', 'city', 'owner', 'is_premium', 'is_available', 'created_at']
    list_filter = ['status', 'condition', 'city', 'is_premium', 'is_available']
    search_fields = ['title', 'author']
    inlines = [BookImageInline]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'created_at']


@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ['book', 'user1', 'user2', 'created_at']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'room', 'text', 'is_read', 'created_at']
    list_filter = ['is_read']
