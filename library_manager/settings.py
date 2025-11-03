from pathlib import Path
import os
import dj_database_url
from django.core.management.utils import get_random_secret_key
import dotenv

# ==============================
# 🧩 CARREGAR VARIÁVEIS DE AMBIENTE
# ==============================
# Isso garante que o .env seja carregado automaticamente
BASE_DIR = Path(__file__).resolve().parent.parent
dotenv.load_dotenv(os.path.join(BASE_DIR, '.env'))  # ✅ corrigido: converte Path para string

# ==============================
# 🔐 CONFIGURAÇÕES DE SEGURANÇA
# ==============================
SECRET_KEY = os.getenv('SECRET_KEY', default=get_random_secret_key())
DEBUG = os.getenv('DEBUG', 'True').lower() in ['true', '1', 'yes']
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '*').split(',')

# ==============================
# ⚙️ APLICAÇÕES INSTALADAS
# ==============================
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Aplicações locais e externas
    'core',
    'django_bootstrap5',
    'storages',  # Integração com AWS S3
    'csp',       # Content Security Policy
    'django_extensions',
]

# ==============================
# 🧱 MIDDLEWARE
# ==============================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]

# ==============================
# 🌐 URLS E WSGI
# ==============================
ROOT_URLCONF = 'library_manager.urls'
WSGI_APPLICATION = 'library_manager.wsgi.application'

# ==============================
# 🧩 TEMPLATES
# ==============================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'core/templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ==============================
# 💾 BANCO DE DADOS
# ==============================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

database_url = os.getenv('JAWSDB_URL')
if database_url:
    DATABASES['default'] = dict(dj_database_url.parse(database_url))
elif DEBUG and os.getenv('DB_ENGINE') == 'django.db.backends.mysql':
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'DJANGO_G',
        'USER': 'djangoadmin',
        'PASSWORD': '100902',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }

DATABASES['default']['CONN_MAX_AGE'] = 600

# ==============================
# ⚡ CACHE E SESSÕES
# ==============================
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# ==============================
# 🔑 SENHAS E AUTENTICAÇÃO
# ==============================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ==============================
# 🌍 LOCALIZAÇÃO
# ==============================
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# ==============================
# 📦 ARQUIVOS ESTÁTICOS
# ==============================
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_MAX_AGE = 31536000  # 1 ano de cache

# ==============================
# ☁️ AWS S3 CONFIG (UPLOADS)
# ==============================
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'garoca1')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-2')
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.amazonaws.com"
AWS_QUERYSTRING_AUTH = False  # URLs permanentes

# 📁 Uploads e Mídia (S3 sempre ativo)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# ==============================
# ⚙️ OUTRAS CONFIGURAÇÕES
# ==============================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DEFAULT_CHARSET = 'utf-8'
AUTH_USER_MODEL = 'core.Leitor'

# ==============================
# 🔐 LOGIN E SEGURANÇA
# ==============================
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/perfil/'
LOGOUT_REDIRECT_URL = '/login/'

SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_SSL_REDIRECT = not DEBUG
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not DEBUG
SECURE_HSTS_PRELOAD = not DEBUG
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# ==============================
# 🧱 CONTENT SECURITY POLICY
# ==============================
CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "child-src": ("'self'", "blob:"),
        "default-src": ("'self'",),
        "font-src": (
            "'self'",
            "https://cdnjs.cloudflare.com",
            "https://cdn.jsdelivr.net",
            "https://stackpath.bootstrapcdn.com",
            "data:",
        ),
        "frame-ancestors": ("'self'",),
        "img-src": ("'self'", "blob:", "data:", f"https://{AWS_S3_CUSTOM_DOMAIN}"),
        "script-src": (
            "'self'",
            "https://stackpath.bootstrapcdn.com",
            "https://code.jquery.com",
            "https://cdn.jsdelivr.net",
            "https://cdnjs.cloudflare.com",
            "'unsafe-inline'",
        ),
        "style-src": (
            "'self'",
            "https://stackpath.bootstrapcdn.com",
            "https://cdnjs.cloudflare.com",
            "https://cdn.jsdelivr.net",
            "'unsafe-inline'",
        ),
        "worker-src": ("'self'", "blob:"),
    }
}

# ==============================
# 🚫 CACHE CONTROL MIDDLEWARE
# ==============================
from django.utils.cache import patch_cache_control
from django.utils.deprecation import MiddlewareMixin

class CacheControlMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if request.path.startswith('/login/') or request.path.startswith('/perfil/'):
            patch_cache_control(response, no_cache=True, no_store=True, must_revalidate=True)
        elif request.path.startswith('/static/'):
            patch_cache_control(response, public=True, max_age=WHITENOISE_MAX_AGE, immutable=True)
        else:
            patch_cache_control(response, public=True, max_age=3600)
        return response

MIDDLEWARE.append('library_manager.settings.CacheControlMiddleware')

# ==============================
# 🧾 LOGGING
# ==============================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG' if DEBUG else 'ERROR',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG' if DEBUG else 'ERROR',
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': False,
        },
        'storages.backends.s3boto3': {
            'handlers': ['console'],
            'level': 'DEBUG' if DEBUG else 'ERROR',
            'propagate': False,
        },
    }
}

