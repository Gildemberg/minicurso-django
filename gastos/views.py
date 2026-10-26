from django.shortcuts import get_object_or_404, redirect, render
from .forms import GastoForm
from .models import Gasto


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
