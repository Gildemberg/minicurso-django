from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    """Uma categoria de gasto: Alimentacao, Transporte, Moradia...

    Cada usuario tem as SUAS categorias. A "Alimentacao" de um nao e a do outro.
    """

    # Paleta de cores sugerida (a mesma usada nas barras do dashboard).
    CORES = [
        ('#2a78d6', 'Azul'),
        ('#1baf7a', 'Verde-agua'),
        ('#eda100', 'Amarelo'),
        ('#008300', 'Verde'),
        ('#4a3aa7', 'Violeta'),
        ('#e34948', 'Vermelho'),
        ('#e87ba4', 'Rosa'),
        ('#eb6834', 'Laranja'),
    ]

    # settings.AUTH_USER_MODEL em vez de importar User direto: assim o projeto
    # continua funcionando se um dia voce trocar o model de usuario.
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,   # apagou o usuario, vao junto as categorias
        related_name='categorias',
        verbose_name='usuario',
    )
    nome = models.CharField('nome', max_length=50)
    cor = models.CharField('cor', max_length=7, choices=CORES, default='#2a78d6')

    class Meta:
        verbose_name = 'categoria'
        verbose_name_plural = 'categorias'
        ordering = ['nome']
        constraints = [
            # O nome so precisa ser unico DENTRO de cada usuario: duas pessoas
            # podem ter, cada uma, a sua "Alimentacao".
            models.UniqueConstraint(
                fields=['usuario', 'nome'],
                name='categoria_nome_unico_por_usuario',
            ),
        ]

    def __str__(self):
        # E isto que aparece no admin, nos <select> dos formularios etc.
        return self.nome

    def total_gasto(self):
        """Soma de todos os gastos desta categoria."""
        return self.gastos.aggregate(total=models.Sum('valor'))['total'] or 0


class Gasto(models.Model):
    """Um gasto individual, sempre ligado a um usuario e a uma categoria."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='gastos',
        verbose_name='usuario',
    )
    descricao = models.CharField('descricao', max_length=100)
    valor = models.DecimalField(
        'valor',
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
    )
    data = models.DateField('data', default=timezone.localdate)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,  # nao deixa apagar categoria que tem gastos
        related_name='gastos',     # permite categoria.gastos.all()
        verbose_name='categoria',
    )
    observacao = models.TextField('observacao', blank=True)
    criado_em = models.DateTimeField('criado em', auto_now_add=True)

    class Meta:
        verbose_name = 'gasto'
        verbose_name_plural = 'gastos'
        ordering = ['-data', '-id']  # mais recentes primeiro

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'
