"""Comando para popular o banco com dados de exemplo.

Uso:  python manage.py popular_dados
      python manage.py popular_dados --limpar

Cria as categorias de exemplo (se ainda nao existirem) e gastos dos ultimos
3 meses, para o dashboard ja abrir com numeros na tela.
"""
import random
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.utils import timezone

from gastos.models import Categoria, Gasto

# Cada categoria tem uma cor e uma lista de (descricao, valor minimo, valor maximo).
CATEGORIAS = {
    'Alimentacao': ('#e8590c', [('Almoco no RU', 8, 18), ('Mercado', 90, 320), ('Lanche', 12, 35),
                                ('Cafe', 6, 15), ('Delivery', 30, 80)]),
    'Transporte': ('#2a78d6', [('Passagem de onibus', 5, 10), ('Uber', 12, 45), ('Gasolina', 80, 220),
                               ('Estacionamento', 8, 25)]),
    'Moradia': ('#7048e8', [('Aluguel', 700, 1200), ('Conta de luz', 90, 210), ('Internet', 80, 130),
                            ('Conta de agua', 40, 90)]),
    'Educacao': ('#2f9e44', [('Livro', 45, 160), ('Curso online', 30, 200), ('Material de estudo', 20, 70)]),
    'Lazer': ('#d6336c', [('Cinema', 20, 45), ('Streaming', 20, 55), ('Show', 60, 180),
                          ('Bar com amigos', 40, 130)]),
    'Saude': ('#0c8599', [('Farmacia', 25, 120), ('Consulta', 90, 250), ('Academia', 70, 130)]),
}


class Command(BaseCommand):
    help = 'Cria categorias e gastos de exemplo dos ultimos 3 meses.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limpar',
            action='store_true',
            help='Apaga todos os gastos e categorias antes de popular.',
        )

    def handle(self, *args, **opcoes):
        # Semente fixa: todo mundo na sala gera os mesmos dados.
        random.seed(42)

        if opcoes['limpar']:
            # Gastos primeiro: a categoria e PROTECT e nao apaga se tiver gasto.
            Gasto.objects.all().delete()
            Categoria.objects.all().delete()
            self.stdout.write('Dados anteriores apagados.')

        categorias = {}
        for nome, (cor, _) in CATEGORIAS.items():
            categorias[nome], _ = Categoria.objects.get_or_create(nome=nome, defaults={'cor': cor})

        hoje = timezone.localdate()
        criados = 0

        for dias_atras in range(90):
            data = hoje - timedelta(days=dias_atras)

            # O mes atual e o que abre no dashboard: enche ele um pouco mais.
            maximo_por_dia = 4 if data.month == hoje.month else 3

            for _ in range(random.randint(1, maximo_por_dia)):
                nome_categoria = random.choice(list(categorias))
                descricao, minimo, maximo = random.choice(CATEGORIAS[nome_categoria][1])

                Gasto.objects.create(
                    descricao=descricao,
                    valor=Decimal(random.randint(minimo * 100, maximo * 100)) / 100,
                    data=data,
                    categoria=categorias[nome_categoria],
                )
                criados += 1

        self.stdout.write(self.style.SUCCESS(
            f'{len(categorias)} categorias e {criados} gastos criados.'
        ))
