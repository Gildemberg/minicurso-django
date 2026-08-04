from django.contrib import messages
from django.contrib.auth import login
from django.shortcuts import redirect, render

from apps.gastos.models import Categoria

from .forms import CadastroForm


def cadastro(request):
    """Cria uma conta nova pelo site, sem passar pelo /admin/."""
    # Quem ja esta logado nao tem o que fazer aqui.
    if request.user.is_authenticated:
        return redirect('gastos:dashboard')

    if request.method == 'POST':
        form = CadastroForm(request.POST)
        if form.is_valid():
            usuario = form.save()   # o UserCreationForm ja grava a senha com hash

            # Conta nova nao tem categoria nenhuma - e sem categoria nao da
            # para lancar gasto. Damos um conjunto inicial para a pessoa
            # conseguir usar o sistema no primeiro minuto.
            Categoria.criar_padroes_para(usuario)

            # Ja entra logado: evita obrigar a digitar a senha duas vezes.
            login(request, usuario)

            messages.success(request, f'Conta criada. Bem-vindo(a), {usuario.username}!')
            return redirect('gastos:dashboard')
    else:
        form = CadastroForm()

    return render(request, 'registration/cadastro.html', {'form': form})
