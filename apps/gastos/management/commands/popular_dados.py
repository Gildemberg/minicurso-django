"""Comando para popular o banco com dados de exemplo.

Uso:  python manage.py popular_dados
      python manage.py popular_dados --limpar

Cria DOIS usuarios, cada um com as suas proprias categorias e gastos. E o que
permite demonstrar em aula que um nao enxerga os dados do outro.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.gastos.models import Categoria, Gasto

# Dois usuarios para dar para comparar as duas contas lado a lado.
USUARIOS = ['ana', 'bruno']
SENHA_EXEMPLO = 'senha-de-teste-123'

# As categorias sao as mesmas que toda conta nova recebe (Categoria.PADROES),
# para nao ter duas listas para manter em sincronia.
DESCRICOES = {
    'Alimentacao': [('Almoco no RU', 8, 18), ('Mercado', 90, 320), ('Lanche', 12, 35),
                    ('Cafe', 6, 15), ('Delivery', 30, 80)],
    'Transporte': [('Passagem de onibus', 5, 10), ('Uber', 12, 45), ('Gasolina', 80, 220),
                   ('Estacionamento', 8, 25)],
    'Moradia': [('Aluguel', 700, 1200), ('Conta de luz', 90, 210), ('Internet', 80, 130),
                ('Conta de agua', 40, 90)],
    'Educacao': [('Livro', 45, 160), ('Curso online', 30, 200), ('Material de estudo', 20, 70)],
    'Lazer': [('Cinema', 20, 45), ('Streaming', 20, 55), ('Show', 60, 180), ('Bar com amigos', 40, 130)],
    'Saude': [('Farmacia', 25, 120), ('Consulta', 90, 250), ('Academia', 70, 130)],
}


class Command(BaseCommand):
    help = 'Cria categorias e gastos de exemplo dos ultimos 3 meses.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Apaga os gastos e categorias dos usuarios de exemplo antes de popular.',
        )

    def handle(self, *args, **opcoes):
        # Semente fixa: todo mundo na sala gera os mesmos dados.
        random.seed(42)

        usuarios = [self._criar_usuario(nome) for nome in USUARIOS]

        if opcoes['limpar']:
            Gasto.objects.filter(usuario__in=usuarios).delete()
            Categoria.objects.filter(usuario__in=usuarios).delete()
            self.stdout.write('Dados anteriores dos usuarios de exemplo apagados.')

        for usuario in usuarios:
            categorias, gastos = self._popular_para(usuario)
            self.stdout.write(self.style.SUCCESS(
                f'  {usuario.username}: {categorias} categorias, {gastos} gastos'
            ))

        self.stdout.write('')
        self.stdout.write('Usuarios de exemplo (senha: %s):' % SENHA_EXEMPLO)
        for usuario in usuarios:
            self.stdout.write(f'  {usuario.username}')
        self.stdout.write(self.style.WARNING(
            'Senha fraca de proposito - isto e um comando de desenvolvimento.'
        ))

    def _criar_usuario(self, username):
        usuario, novo = User.objects.get_or_create(
            username=username,
            defaults={'email': f'{username}@exemplo.com'},
        )
        if novo:
            usuario.set_password(SENHA_EXEMPLO)   # nunca gravar senha em texto puro
            usuario.save()
        return usuario

    def _popular_para(self, usuario):
        """Cria as categorias e os gastos de UM usuario."""
        Categoria.criar_padroes_para(usuario)

        # So as categorias para as quais temos descricoes de exemplo: se o
        # usuario tiver criado outras, elas ficam de fora em vez de dar erro.
        categorias = {
            c.nome: c
            for c in Categoria.objects.filter(usuario=usuario)
            if c.nome in DESCRICOES
        }

        hoje = timezone.localdate()
        criados = 0

        for dias_atras in range(90):
            data = hoje - timedelta(days=dias_atras)

            # O mes atual e o que abre no dashboard: enche ele um pouco mais.
            maximo_por_dia = 4 if data.month == hoje.month else 3

            for _ in range(random.randint(1, maximo_por_dia)):
                nome_categoria = random.choice(list(categorias))
                descricao, minimo, maximo = random.choice(DESCRICOES[nome_categoria])

                Gasto.objects.create(
                    usuario=usuario,
                    descricao=descricao,
                    valor=Decimal(random.randint(minimo * 100, maximo * 100)) / 100,
                    data=data,
                    categoria=categorias[nome_categoria],
                )
                criados += 1

        return len(categorias), criados
