from rest_framework import serializers
from .models import (
    User, City, District, Category, Book, BookImage,
    Favorite, ChatRoom, Message
)


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = ['id', 'name']


class DistrictSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)

    class Meta:
        model = District
        fields = ['id', 'name', 'city', 'city_name']


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon']


class UserSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True, default='')
    district_name = serializers.CharField(source='district.name', read_only=True, default='')
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id', 'telegram_id', 'telegram_username', 'full_name',
            'phone', 'avatar', 'city', 'city_name', 'district',
            'district_name', 'books_count', 'created_at'
        ]
        read_only_fields = ['telegram_id', 'created_at']

    def get_books_count(self, obj):
        return obj.books.filter(is_available=True).count()


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = ['id', 'image', 'is_primary', 'order']
        read_only_fields = ['id']


class BookListSerializer(serializers.ModelSerializer):
    """Kitob ro'yxati uchun qisqartirilgan serializer"""
    owner_name = serializers.CharField(source='owner.full_name', read_only=True, default='')
    owner_avatar = serializers.ImageField(source='owner.avatar', read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True, default='')
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    category_icon = serializers.CharField(source='category.icon', read_only=True, default='')
    primary_image = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'category', 'category_name',
            'category_icon', 'status', 'status_display', 'condition', 'condition_display',
            'price', 'barter_wish', 'owner', 'owner_name', 'owner_avatar',
            'city', 'city_name', 'district', 'district_name', 'address',
            'is_available', 'is_premium', 'view_count', 'primary_image',
            'is_favorited', 'created_at'
        ]

    def get_primary_image(self, obj):
        img = obj.images.filter(is_primary=True).first() or obj.images.first()
        if img and img.image:
            if img.image.startswith('data:'):
                return img.image
            return f'data:image/jpeg;base64,{img.image}'
        return None

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, book=obj).exists()
        return False


class BookDetailSerializer(serializers.ModelSerializer):
    """Kitob tafsilotlari uchun to'liq serializer"""
    owner = UserSerializer(read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    district_name = serializers.CharField(source='district.name', read_only=True, default='')
    category_name = serializers.CharField(source='category.name', read_only=True, default='')
    category_icon = serializers.CharField(source='category.icon', read_only=True, default='')
    images = BookImageSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    condition_display = serializers.CharField(source='get_condition_display', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()

    def get_images(self, obj):
        images = obj.images.all()
        result = []
        for img in images:
            data = BookImageSerializer(img).data
            if data.get('image') and not data['image'].startswith('data:'):
                data['image'] = f'data:image/jpeg;base64,{data["image"]}'
            result.append(data)
        return result

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'category', 'category_name',
            'category_icon', 'status', 'status_display', 'condition', 'condition_display',
            'price', 'barter_wish', 'owner', 'city', 'city_name', 'district',
            'district_name', 'address', 'is_available', 'is_premium',
            'view_count', 'images', 'is_favorited', 'favorites_count',
            'created_at', 'updated_at'
        ]

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, book=obj).exists()
        return False

    def get_favorites_count(self, obj):
        return obj.favorited_by.count()


class BookCreateUpdateSerializer(serializers.ModelSerializer):
    """Kitob yaratish / tahrirlash"""
    images = BookImageSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'description', 'category', 'status',
            'condition', 'price', 'barter_wish', 'city', 'district',
            'address', 'images'
        ]

    def to_internal_value(self, data):
        # Empty string larni None ga aylantirish (ForeignKey uchun)
        for field in ['category', 'district']:
            if field in data and data[field] in ['', None, 'null']:
                data[field] = None
        # price bo'sh bo'lsa None qilish
        if 'price' in data and data['price'] in ['', None, 'null']:
            data['price'] = None
        return super().to_internal_value(data)


class FavoriteSerializer(serializers.ModelSerializer):
    book = BookListSerializer(read_only=True)
    book_id = serializers.PrimaryKeyRelatedField(
        queryset=Book.objects.all(), source='book', write_only=True
    )

    class Meta:
        model = Favorite
        fields = ['id', 'book', 'book_id', 'created_at']


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.full_name', read_only=True, default='')
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'sender_name', 'sender_avatar', 'text', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read', 'created_at']


class ChatRoomSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    other_user = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = [
            'id', 'book', 'book_title', 'user1', 'user2',
            'other_user', 'last_message', 'unread_count', 'created_at'
        ]

    def get_other_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other = obj.user2 if obj.user1 == request.user else obj.user1
            return {
                'id': other.id,
                'full_name': other.full_name,
                'telegram_username': other.telegram_username,
                'avatar': other.avatar.url if other.avatar else None
            }
        return None

    def get_last_message(self, obj):
        msg = obj.messages.order_by('-created_at').first()
        if msg:
            return MessageSerializer(msg).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(sender=request.user).count()
        return 0
