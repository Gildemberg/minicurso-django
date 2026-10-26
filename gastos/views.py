from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
from .forms import CategoriaForm, GastoForm
from .models import Categoria, Gasto


def gasto_lista(request):
    gastos = Gasto.objects.select_related('categoria')
    return render(request, 'gastos/gasto_lista.html', {'gastos': gastos})


def gasto_novo(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gastos:gasto_lista')
    else:
        form = GastoForm()

    return render(request, 'gastos/gasto_form.html', {'form': form})


def gasto_editar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)   # <-- a diferenca
        if form.is_valid():
            form.save()
            return redirect('gastos:gasto_lista')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'gastos/gasto_form.html', {'form': form})


def gasto_excluir(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        gasto.delete()
        return redirect('gastos:gasto_lista')
    return render(request, 'gastos/confirmar_exclusao.html', {'objeto': gasto})


def categoria_lista(request):
    categorias = Categoria.objects.annotate(
        quantidade=Count('gastos'),
        total=Sum('gastos__valor'),
    ).order_by('nome')
    return render(request, 'gastos/categoria_lista.html', {'categorias': categorias})


def categoria_nova(request):
    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria criada.')
            return redirect('gastos:categoria_lista')
    else:
        form = CategoriaForm()
    return render(request, 'gastos/categoria_form.html', {'form': form})


def categoria_editar(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada.')
            return redirect('gastos:categoria_lista')
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'gastos/categoria_form.html', {'form': form})


def categoria_excluir(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)

    # on_delete=PROTECT impede apagar categoria em uso: avisamos antes de tentar.
    if categoria.gastos.exists():
        messages.error(request, f'A categoria "{categoria}" tem gastos e nao pode ser excluida.')
        return redirect('gastos:categoria_lista')

    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoria excluida.')
        return redirect('gastos:categoria_lista')
    return render(request, 'gastos/confirmar_exclusao.html', {
        'objeto': categoria,
        'voltar_para': 'gastos:categoria_lista',
    })
