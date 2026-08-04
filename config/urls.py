"""URLs do projeto.

Tudo que chega no servidor passa por aqui primeiro. O `include` repassa as
URLs do site para o arquivo apps/gastos/urls.py.
"""
from django.contrib import admin
from django.urls import include, path

# Identidade do painel: troca o "Django administration" por um nome nosso.
# Tres linhas, efeito imediato - bom para abrir o bloco de admin na aula.
admin.site.site_header = 'Controle de Gastos'
admin.site.site_title = 'Controle de Gastos'
admin.site.index_title = 'Administracao do sistema'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Nossas telas de conta (cadastro). Vem ANTES do include do contrib.auth
    # para poder sobrescrever alguma rota dele se um dia for preciso.
    path('contas/', include('apps.contas.urls')),

    # Login, logout, troca e reset de senha - as views ja vem prontas, so
    # fornecemos os templates. Usa o MESMO backend de autenticacao do admin.
    # Atencao: os templates vao em templates/registration/, e nao em contas/.
    path('contas/', include('django.contrib.auth.urls')),

    path('', include('apps.gastos.urls')),
]
