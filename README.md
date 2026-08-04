# Controle de Gastos — minicurso de Django

Sistema web de controle de gastos pessoais com categorias, construído do zero
com Django. Este é o **projeto de referência** do minicurso: o estado final,
pronto, que a turma vai chegar junto com você ao longo da noite.

O passo a passo da aula está em **[ROTEIRO.md](ROTEIRO.md)**.

---

## O que o sistema faz

- **Multiusuário** — cada pessoa entra com seu login e vê **apenas os próprios
  gastos e categorias**. Usa o mesmo backend de autenticação do `/admin/`
  (`ModelBackend`), mesma tabela de usuários, mesma sessão — só muda a porta
  de entrada.
- **Dashboard** — total do mês, média por lançamento, maior gasto e uma barra
  por categoria mostrando quanto cada uma representa.
- **Gastos** — cadastrar, listar, editar e excluir, com busca por descrição e
  filtros por categoria e por mês.
- **Categorias** — cadastrar, listar, editar e excluir, cada uma com sua cor.
- **Admin do Django** — bem além do `register()` padrão: colunas coloridas,
  filtro por faixa de valor, edição direta na listagem, exportação em CSV,
  gastos embutidos na tela da categoria e o **total do que está filtrado** no
  topo da página. Detalhes no [apêndice do roteiro](ROTEIRO.md).

## Como rodar

```bash
# 1. Ativar o ambiente virtual
source venv/bin/activate          # Linux / macOS
venv\Scripts\activate             # Windows

# 2. Instalar as dependências
pip install -r requirements.txt

# 3. Criar o arquivo de configuração local
cp .env.example .env              # Linux / macOS
copy .env.example .env            # Windows

# 4. Gerar uma SECRET_KEY e colar no .env
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 5. Criar o banco de dados
python manage.py migrate

# 6. Popular com dados de exemplo (cria os usuários ana e bruno)
python manage.py popular_dados

# 7. Criar o SEU usuário, com acesso ao /admin
python manage.py createsuperuser

# 8. Subir o servidor
python manage.py runserver
```

Abra **http://127.0.0.1:8000/** — você cai na tela de login. O admin fica em
**/admin/**.

### Usuários

| Usuário | Senha | Entra em |
|---|---|---|
| `ana` | `senha-de-teste-123` | só no sistema (`/contas/login/`) |
| `bruno` | `senha-de-teste-123` | só no sistema (`/contas/login/`) |
| o seu superusuário | a que você escolheu | no sistema **e** no `/admin/` |

`ana` e `bruno` existem para você demonstrar o isolamento: entre com um, veja
os totais, saia, entre com o outro — são dados completamente separados. As
senhas são fracas de propósito; o comando `popular_dados` é de desenvolvimento.

> Um usuário comum **não consegue** entrar no `/admin/`: o Django exige
> `is_staff=True` e responde *"insira um usuário e senha corretos para uma
> conta de equipe"*. É a separação de papéis funcionando.

Para recomeçar do zero: apague `db.sqlite3` e rode `migrate` de novo.

## Estrutura do projeto

```
manage.py                       ponto de entrada dos comandos
.env                            segredos e config local (NÃO vai para o Git)
.env.example                    modelo do .env (esse vai)
requirements.txt

config/                         CONFIGURAÇÃO do projeto — não é o sistema
├── settings.py                 apps, banco, idioma, templates, estáticos
├── urls.py                     roteador principal
├── wsgi.py                     ponto de entrada do servidor de produção
└── asgi.py

apps/                           TODOS os apps do sistema moram aqui
├── __init__.py                 faz o Python enxergar apps/ como pacote
└── gastos/
    ├── apps.py                 name='apps.gastos' + label='gastos'
    ├── models.py               Categoria e Gasto  → viram tabelas no banco
    ├── forms.py                formulários gerados a partir dos models
    ├── views.py                a lógica: recebe request, devolve response
    ├── urls.py                 as rotas do app
    ├── admin.py                registro dos models no painel admin
    ├── migrations/             histórico de mudanças no banco
    └── management/commands/
        └── popular_dados.py    gera dados de exemplo

templates/                      o HTML, fora dos apps
├── base.html                   layout comum (menu, mensagens)
└── gastos/                     uma página por template

static/css/estilo.css           CSS puro, sem framework
```

### Por que essa estrutura

| Decisão | Motivo |
|---|---|
| `config/` em vez de `controle_gastos/` | aquela pasta é **configuração**, não o sistema. Deixa óbvio qual arquivo abrir. |
| Apps dentro de `apps/` | a raiz não vira um amontoado de pastas conforme o projeto cresce. |
| `label = 'gastos'` no `apps.py` | sem ele o app se chamaria `apps.gastos` e as tabelas teriam nome esquisito. |
| Segredos no `.env` | `SECRET_KEY` no código é o vazamento mais comum do mundo Django. |
| `templates/` e `static/` na raiz | são do site inteiro, não de um app só. |
| `settings.AUTH_USER_MODEL` na FK | não amarra o projeto ao `User` padrão; trocar o model de usuário depois continua possível. |

### Como o isolamento entre usuários é garantido

São quatro camadas, e **todas as quatro são necessárias**:

| Camada | Onde | O que impede |
|---|---|---|
| `@login_required` | todas as views | acesso anônimo |
| `.filter(usuario=request.user)` | listagens e dashboard | ver dados alheios numa lista |
| `get_object_or_404(..., usuario=request.user)` | editar / excluir | trocar o id na URL e abrir o registro de outro (dá **404**, não 403) |
| `queryset` do campo `categoria` no form | `GastoForm.__init__` | mandar no POST o id de uma categoria de outra pessoa |

A quarta é a que costuma ser esquecida. Filtrar só o `<select>` na tela não
basta — quem manda o POST na mão passa direto. Limitar o `queryset` do campo
faz o **Django rejeitar** o valor na validação.

> O `usuario` **não está** no `fields` do formulário, de propósito. O dono é
> definido na view com `form.save(commit=False)`. Campo de dono nunca vem do
> cliente.

> **Atenção ao criar um app novo:** o `startapp` não sabe da pasta `apps/`.
> ```bash
> mkdir apps/relatorios
> python manage.py startapp relatorios apps/relatorios
> ```
> Depois **edite `apps/relatorios/apps.py`** e ajuste `name = 'apps.relatorios'`
> e `label = 'relatorios'`. Sem isso o Django não acha o app.

## O caminho de uma requisição

Vale desenhar isso no quadro — é o modelo mental que faz o Django encaixar:

```
navegador  →  config/urls.py  →  apps/gastos/urls.py  →  views.py
                                                            ↓
navegador  ←      HTML       ←      template        ←    models.py (banco)
```

## Comandos úteis

| Comando | O que faz |
|---|---|
| `python manage.py runserver` | sobe o servidor de desenvolvimento |
| `python manage.py makemigrations` | gera a migration a partir dos models |
| `python manage.py migrate` | aplica as migrations no banco |
| `python manage.py createsuperuser` | cria usuário do admin |
| `python manage.py shell` | console Python com o Django carregado |
| `python manage.py popular_dados --limpar` | recria os dados de exemplo |
