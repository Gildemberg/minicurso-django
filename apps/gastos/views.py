"""Views do sistema.

REGRA DE OURO deste arquivo: nenhuma consulta sai daqui sem filtrar por
`request.user`. Se esquecer em UMA view, um usuario ve o dinheiro do outro.
Por isso todo acesso a objeto usa `get_object_or_404(..., usuario=request.user)`
em vez de so `pk=pk`.
"""
from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import CategoriaForm, GastoForm
from .models import Categoria, Gasto


def _primeiro_dia_do_mes(texto, padrao=None):
    """Converte o texto 'AAAA-MM' (vindo do <input type="month">) em uma data.

    Se o texto for invalido ou vazio, devolve `padrao`.
    """
    try:
        ano, mes = texto.split('-')
        return date(int(ano), int(mes), 1)
    except (AttributeError, ValueError):
        return padrao


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    """Resumo do mes: totais, gasto por categoria e ultimos lancamentos."""
    hoje = timezone.localdate()
    mes = _primeiro_dia_do_mes(request.GET.get('mes'), padrao=hoje.replace(day=1))

    gastos_do_mes = Gasto.objects.filter(
        usuario=request.user,
        data__year=mes.year,
        data__month=mes.month,
    )

    resumo = gastos_do_mes.aggregate(total=Sum('valor'), quantidade=Count('id'))
    total = resumo['total'] or Decimal('0')
    quantidade = resumo['quantidade']

    # Agrupa os gastos por categoria e soma o valor de cada grupo.
    # Equivale a: SELECT categoria, SUM(valor) ... GROUP BY categoria
    agrupado = (
        gastos_do_mes
        .values('categoria__nome', 'categoria__cor')
        .annotate(total=Sum('valor'), quantidade=Count('id'))
        .order_by('-total')
    )

    # Calcula a fatia (%) de cada categoria - e a largura da barra no template.
    por_categoria = [
        {
            'nome': linha['categoria__nome'],
            'cor': linha['categoria__cor'],
            'total': linha['total'],
            'quantidade': linha['quantidade'],
            'percentual': round(linha['total'] / total * 100, 1) if total else 0,
        }
        for linha in agrupado
    ]

    contexto = {
        'mes': mes,
        'mes_input': mes.strftime('%Y-%m'),
        'total': total,
        'quantidade': quantidade,
        'media': total / quantidade if quantidade else Decimal('0'),
        'maior_gasto': gastos_do_mes.select_related('categoria').order_by('-valor').first(),
        'por_categoria': por_categoria,
        'ultimos_gastos': gastos_do_mes.select_related('categoria')[:5],
    }
    return render(request, 'gastos/dashboard.html', contexto)


# ---------------------------------------------------------------------------
# Gastos (CRUD)
# ---------------------------------------------------------------------------

@login_required
def gasto_lista(request):
    """Lista os gastos, com busca e filtros por categoria e por mes."""
    gastos = Gasto.objects.filter(usuario=request.user).select_related('categoria')

    busca = request.GET.get('busca', '').strip()
    categoria_id = request.GET.get('categoria', '')
    mes_texto = request.GET.get('mes', '')

    if busca:
        gastos = gastos.filter(descricao__icontains=busca)

    if categoria_id:
        gastos = gastos.filter(categoria_id=categoria_id)

    mes = _primeiro_dia_do_mes(mes_texto)
    if mes:
        gastos = gastos.filter(data__year=mes.year, data__month=mes.month)

    contexto = {
        'gastos': gastos,
        'categorias': Categoria.objects.filter(usuario=request.user),
        'total': gastos.aggregate(total=Sum('valor'))['total'] or Decimal('0'),
        # Devolvidos para o template manter os filtros preenchidos.
        'busca': busca,
        'categoria_id': categoria_id,
        'mes_input': mes_texto,
    }
    return render(request, 'gastos/gasto_lista.html', contexto)


@login_required
def gasto_novo(request):
    if request.method == 'POST':
        form = GastoForm(request.POST, usuario=request.user)
        if form.is_valid():
            # commit=False monta o objeto sem gravar, para a gente definir o
            # dono antes. O usuario JAMAIS vem do formulario.
            gasto = form.save(commit=False)
            gasto.usuario = request.user
            gasto.save()

            messages.success(request, 'Gasto cadastrado com sucesso.')
            return redirect('gastos:gasto_lista')
    else:
        form = GastoForm(usuario=request.user)

    return render(request, 'gastos/gasto_form.html', {
        'form': form,
        'titulo': 'Novo gasto',
    })


@login_required
def gasto_editar(request, pk):
    # O `usuario=request.user` aqui e o que impede alguem de editar o gasto de
    # outra pessoa trocando o numero na URL. Da 404, e nao 403: para quem nao e
    # dono, o registro simplesmente nao existe.
    gasto = get_object_or_404(Gasto, pk=pk, usuario=request.user)

    if request.method == 'POST':
        # `instance=gasto` faz o form ATUALIZAR esse registro em vez de criar outro.
        form = GastoForm(request.POST, instance=gasto, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Gasto atualizado com sucesso.')
            return redirect('gastos:gasto_lista')
    else:
        form = GastoForm(instance=gasto, usuario=request.user)

    return render(request, 'gastos/gasto_form.html', {
        'form': form,
        'titulo': 'Editar gasto',
        'objeto': gasto,
    })


@login_required
def gasto_excluir(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk, usuario=request.user)

    # So apaga no POST: um GET nunca deve alterar dados.
    if request.method == 'POST':
        gasto.delete()
        messages.success(request, 'Gasto excluido.')
        return redirect('gastos:gasto_lista')

    return render(request, 'gastos/confirmar_exclusao.html', {
        'objeto': gasto,
        'tipo': 'gasto',
        'voltar_para': 'gastos:gasto_lista',
    })


# ---------------------------------------------------------------------------
# Categorias (CRUD)
# ---------------------------------------------------------------------------

@login_required
def categoria_lista(request):
    categorias = Categoria.objects.filter(usuario=request.user).annotate(
        quantidade=Count('gastos'),
        total=Sum('gastos__valor'),
    )
    return render(request, 'gastos/categoria_lista.html', {'categorias': categorias})


@login_required
def categoria_nova(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST, usuario=request.user)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()

            messages.success(request, 'Categoria criada com sucesso.')
            return redirect('gastos:categoria_lista')
    else:
        form = CategoriaForm(usuario=request.user)

    return render(request, 'gastos/categoria_form.html', {
        'form': form,
        'titulo': 'Nova categoria',
    })


@login_required
def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso.')
            return redirect('gastos:categoria_lista')
    else:
        form = CategoriaForm(instance=categoria, usuario=request.user)

    return render(request, 'gastos/categoria_form.html', {
        'form': form,
        'titulo': 'Editar categoria',
        'objeto': categoria,
    })


@login_required
def categoria_excluir(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk, usuario=request.user)

    # on_delete=PROTECT impede apagar categoria em uso: avisamos antes de tentar.
    if categoria.gastos.exists():
        messages.error(
            request,
            f'A categoria "{categoria}" tem gastos lancados e nao pode ser excluida.',
        )
        return redirect('gastos:categoria_lista')

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluida.')
        return redirect('gastos:categoria_lista')

    return render(request, 'gastos/confirmar_exclusao.html', {
        'objeto': categoria,
        'tipo': 'categoria',
        'voltar_para': 'gastos:categoria_lista',
    })
