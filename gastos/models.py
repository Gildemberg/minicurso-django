from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    cor = models.CharField(max_length=7, default='#2a78d6')

    def __str__(self):
        return self.nome


class Gasto(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.localdate)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='gastos',
    )

    class Meta:
        ordering = ['-data', '-id']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'
