"""
Paramètres de test : base SQLite locale et isolée.
Les tests ne créent ainsi aucune base de test sur l'instance Supabase partagée par l'équipe.

Usage : uv run python manage.py test --settings=cargolink.settings_test
"""
from .settings import *  # noqa: F401,F403

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_cargolink.sqlite3',  # noqa: F405
    }
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

# Les tests n'appellent jamais d'API IA réelle
DEEPSEEK_API_KEY = ''
MEDIA_ROOT = BASE_DIR / 'media_test'  # noqa: F405

# Cache CargoLink AI désactivé : chaque test simule ses propres réponses
CARGOLINK_AI_CACHE_SECONDS = 0
