from django.shortcuts import render
from .models import Gasto


def gasto_lista(request):
    gastos = Gasto.objects.select_related('categoria')
    return render(request, 'gastos/gasto_lista.html', {'gastos': gastos})
