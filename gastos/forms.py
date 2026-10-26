from django import forms
from .models import Categoria, Gasto


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'data', 'categoria']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'cor']
        widgets = {
            'cor': forms.TextInput(attrs={'type': 'color'}),
        }

    def clean_nome(self):
        nome = self.cleaned_data['nome']
        repetidas = Categoria.objects.filter(nome__iexact=nome)
        if self.instance.pk:                       # editando: ignora ela mesma
            repetidas = repetidas.exclude(pk=self.instance.pk)
        if repetidas.exists():
            raise forms.ValidationError('Ja existe uma categoria com esse nome.')
        return nome
