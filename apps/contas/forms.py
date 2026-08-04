from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CadastroForm(UserCreationForm):
    """Formulario de criacao de conta.

    Herda do UserCreationForm, que ja traz os dois campos de senha, a
    conferencia entre eles e a validacao contra AUTH_PASSWORD_VALIDATORS
    (tamanho minimo, senha comum, senha so de numeros...).
    """

    email = forms.EmailField(
        label='E-mail',
        required=True,   # no User padrao o email e opcional; aqui exigimos
        help_text='Usado para recuperar a senha.',
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Nome de usuario'
        self.fields['username'].help_text = 'Letras, numeros e @ . + - _'
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirme a senha'

    def clean_email(self):
        """Impede dois cadastros com o mesmo e-mail.

        O model User NAO exige e-mail unico. Sem esta checagem, dois usuarios
        com o mesmo e-mail receberiam ambos o link de redefinir senha - e o
        dono do e-mail nao saberia qual conta esta redefinindo.
        """
        email = self.cleaned_data['email']

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ja existe uma conta com esse e-mail.')

        return email
