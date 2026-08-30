from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
import uuid as _uuid


class User(AbstractUser):
    """Telegram user model"""
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='bookzone_users',
        related_query_name='bookzone_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='bookzone_users',
        related_query_name='bookzone_user',
    )
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True, verbose_name="Telegram ID")
    telegram_username = models.CharField(max_length=255, blank=True, verbose_name="Username")
    full_name = models.CharField(max_length=255, blank=True, verbose_name="To'liq ism")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Telefon")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Avatar")
    city = models.ForeignKey('City', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Shahar")
    district = models.ForeignKey('District', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tuman")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Foydalanuvchi"
        verbose_name_plural = "Foydalanuvchilar"

    def __str__(self):
        return self.full_name or self.telegram_username or str(self.telegram_id)


class SimpleToken(models.Model):
    """Foydalanuvchi token'i"""
    key = models.CharField(max_length=64, unique=True, default='')
    user = models.OneToOneField(
        'books.User',
        on_delete=models.CASCADE,
        related_name='simple_token'
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Token'
        verbose_name_plural = 'Tokens'

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = _uuid.uuid4().hex + _uuid.uuid4().hex[:32]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.key[:8] + '...'


class City(models.Model):
    """Viloyat / Shahar"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Shahar nomi")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Shahar"
        verbose_name_plural = "Shaharlar"
        ordering = ['name']

    def __str__(self):
        return self.name


class District(models.Model):
    """Tuman"""
    name = models.CharField(max_length=100, verbose_name="Tuman nomi")
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts', verbose_name="Shahar")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Tuman"
        verbose_name_plural = "Tumanlar"
        ordering = ['name']
        unique_together = ['name', 'city']

    def __str__(self):
        return f"{self.name}, {self.city.name}"


class Category(models.Model):
    """Kitob kategoriyasi"""
    name = models.CharField(max_length=100, unique=True, verbose_name="Kategoriya nomi")
    icon = models.CharField(max_length=50, blank=True, verbose_name="Icon nomi")
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['name']

    def __str__(self):
        return f"{self.icon} {self.name}" if self.icon else self.name


class Book(models.Model):
    """Kitob"""
    STATUS_CHOICES = [
        ('sale', 'Sotish'),
        ('rent', 'Ijara'),
        ('barter', 'Barter'),
    ]

    CONDITION_CHOICES = [
        ('new', 'Yangi'),
        ('like_new', 'Yangidek'),
        ('good', 'Yaxshi'),
        ('acceptable', 'Qoniqarli'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, verbose_name="Kitob nomi")
    author = models.CharField(max_length=255, verbose_name="Muallif")
    description = models.TextField(blank=True, verbose_name="Tavsif")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Kategoriya")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, verbose_name="Holat")
    condition = models.CharField(max_length=15, choices=CONDITION_CHOICES, default='good', verbose_name="Holat")
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Narx (so'm)")
    barter_wish = models.CharField(max_length=500, blank=True, verbose_name="Barter sharti")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books', verbose_name="Egasi")
    city = models.ForeignKey(City, on_delete=models.CASCADE, verbose_name="Shahar")
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Tuman")
    address = models.CharField(max_length=255, blank=True, verbose_name="Manzil")
    is_available = models.BooleanField(default=True, verbose_name="Mavjud")
    is_premium = models.BooleanField(default=False, verbose_name="Premium")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Ko'rishlar soni")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Kitob"
        verbose_name_plural = "Kitoblar"
        ordering = ['-is_premium', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.author}"


class BookImage(models.Model):
    """Kitob rasmlari"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='books/', verbose_name="Rasm")
    is_primary = models.BooleanField(default=False, verbose_name="Asosiy rasm")
    order = models.PositiveIntegerField(default=0, verbose_name="Tartib")

    class Meta:
        verbose_name = "Kitob rasmi"
        verbose_name_plural = "Kitob rasmlari"
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.book.title}"


class Favorite(models.Model):
    """Sevimli kitoblar"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Sevimli"
        verbose_name_plural = "Sevimlilar"
        unique_together = ['user', 'book']


class ChatRoom(models.Model):
    """Suhbat xonasi"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='chat_rooms')
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_rooms_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Suhbat xonasi"
        verbose_name_plural = "Suhbat xonalari"
        unique_together = ['book', 'user1', 'user2']

    def __str__(self):
        return f"Chat: {self.user1} <-> {self.user2} about {self.book.title}"


class Message(models.Model):
    """Xabar"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    text = models.TextField(verbose_name="Xabar matni")
    is_read = models.BooleanField(default=False, verbose_name="O'qilgan")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Xabar"
        verbose_name_plural = "Xabarlar"
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender}: {self.text[:50]}"
