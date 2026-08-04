"""Configuracao do projeto.

O que muda de maquina para maquina (chave secreta, modo debug, banco) NAO fica
aqui: fica no arquivo .env, que nao vai para o Git. Este arquivo apenas le de
la. Copie o .env.example para .env antes de rodar o projeto.
"""
from pathlib import Path

import environ

# Raiz do projeto: a pasta que contem o manage.py.
BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Variaveis de ambiente
# ---------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ['127.0.0.1', 'localhost']),
)
environ.Env.read_env(BASE_DIR / '.env')

# Sem valor padrao de proposito: se faltar no .env, o projeto avisa na hora.
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env('ALLOWED_HOSTS')


# ---------------------------------------------------------------------------
# Aplicacoes
# ---------------------------------------------------------------------------
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = []

# Nossos apps: todos moram dentro da pasta apps/.
LOCAL_APPS = [
    'apps.gastos',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # Pasta de templates na raiz do projeto (fora dos apps).
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
# DATABASE_URL vem do .env. Trocar SQLite por PostgreSQL depois e so mudar a
# URL para: postgres://usuario:senha@localhost:5432/nome_do_banco
DATABASES = {
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}


# ---------------------------------------------------------------------------
# Validacao de senha
# ---------------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Nao precisamos declarar AUTHENTICATION_BACKENDS: o padrao ja e o
# ModelBackend, exatamente o mesmo que o /admin/ usa. Mesma tabela de
# usuarios, mesma senha, mesma sessao - so muda a tela de entrada.

# Para onde o @login_required manda quem nao esta logado.
LOGIN_URL = 'login'

# Para onde vai depois de entrar e depois de sair.
LOGIN_REDIRECT_URL = 'gastos:dashboard'
LOGOUT_REDIRECT_URL = 'login'

# Nao ha recuperacao de senha por e-mail neste projeto, entao nao existe
# configuracao de EMAIL_* aqui. Quem esquece a senha pede para o
# administrador trocar no /admin/, ou usa:
#   python manage.py changepassword <usuario>


# ---------------------------------------------------------------------------
# Internacionalizacao
# ---------------------------------------------------------------------------
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_I18N = True
USE_TZ = True

# Formata numeros no padrao brasileiro: 1.234,56
USE_THOUSAND_SEPARATOR = True


# ---------------------------------------------------------------------------
# Arquivos estaticos e de midia
# ---------------------------------------------------------------------------
STATIC_URL = 'static/'

# Onde o Django procura os estaticos durante o desenvolvimento.
STATICFILES_DIRS = [BASE_DIR / 'static']

# Para onde o `collectstatic` copia tudo na hora de publicar.
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
