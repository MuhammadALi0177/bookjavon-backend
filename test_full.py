import os, sys, io, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django; django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from books.models import City, District, Category, Book, SimpleToken

User = get_user_model()
client = Client()

PASS = 0
FAIL = 0

def test(name, condition, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  [PASS] {name}")
    else:
        FAIL += 1
        print(f"  [FAIL] {name} - {detail}")

print("=" * 60)
print("  BOOKZONE FULL API TEST")
print("=" * 60)

# ---- 1. STATS ----
print("\n[1] STATS")
resp = client.get('/api/stats/')
data = resp.json()
test("Stats returns 200", resp.status_code == 200)
test("Stats has total_books", 'total_books' in data)
test("Stats has total_users", 'total_users' in data)
test("Stats has total_cities", 'total_cities' in data)
test("Cities count > 0", data.get('total_cities', 0) > 0, f"got {data.get('total_cities')}")

# ---- 2. CATEGORIES ----
print("\n[2] CATEGORIES")
resp = client.get('/api/categories/?page_size=100')
data = resp.json()
cats = data.get('results', data)
test("Categories returns 200", resp.status_code == 200)
test("Categories count = 20", len(cats) == 20, f"got {len(cats)}")
test("Categories have icon field", all('icon' in c for c in cats))

# ---- 3. CITIES ----
print("\n[3] CITIES")
resp = client.get('/api/cities/?page_size=100')
data = resp.json()
cities = data.get('results', data)
test("Cities returns 200", resp.status_code == 200)
test("Cities count = 13", len(cities) == 13, f"got {len(cities)}")
test("Toshkent exists", any(c['name'] == 'Toshkent' for c in cities))

# ---- 4. DISTRICTS ----
print("\n[4] DISTRICTS")
toshkent = City.objects.get(name='Toshkent')
resp = client.get(f'/api/districts/?city_id={toshkent.id}')
data = resp.json()
districts = data.get('results', data)
test("Districts returns 200", resp.status_code == 200)
test("Toshkent has districts", len(districts) > 0, f"got {len(districts)}")

# ---- 5. REGISTER ----
print("\n[5] REGISTER")
resp = client.post('/api/register/', json.dumps({
    'username': 'testuser_api',
    'password': 'testpass123',
    'full_name': 'Test API User',
    'email': 'testapi@test.com'
}), content_type='application/json')
data = resp.json()
test("Register returns 201", resp.status_code == 201, f"got {resp.status_code}: {data}")
test("Register returns user", 'user' in data)
test("Register returns token", 'token' in data)
token = data.get('token', '')

# ---- 6. REGISTER DUPLICATE ----
print("\n[6] REGISTER DUPLICATE")
resp = client.post('/api/register/', json.dumps({
    'username': 'testuser_api',
    'password': 'testpass123',
    'full_name': 'Duplicate'
}), content_type='application/json')
test("Duplicate register returns 400", resp.status_code == 400)

# ---- 7. LOGIN ----
print("\n[7] LOGIN")
resp = client.post('/api/login/', json.dumps({
    'username': 'testuser_api',
    'password': 'testpass123'
}), content_type='application/json')
data = resp.json()
test("Login returns 200", resp.status_code == 200)
test("Login returns token", 'token' in data)

# ---- 8. LOGIN WRONG PASSWORD ----
print("\n[8] LOGIN WRONG PASSWORD")
resp = client.post('/api/login/', json.dumps({
    'username': 'testuser_api',
    'password': 'wrongpassword'
}), content_type='application/json')
test("Wrong password returns 401", resp.status_code == 401)

# ---- 9. PROFILE (authenticated) ----
print("\n[9] PROFILE")
user = User.objects.get(username='testuser_api')
token_obj = SimpleToken.objects.get(user=user)
resp = client.get('/api/profile/', HTTP_AUTHORIZATION=f'demo {token_obj.key}')
data = resp.json()
test("Profile returns 200", resp.status_code == 200)
test("Profile has username", data.get('username') == 'testuser_api')

# ---- 10. PROFILE (unauthenticated) ----
print("\n[10] PROFILE (no auth)")
resp = client.get('/api/profile/')
test("Profile without auth returns 401", resp.status_code == 401)

# ---- 11. BOOKS LIST ----
print("\n[11] BOOKS LIST")
resp = client.get('/api/books/')
data = resp.json()
test("Books list returns 200", resp.status_code == 200)
test("Books has results", 'results' in data)

# ---- 12. CREATE BOOK ----
print("\n[12] CREATE BOOK")
cat = Category.objects.first()
resp = client.post('/api/books/', json.dumps({
    'title': 'Test Kitob',
    'author': 'Test Muallif',
    'status': 'sale',
    'price': 50000,
    'city': toshkent.id,
    'category': cat.id,
    'description': 'Test tavsif'
}), content_type='application/json', HTTP_AUTHORIZATION=f'demo {token_obj.key}')
data = resp.json()
test("Create book returns 201", resp.status_code == 201, f"got {resp.status_code}: {data}")
test("Created book has id", 'id' in data)
book_id = data.get('id', '')

# ---- 13. BOOK DETAIL ----
print("\n[13] BOOK DETAIL")
if book_id:
    resp = client.get(f'/api/books/{book_id}/')
    data = resp.json()
    test("Book detail returns 200", resp.status_code == 200)
    test("Book detail has title", data.get('title') == 'Test Kitob')
else:
    test("Book detail skipped", False, "no book_id")

# ---- 14. BOOKS FILTER BY CITY ----
print("\n[14] BOOKS FILTER")
resp = client.get(f'/api/books/?city_id={toshkent.id}')
data = resp.json()
results = data.get('results', [])
test("Filter by city works", len(results) >= 1)

# ---- 15. BOOKS FILTER BY SEARCH ----
print("\n[15] BOOKS SEARCH")
resp = client.get('/api/books/?search=Test')
data = resp.json()
results = data.get('results', [])
test("Search works", len(results) >= 1)

# ---- CLEANUP ----
print("\n[CLEANUP]")
Book.objects.filter(title='Test Kitob').delete()
user = User.objects.filter(username='testuser_api').first()
if user:
    user.delete()
print("  Test data cleaned up.")

# ---- SUMMARY ----
print("\n" + "=" * 60)
print(f"  RESULTS: {PASS} passed, {FAIL} failed out of {PASS+FAIL} tests")
print("=" * 60)
