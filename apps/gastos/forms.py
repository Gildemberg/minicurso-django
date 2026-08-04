from decimal import Decimal

from django import forms

from .models import Categoria, Gasto


class CampoValor(forms.DecimalField):
    """Campo de dinheiro que aceita virgula OU ponto.

    Sem isto, quem digita "42,50" recebe "Informe um numero." - e o brasileiro
    digita virgula. (Extra de acabamento: da para ensinar so no final da aula.)
    """

    def to_python(self, valor):
        if isinstance(valor, str):
            valor = valor.replace(',', '.')
        return super().to_python(valor)


class GastoForm(forms.ModelForm):
    """Formulario gerado a partir do model Gasto.

    O campo `usuario` NAO aparece aqui de proposito: quem define o dono e a
    view, a partir de request.user. Campo de dono nunca vem do formulario.
    """

    # Declarar o campo aqui substitui o que o ModelForm geraria sozinho.
    valor = CampoValor(
        label='Valor',
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01'),
        widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
    )

    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'data', 'categoria', 'observacao']
        widgets = {
            'descricao': forms.TextInput(attrs={'placeholder': 'Ex.: Almoco no RU'}),
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'observacao': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Garante que o <input type="date"> receba a data no formato que ele entende.
        self.fields['data'].input_formats = ['%Y-%m-%d']
        self.fields['categoria'].empty_label = 'Selecione uma categoria'
        self.fields['observacao'].required = False

        # SEGURANCA: limitar o queryset nao e so cosmetico. Alem de mostrar so
        # as categorias do usuario no <select>, isso faz o Django REJEITAR um
        # POST com o id de uma categoria de outra pessoa.
        if usuario is not None:
            self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nome', 'cor']
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex.: Alimentacao'}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario

    def clean_nome(self):
        """Impede duas categorias com o mesmo nome para o MESMO usuario.

        O banco ja garante isso pela UniqueConstraint do model. Aqui a gente
        repete a checagem so para dar uma mensagem boa, no campo certo, em vez
        do erro generico que o banco produziria.
        """
        nome = self.cleaned_data['nome']

        if self.usuario is None:
            return nome

        repetidas = Categoria.objects.filter(usuario=self.usuario, nome__iexact=nome)
        if self.instance.pk:
            repetidas = repetidas.exclude(pk=self.instance.pk)   # editando: ignora ela mesma

        if repetidas.exists():
            raise forms.ValidationError('Voce ja tem uma categoria com esse nome.')

        return nome
