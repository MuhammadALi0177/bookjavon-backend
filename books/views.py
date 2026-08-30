from rest_framework import viewsets, generics, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count
from django.shortcuts import get_object_or_404

from .models import (
    User, City, District, Category, Book, BookImage,
    Favorite, ChatRoom, Message
)
from .serializers import (
    CitySerializer, DistrictSerializer, CategorySerializer,
    UserSerializer, BookListSerializer, BookDetailSerializer,
    BookCreateUpdateSerializer, BookImageSerializer,
    FavoriteSerializer, ChatRoomSerializer, MessageSerializer
)


class CityListView(generics.ListAPIView):
    """Shaharlar ro'yxati"""
    queryset = City.objects.filter(is_active=True)
    serializer_class = CitySerializer
    permission_classes = [permissions.AllowAny]


class DistrictListView(generics.ListAPIView):
    """Tumanlar ro'yxati (shahar bo'yicha)"""
    serializer_class = DistrictSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = District.objects.filter(is_active=True)
        city_id = self.request.query_params.get('city_id')
        if city_id:
            queryset = queryset.filter(city_id=city_id)
        return queryset


class CategoryListView(generics.ListAPIView):
    """Kategoriyalar ro'yxati"""
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class BookViewSet(viewsets.ModelViewSet):
    """Kitoblar CRUD"""
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return BookListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BookCreateUpdateSerializer
        return BookDetailSerializer

    def get_queryset(self):
        queryset = Book.objects.filter(is_available=True).select_related(
            'owner', 'city', 'district', 'category'
        ).prefetch_related('images')

        # Filters
        city_id = self.request.query_params.get('city_id')
        district_id = self.request.query_params.get('district_id')
        category_id = self.request.query_params.get('category_id')
        book_status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')

        if city_id:
            queryset = queryset.filter(city_id=city_id)
        if district_id:
            queryset = queryset.filter(district_id=district_id)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        if book_status:
            queryset = queryset.filter(status=book_status)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(author__icontains=search)
            )
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)

        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.view_count += 1
        instance.save(update_fields=['view_count'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'])
    def upload_image(self, request, pk=None):
        """Kitobga rasm yuklash (base64)"""
        try:
            book = self.get_object()
            if book.owner != request.user:
                return Response(
                    {'error': 'Faqat o\'z kitobingizga rasm yuklashingiz mumkin'},
                    status=status.HTTP_403_FORBIDDEN
                )

            image_data = request.data.get('image', '')
            if not image_data:
                return Response({'error': 'Rasm yuklanmadi'}, status=status.HTTP_400_BAD_REQUEST)

            # base64 tozalash
            if ',' in image_data:
                image_data = image_data.split(',', 1)[1]

            is_primary = book.images.count() == 0
            book_image = BookImage.objects.create(
                book=book, image=image_data, is_primary=is_primary
            )
            return Response(
                BookImageSerializer(book_image, context={'request': request}).data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': f'Rasm yuklashda xatolik: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        """Sevimlilarga qo'shish / olib tashlash"""
        book = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user, book=book
        )
        if not created:
            favorite.delete()
            return Response({'is_favorited': False})
        return Response({'is_favorited': True})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def start_chat(self, request, pk=None):
        """Kitob egasi bilan suhbat boshlash"""
        book = self.get_object()
        if book.owner == request.user:
            return Response(
                {'error': 'O\'zingiz bilan suhbat boshlay olmaysiz'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Existing chat check
        chat_room = ChatRoom.objects.filter(
            book=book
        ).filter(
            Q(user1=request.user, user2=book.owner) |
            Q(user1=book.owner, user2=request.user)
        ).first()

        if not chat_room:
            chat_room = ChatRoom.objects.create(
                book=book, user1=request.user, user2=book.owner
            )

        return Response(ChatRoomSerializer(chat_room, context={'request': request}).data)


class MyBooksView(generics.ListAPIView):
    """Mening kitoblarim"""
    serializer_class = BookListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(
            owner=self.request.user
        ).select_related('city', 'district', 'category').prefetch_related('images')


class UserProfileView(generics.RetrieveUpdateAPIView):
    """Foydalanuvchi profili"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class FavoritesView(generics.ListAPIView):
    """Sevimli kitoblar"""
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(
            user=self.request.user
        ).select_related('book', 'book__owner', 'book__city')


class ChatRoomViewSet(viewsets.ModelViewSet):
    """Suhbat xonalari"""
    serializer_class = ChatRoomSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ChatRoom.objects.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user)
        ).select_related('book', 'user1', 'user2')

    @action(detail=True, methods=['get', 'post'])
    def messages(self, request, pk=None):
        """Xabarlarni ko'rish / yuborish"""
        room = self.get_object()

        # Verify user is participant
        if request.user not in [room.user1, room.user2]:
            return Response(
                {'error': 'Siz bu suhbatning ishtirokchisi emassiz'},
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'GET':
            messages = room.messages.select_related('sender').order_by('created_at')
            page = self.paginate_queryset(messages)
            if page is not None:
                serializer = MessageSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = MessageSerializer(messages, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            text = request.data.get('text', '').strip()
            if not text:
                return Response(
                    {'error': 'Xabar bo\'sh bo\'lmasligi kerak'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            message = Message.objects.create(
                room=room, sender=request.user, text=text
            )
            return Response(
                MessageSerializer(message).data,
                status=status.HTTP_201_CREATED
            )

    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Xabarlarni o'qilgan deb belgilash"""
        room = self.get_object()
        room.messages.filter(is_read=False).exclude(
            sender=request.user
        ).update(is_read=True)
        return Response({'status': 'ok'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def webapp_init(request):
    """
    Telegram WebApp initData ni qabul qilish va foydalanuvchi yaratish.
    """
    from .authentication import TelegramWebAppAuth
    auth = TelegramWebAppAuth()
    result = auth.authenticate(request)
    if result:
        user, token = result
        return Response({
            'user': UserSerializer(user).data,
            'token': token
        })
    return Response(
        {'error': 'Autentifikatsiya xatosi'},
        status=status.HTTP_401_UNAUTHORIZED
    )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    Ro'yxatdan o'tish — email/username + parol bilan.
    """
    from books.models import SimpleToken

    username = request.data.get('username', '').strip()
    email = request.data.get('email', '').strip()
    password = request.data.get('password', '')
    full_name = request.data.get('full_name', '').strip()

    if not username or not password:
        return Response(
            {'error': 'Username va parol kiritish shart'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if len(password) < 6:
        return Response(
            {'error': 'Parol kamida 6 ta belgi bo\'lishi kerak'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Bu username allaqachon band'},
            status=status.HTTP_400_BAD_REQUEST
        )

    if email and User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Bu email allaqachon ro\'yxatdan o\'tgan'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = User.objects.create_user(
        username=username,
        password=password,
        email=email,
        full_name=full_name or username,
    )

    token = SimpleToken.objects.create(user=user)

    return Response({
        'user': UserSerializer(user).data,
        'token': token.key
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    Kirish — username + parol bilan.
    """
    from books.models import SimpleToken

    username = request.data.get('username', '').strip()
    password = request.data.get('password', '')

    if not username or not password:
        return Response(
            {'error': 'Username va parol kiritish shart'},
            status=status.HTTP_400_BAD_REQUEST
        )

    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'error': 'Username yoki parol noto\'g\'ri'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # Token olish yoki yaratish
    token, _ = SimpleToken.objects.get_or_create(user=user)

    return Response({
        'user': UserSerializer(user).data,
        'token': token.key
    })


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def ping_view(request):
    return Response({'status': 'ok', 'message': 'BookJavon is alive!'})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def stats_view(request):
    """Platforma statistikasi"""
    return Response({
        'total_books': Book.objects.filter(is_available=True).count(),
        'total_users': User.objects.count(),
        'total_cities': City.objects.filter(is_active=True).count(),
        'books_by_status': {
            'sale': Book.objects.filter(status='sale', is_available=True).count(),
            'rent': Book.objects.filter(status='rent', is_available=True).count(),
            'barter': Book.objects.filter(status='barter', is_available=True).count(),
        }
    })
