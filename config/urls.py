"""URLs do projeto.

Tudo que chega no servidor passa por aqui primeiro. O `include` repassa as
URLs do site para o arquivo apps/gastos/urls.py.
"""
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

# Identidade do painel: troca o "Django administration" por um nome nosso.
# Tres linhas, efeito imediato - bom para abrir o bloco de admin na aula.
admin.site.site_header = 'Controle de Gastos'
admin.site.site_title = 'Controle de Gastos'
admin.site.index_title = 'Administracao do sistema'

urlpatterns = [
    path('admin/', admin.site.urls),

    # Autenticacao: usamos as views prontas do django.contrib.auth, uma por
    # uma, em vez de `include('django.contrib.auth.urls')`.
    #
    # POR QUE UMA POR UMA: aquele include registra TAMBEM as quatro rotas de
    # "esqueci minha senha". Como o django.contrib.admin traz templates
    # proprios em registration/, essas rotas passariam a funcionar sozinhas -
    # com a cara do admin e sem e-mail configurado. Listando so o que a gente
    # quer, /contas/password_reset/ simplesmente nao existe.
    #
    # Os templates ficam em templates/registration/ (o nome da pasta e fixo,
    # nao acompanha o /contas/ da URL).
    path('contas/login/', auth_views.LoginView.as_view(), name='login'),

    # O logout SO aceita POST no Django 5 - no template use um <form>.
    path('contas/logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Trocar a senha estando logado. Exige a senha atual, e o nome
    # `password_change_done` e obrigatorio: e para la que a view redireciona.
    path('contas/senha/', auth_views.PasswordChangeView.as_view(), name='password_change'),
    path('contas/senha/ok/', auth_views.PasswordChangeDoneView.as_view(),
         name='password_change_done'),

    path('', include('apps.gastos.urls')),
]
