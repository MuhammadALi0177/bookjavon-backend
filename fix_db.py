import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from books.models import *

# Remove duplicate categories (keep ones with text icons, remove emoji ones)
emoji_icons = ['book', 'toy', 'box', 'globe', 'search', 'rocket', 'pen', 'graduation', 'chart', 'mask', 'smile', 'translate', 'ruler', 'brain', 'chess', 'flower', 'trophy', 'castle', 'laptop', 'pill']

# Find duplicates - keep only the first of each name
seen_names = set()
dups = []
for c in Category.objects.all().order_by('id'):
    if c.name in seen_names:
        dups.append(c)
    else:
        seen_names.add(c.name)

for d in dups:
    print(f'Removing duplicate: {d.name} (icon={d.icon})')
    d.delete()

print(f'Removed {len(dups)} duplicates')
print(f'Remaining categories: {Category.objects.count()}')
