# -*- coding: utf-8 -*-
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from books.models import Category

# Delete old
Category.objects.filter(name='Diniy kitoblar').delete()

# Update all category icons
updates = {
    'Badiiy adabiyot': '\U0001f4d6',
    'Ilmiy kitoblar': '\U0001f393',
    "O'quv qo'llanmalari": '\U0001f4d0',
    'Bolalar kitoblari': '\U0001f9f8',
    'Linguistika': '\U0001f5e3',
    'Tarixiy kitoblar': '\U0001f3db',
    'Texnologiya': '\U0001f4bb',
    'Tibbiyot': '\U0001f48a',
    'Iqtisodiyot': '\U0001f4c8',
    'Psixologiya': '\U0001f9e0',
    'Chet tili kitoblari': '\U0001f30d',
    'Klassika': '\U0001f3ad',
    'Detektiv': '\U0001f50e',
    'Fantastika': '\U0001f6f8',
    'Shaxmat': '\u265f\ufe0f',
    'Sport': '\U0001f3c5',
    'Kulgu': '\U0001f602',
    'Hikoyalar': '\u270d\ufe0f',
    "Sherlar": '\U0001f338',
    'Boshqa': '\U0001f4e6',
}

for name, icon in updates.items():
    cat, created = Category.objects.get_or_create(name=name, defaults={'icon': icon})
    if not created and cat.icon != icon:
        cat.icon = icon
        cat.save()

print('Total categories: ' + str(Category.objects.count()))
print('Done!')
