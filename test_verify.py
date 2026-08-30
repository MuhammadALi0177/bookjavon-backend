# -*- coding: utf-8 -*-
import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from books.models import User, City, Book, Category
from books.serializers import BookCreateUpdateSerializer

user, _ = User.objects.get_or_create(
    telegram_id=9999999,
    defaults={'username': 'test_verify', 'full_name': 'Test Verify', 'telegram_username': 'test_verify'}
)
city = City.objects.first()

# === CASE 1: Minimal payload ===
print("CASE 1: Minimal payload (no optional fields)...")
s = BookCreateUpdateSerializer(data={
    'title': 'Test Kitob 1',
    'author': 'Test Muallif',
    'status': 'sale',
    'city': city.id
})
if s.is_valid():
    book = s.save(owner=user)
    print("  PASS: Book created:", book.id)
else:
    print("  FAIL:", s.errors)
    sys.exit(1)

# === CASE 2: Empty strings (THE BUG) ===
print("CASE 2: Empty strings for optional FK fields...")
s = BookCreateUpdateSerializer(data={
    'title': 'Test Kitob 2',
    'author': 'Test Muallif 2',
    'status': 'barter',
    'condition': 'good',
    'city': city.id,
    'category': '',
    'district': '',
    'price': '',
    'barter_wish': '',
    'description': '',
    'address': ''
})
if s.is_valid():
    book = s.save(owner=user)
    print("  PASS: Book created despite empty strings:", book.id)
else:
    print("  FAIL:", s.errors)
    sys.exit(1)

# === CASE 3: With valid FK ===
print("CASE 3: With valid category...")
cat = Category.objects.first()
s = BookCreateUpdateSerializer(data={
    'title': 'Test Kitob 3',
    'author': 'Test Muallif 3',
    'status': 'rent',
    'condition': 'like_new',
    'city': city.id,
    'category': cat.id,
    'price': 50000,
})
if s.is_valid():
    book = s.save(owner=user)
    print("  PASS: Book created:", book.id)
else:
    print("  FAIL:", s.errors)
    sys.exit(1)

# === CASE 4: Missing title (should fail) ===
print("CASE 4: Missing title (should fail)...")
s = BookCreateUpdateSerializer(data={
    'author': 'Muallif',
    'status': 'sale',
    'city': city.id
})
if not s.is_valid():
    print("  PASS: Correctly rejected:", s.errors)
else:
    print("  FAIL: Should have been rejected!")
    sys.exit(1)

# Verify
total = Book.objects.filter(owner=user).count()
print(f"\nAll 4 tests passed! User has {total} books.")
