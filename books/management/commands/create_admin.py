from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Admin superuser yaratish'

    def handle(self, *args, **options):
        username = 'admin'
        password = 'admin12345'
        email = 'admin@bookjavon.uz'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(f'"{username}" allaqachon mavjud!'))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            full_name='Admin'
        )
        self.stdout.write(self.style.SUCCESS(
            f'Superuser yaratildi!\n'
            f'  Username: {username}\n'
            f'  Password: {password}\n'
            f'  Email: {email}\n\n'
            f'Kirish: https://bookjavon-backend.onrender.com/admin/'
        ))
