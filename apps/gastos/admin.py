"""Customizacao do painel administrativo.

Este arquivo esta organizado do mais simples para o mais avancado. Na aula,
mostre de cima para baixo: cada bloco e uma melhoria visivel no /admin/.
"""
import csv

from django.contrib import admin
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.utils.formats import number_format
from django.utils.html import format_html

from .models import Categoria, Gasto


def moeda(valor):
    """Formata um numero como dinheiro no padrao brasileiro."""
    if valor is None:
        valor = 0
    return f'R$ {number_format(valor, decimal_pos=2, force_grouping=True)}'


# ---------------------------------------------------------------------------
# Filtro customizado: agrupa os gastos por faixa de valor
# ---------------------------------------------------------------------------
class FaixaDeValorFilter(admin.SimpleListFilter):
    """Aparece na barra lateral junto com os filtros automaticos.

    `list_filter` so filtra por campo que existe. Quando o filtro que voce quer
    e uma REGRA (uma faixa, um intervalo, um calculo), escreve-se assim.
    """

    title = 'faixa de valor'
    parameter_name = 'faixa'   # vira ?faixa=... na URL

    def lookups(self, request, model_admin):
        """As opcoes que aparecem na lateral: (valor_na_url, texto_na_tela)."""
        return [
            ('baixo', 'Ate R$ 50'),
            ('medio', 'De R$ 50 a R$ 200'),
            ('alto', 'Acima de R$ 200'),
        ]

    def queryset(self, request, queryset):
        """Recebe a lista completa e devolve so o que casa com a opcao."""
        if self.value() == 'baixo':
            return queryset.filter(valor__lte=50)
        if self.value() == 'medio':
            return queryset.filter(valor__gt=50, valor__lte=200)
        if self.value() == 'alto':
            return queryset.filter(valor__gt=200)
        return queryset


# ---------------------------------------------------------------------------
# Acoes em lote: aparecem no combo acima da listagem
# ---------------------------------------------------------------------------
@admin.action(description='Exportar selecionados para CSV')
def exportar_csv(modeladmin, request, queryset):
    resposta = HttpResponse(content_type='text/csv')
    resposta['Content-Disposition'] = 'attachment; filename="gastos.csv"'

    # O BOM e o ';' fazem o arquivo abrir certo no Excel em portugues.
    resposta.write('﻿')
    escritor = csv.writer(resposta, delimiter=';')
    escritor.writerow(['Data', 'Descricao', 'Categoria', 'Valor'])

    for gasto in queryset.select_related('categoria'):
        escritor.writerow([
            gasto.data.strftime('%d/%m/%Y'),
            gasto.descricao,
            gasto.categoria.nome,
            str(gasto.valor).replace('.', ','),
        ])

    return resposta


@admin.action(description='Duplicar selecionados')
def duplicar(modeladmin, request, queryset):
    for gasto in queryset:
        # pk=None faz o save() criar um registro novo em vez de atualizar.
        gasto.pk = None
        gasto.descricao = f'{gasto.descricao} (copia)'
        gasto.save()

    # Mensagem de retorno para o usuario - o admin ja sabe exibir.
    modeladmin.message_user(request, f'{queryset.count()} gasto(s) duplicado(s).')


# ---------------------------------------------------------------------------
# Inline: os gastos aparecem DENTRO da tela da categoria
# ---------------------------------------------------------------------------
class GastoInline(admin.TabularInline):
    model = Gasto
    extra = 0                  # nao mostra linhas em branco
    max_num = 10               # evita carregar centenas de linhas
    fields = ['data', 'descricao', 'valor']
    ordering = ['-data']
    show_change_link = True    # link para a tela completa do gasto
    verbose_name_plural = 'Ultimos gastos desta categoria'


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['amostra_de_cor', 'nome', 'usuario', 'quantidade_de_gastos', 'total_gasto']
    list_display_links = ['nome']
    list_filter = ['usuario']
    list_select_related = ['usuario']
    search_fields = ['nome']   # obrigatorio para o autocomplete do GastoAdmin
    autocomplete_fields = ['usuario']
    inlines = [GastoInline]

    # Explicito de proposito: o annotate() abaixo cria um GROUP BY, e nesse
    # caso o Django deixa de enxergar o ordering do Meta e emite um aviso.
    ordering = ['nome']

    def get_queryset(self, request):
        """Anota os totais numa consulta so, em vez de uma por linha."""
        return super().get_queryset(request).annotate(
            _total=Sum('gastos__valor'),
            _quantidade=Count('gastos'),
        )

    @admin.display(description='cor')
    def amostra_de_cor(self, obj):
        # format_html escapa os valores antes de montar o HTML - nunca use
        # f-string para gerar HTML, e assim que nasce uma falha de XSS.
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;'
            'border-radius:4px;background:{}"></span>',
            obj.cor,
        )

    @admin.display(description='lancamentos', ordering='_quantidade')
    def quantidade_de_gastos(self, obj):
        return obj._quantidade

    @admin.display(description='total gasto', ordering='_total')
    def total_gasto(self, obj):
        return moeda(obj._total)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    # --- Listagem ---------------------------------------------------------
    list_display = ['data', 'descricao', 'usuario', 'categoria_colorida', 'valor']
    list_display_links = ['descricao']
    list_editable = ['valor']          # edita direto na listagem, sem abrir
    list_filter = ['usuario', 'categoria', FaixaDeValorFilter, 'data']
    search_fields = ['descricao', 'observacao']
    date_hierarchy = 'data'            # navegacao por ano/mes/dia no topo
    list_per_page = 25
    list_select_related = ['categoria', 'usuario']  # evita N+1
    ordering = ['-data']

    # --- Formulario -------------------------------------------------------
    autocomplete_fields = ['categoria', 'usuario']  # <select> com busca
    readonly_fields = ['criado_em']

    # Agrupa os campos em secoes, em vez de uma lista corrida.
    fieldsets = [
        (None, {
            'fields': ['usuario', 'descricao', 'valor', 'data', 'categoria'],
        }),
        ('Detalhes', {
            'fields': ['observacao', 'criado_em'],
            'classes': ['collapse'],   # secao comeca recolhida
        }),
    ]

    actions = [exportar_csv, duplicar]

    @admin.display(description='categoria', ordering='categoria__nome')
    def categoria_colorida(self, obj):
        return format_html(
            '<span style="display:inline-block;width:10px;height:10px;'
            'border-radius:3px;background:{};margin-right:6px"></span>{}',
            obj.categoria.cor,
            obj.categoria.nome,
        )

    def changelist_view(self, request, extra_context=None):
        """Mostra no titulo da pagina o total do que esta filtrado na tela.

        Truque util: chamamos o comportamento padrao primeiro e so entao
        pegamos o queryset ja filtrado, que fica em context_data['cl'].
        """
        resposta = super().changelist_view(request, extra_context)

        try:
            gastos_na_tela = resposta.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return resposta   # a pagina nao e a listagem (ex.: um redirect)

        total = gastos_na_tela.aggregate(total=Sum('valor'))['total']
        resposta.context_data['title'] = f'Gastos — total filtrado: {moeda(total)}'
        return resposta
