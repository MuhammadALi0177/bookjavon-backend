from django.core.management.base import BaseCommand
from books.models import City, District, Category


class Command(BaseCommand):
    help = 'O\'zbekiston shaharlari, tumanlari va kategoriyalarni yuklash'

    def handle(self, *args, **options):
        self.stdout.write("Ma'lumotlar yuklanmoqda...")

        # Shaharlar
        cities_data = {
            'Toshkent': [
                'Chilonzor', 'Yakkasaroy', 'Shayxontohur', 'Olmazor',
                'Uchtepa', 'Yashnabod', 'Mirobod', 'O\'zbekiston',
                'Mirzo Ulug\'bek', 'Bektemir', 'Yangihayot', 'Sirg\'ali'
            ],
            'Samarqand': [
                'Samarqand shahar', 'Urgut', 'Jomboy', 'Kattaqo\'rg\'on',
                'Nurobod', 'Paxtachi', 'Payariq', 'Bulung\'ur'
            ],
            'Buxoro': [
                'Buxoro shahar', 'Vobkent', 'Kogon', 'Jondor',
                'Peshku', 'Romitan', 'Shofirkon', 'Qorako\'l'
            ],
            'Farg\'ona': [
                'Farg\'ona shahar', 'Qo\'qon', 'Marg\'ilon', 'Quvasoy',
                'Rishton', 'Bog\'dod', 'Dang\'ara', 'Oltiariq'
            ],
            'Namangan': [
                'Namangan shahar', 'Chust', 'Kosonsoy', 'Pop',
                'To\'raqo\'rg\'on', 'Uchqo\'rg\'on', 'Mingbuloq', 'Yangiqo\'rg\'on'
            ],
            'Andijon': [
                'Andijon shahar', 'Xonobod', 'Asaka', 'Xo\'jaobod',
                'Baliqchi', 'Jalaquduq', 'Qo\'rg\'ontepa', 'Shahrixon'
            ],
            'Xorazm': [
                'Urganch shahar', 'Xiva', 'Xonqa', 'Gurlan',
                'Shovot', 'YANGIARIQ', 'Yangibozor', 'Hazorasp'
            ],
            'Qashqadaryo': [
                'Qarshi shahar', 'Shahrisabz', 'Kitob', 'Muborak',
                'Koson', 'Nishon', 'Chiroqchi', 'Dehqonobod'
            ],
            'Surxondaryo': [
                'Termiz shahar', 'Denau', 'Boysun', 'Muzrabot',
                'Sariosiyo', 'Qumqo\'rg\'on', 'Sherobod', 'Angor'
            ],
            'Jizzax': [
                'Jizzax shahar', 'Dustlik', 'Forish', 'G\'allaorol',
                'Mirzacho\'l', 'Paxtakor', 'Zarbdor', 'Zafarobod'
            ],
            'Navoiy': [
                'Navoiy shahar', 'Zarafshan', 'Uchquduq', 'Qiziltepa',
                'Nurota', 'Konimex', 'Xatirchi', 'Tomdi'
            ],
            'Sirdaryo': [
                'Guliston shahar', 'Yangiyer', 'Syrdarya', 'Mirzaobod',
                'Oqoltin', 'Boyovut', 'Guliston', 'Sardoba'
            ],
            'Qoraqalpog\'iston': [
                'Nukus shahar', 'Xojayli', 'Chimboy', 'Mo\'ynoq',
                'Qanliko\'l', 'Beruniy', 'Ellikqal\'a', 'Taxtako\'pir'
            ],
        }

        for city_name, districts in cities_data.items():
            city, created = City.objects.get_or_create(name=city_name)
            if created:
                self.stdout.write(f"  [OK] Shahar: {city_name}")
            for district_name in districts:
                _, created = District.objects.get_or_create(
                    name=district_name, city=city
                )
                if created:
                    self.stdout.write(f"    [+] Tuman: {district_name}")

        # Kategoriyalar
        categories_data = [
            ('Badiiy adabiyot', 'book'),
            ('Ilmiy kitoblar', 'graduation'),
            ('O\'quv qo\'llanmalari', 'ruler'),
            ('Bolalar kitoblari', 'toy'),
            ('Linguistika', 'translate'),
            ('Tarixiy kitoblar', 'castle'),
            ('Texnologiya', 'laptop'),
            ('Tibbiyot', 'pill'),
            ('Iqtisodiyot', 'chart'),
            ('Psixologiya', 'brain'),
            ('Chet tili kitoblari', 'globe'),
            ('Klassika', 'mask'),
            ('Detektiv', 'search'),
            ('Fantastika', 'rocket'),
            ('Shaxmat', 'chess'),
            ('Sport', 'trophy'),
            ('Kulgu', 'smile'),
            ('Hikoyalar', 'pen'),
            ('She\'rlar', 'flower'),
            ('Boshqa', 'box'),
        ]

        for name, icon in categories_data:
            _, created = Category.objects.get_or_create(
                name=name, defaults={'icon': icon}
            )
            if created:
                self.stdout.write(f"  [C] Kategoriya: {name}")

        self.stdout.write(self.style.SUCCESS(
            f"\n[OK] Ma'lumotlar muvaffaqiyatli yuklandi!\n"
            f"   Shaharlar: {City.objects.count()}\n"
            f"   Tumanlar: {District.objects.count()}\n"
            f"   Kategoriyalar: {Category.objects.count()}"
        ))
