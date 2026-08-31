import os
import logging
import threading
from django.apps import AppConfig

logger = logging.getLogger(__name__)# Bot haqida ma'lumotlar — views.py dan import qilinadi


class BooksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'books'
    verbose_name = 'Kitoblar'
