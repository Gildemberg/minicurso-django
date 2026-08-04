# Roteiro do minicurso — 3h30

**Público:** alunos de Sistemas de Informação, do 1º ao 8º período.
**Meta:** cada aluno sai com um sistema de controle de gastos rodando na
própria máquina, feito do zero.

O grande risco de uma turma assim não é o conteúdo — é o **desnível**. O
roteiro abaixo é desenhado para isso: blocos curtos, um ponto de sincronia ao
fim de cada um, e desafios extras para quem terminar antes.

> ### ⚠️ Leia antes: o repositório vai além da aula
>
> O código deste repositório é a versão **final e multiusuário** — com login e
> com cada pessoa vendo só os próprios gastos.
>
> **O roteiro constrói a versão de uma noite**, sem login, porque multiusuário
> não cabe em 3h30 sem sacrificar o dashboard. Por isso alguns trechos de
> código aqui aparecem sem o campo `usuario` que você vê no repositório.
>
> A ponte entre as duas versões está no **[Apêndice A](#apêndice-a--multiusuário-e-login)**:
> ele mostra exatamente o que muda para sair da versão da aula e chegar na do
> repositório. Use como desafio do Bloco 6, material de casa ou segundo encontro.

---

## Antes da aula (faça isso com antecedência)

1. **Peça que instalem o Python antes.** Mande um e-mail/mensagem no grupo 3
   dias antes com o link do [python.org/downloads](https://www.python.org/downloads/)
   e o aviso: no Windows, marcar **"Add Python to PATH"** na primeira tela.
   Perder 40 minutos instalando Python destrói a aula.
2. **Suba este projeto no GitHub** e, se possível, marque um commit por
   checkpoint (`git tag bloco-1`, `bloco-2`...). Quem travar dá
   `git checkout bloco-3` e volta pra turma.
3. **Teste o Wi-Fi da sala.** São dois downloads: Django (~10 MB) e
   django-environ (pequeno). Se a rede for ruim, leve os `.whl` num pendrive:
   `pip download django django-environ -d pacotes/` e na sala
   `pip install --no-index --find-links=pacotes django django-environ`.
4. **Deixe o projeto pronto rodando numa aba** para o "demo do final" do minuto 0.

---

## Linha do tempo

| Horário | Bloco | Assunto |
|---|---|---|
| 0:00 – 0:12 | 0 | Abertura: o que vamos construir |
| 0:12 – 0:37 | 1 | Ambiente, estrutura do projeto e `.env` |
| 0:37 – 1:05 | 2 | Models, banco de dados e admin |
| 1:05 – 1:35 | 3 | Primeira página: URL → view → template |
| 1:35 – 1:50 | — | **INTERVALO** |
| 1:50 – 2:30 | 4 | CRUD de gastos com formulários |
| 2:30 – 3:00 | 5 | Dashboard: agregações e filtros |
| 3:00 – 3:20 | 6 | Acabamento e desafios |
| 3:20 – 3:30 | 7 | Fechamento e próximos passos |

> A estrutura profissional (`config/`, `apps/`, `.env`) custa uns **7 minutos a
> mais** no Bloco 1. Tirei do Bloco 0, que era generoso. Se o Bloco 1 estourar,
> o corte é o `.env`: entregue o `settings.py` pronto e explique em 1 minuto.

---

## Bloco 0 — Abertura (12 min)

**Não comece com teoria.** Abra o sistema pronto e use por 2 minutos: lance um
gasto, veja a barra do dashboard crescer, filtre por mês. A turma precisa saber
onde vai chegar.

Depois, o único diagrama da noite — desenhe no quadro:

```
navegador  →  urls.py  →  views.py  →  models.py  →  banco
                             ↓
navegador  ←   HTML    ←  template
```

Três frases para fixar:
- **URL** é o endereço. Diz *qual* código roda.
- **View** é a função. Ela recebe o pedido e decide o que responder.
- **Template** é o HTML com buracos que a view preenche.

> **Model, view, template.** Se você só ensinar isso hoje, a aula valeu.

Diga também o que **não** vamos ver: login, deploy, API, testes. Isso evita a
pergunta "e como faz login?" no minuto 20 e já anuncia o material extra.

---

## Bloco 1 — Ambiente e projeto no ar (25 min)

**Objetivo:** todo mundo vendo o foguete verde do Django, já na estrutura
profissional.

### 1.1 — Ambiente virtual (5 min)

```bash
mkdir controle-gastos && cd controle-gastos

python -m venv venv                 # cria o ambiente virtual
source venv/bin/activate            # Linux/macOS
venv\Scripts\activate               # Windows

pip install django django-environ
```

### 1.2 — O projeto se chama `config` (5 min)

```bash
django-admin startproject config .   # o ponto no final importa!
python manage.py runserver
```

Duas coisas para explicar aqui — **as duas geram pergunta**:

**O ponto final.** Sem ele o Django cria uma pasta a mais e o caminho de todo
mundo fica diferente do seu. Com o ponto, o `manage.py` fica na raiz.

**Por que `config` e não `controle_gastos`?** Porque aquela pasta não é o seu
sistema — ela é só a *configuração* dele. Chamar de `config` deixa isso óbvio
e é o padrão que você vai encontrar em projeto Django sério:

> Se o projeto se chama `controle_gastos` e o app também tem nome parecido,
> ninguém sabe qual arquivo abrir. `config/` é configuração, `apps/` é o sistema.

### 1.3 — Os apps moram em `apps/` (8 min)

```bash
mkdir apps
touch apps/__init__.py              # Linux/macOS
type nul > apps\__init__.py         # Windows

mkdir apps/gastos
python manage.py startapp gastos apps/gastos
```

> **O `__init__.py` é obrigatório.** É ele que faz o Python enxergar `apps/`
> como um pacote. Sem esse arquivo vazio, nada importa e o erro é confuso.
> Bom momento para explicar o que é um pacote em Python.

**Projeto x app** — a confusão nº 1 de quem começa:
> O **projeto** é o site inteiro (configuração, banco, rotas gerais).
> O **app** é uma funcionalidade dele. Um projeto tem vários apps — hoje temos
> um só, mas a pasta `apps/` já está pronta para o segundo.

Agora **a pegadinha desta estrutura**. O `startapp` não sabe que o app foi
parar dentro de `apps/`, então ele escreve o caminho errado. Corrija
`apps/gastos/apps.py`:

```python
class GastosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.gastos'    # caminho real de importação
    label = 'gastos'        # nome curto: mantém as tabelas como gastos_gasto
```

> **Se esquecer o `label`**, as tabelas nascem com nomes esquisitos e as
> migrations ficam presas ao caminho da pasta. É uma linha que evita dor
> depois — e explica o que é "app label" no Django.

E registre em `config/settings.py`:

```python
INSTALLED_APPS = [
    ...
    'apps.gastos',
]
```

> No projeto de referência o `INSTALLED_APPS` está separado em três listas
> (`DJANGO_APPS`, `THIRD_PARTY_APPS`, `LOCAL_APPS`) e somado no final. É outro
> padrão comum — em projeto grande você bate o olho e sabe o que é seu e o que
> é de terceiro. **Na aula, ensine a lista simples**; mostre a separada só se
> alguém perguntar, ou no Bloco 6.

### 1.4 — Configuração e o `.env` (7 min)

Ainda em `config/settings.py`, deixe o português pronto:

```python
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'
USE_THOUSAND_SEPARATOR = True   # 1.234,56
```

E tire os segredos do código. Abra o `settings.py` gerado e **mostre a
`SECRET_KEY` ali, em texto puro**:

> Esse arquivo vai para o GitHub. Essa chave assina as sessões de todos os
> usuários. Quem tem a chave consegue se passar por qualquer um. Existem robôs
> varrendo o GitHub atrás exatamente disso.

A correção:

```python
import environ

env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
```

Crie o `.env` (que **não** vai para o Git) e o `.env.example` (que vai, sem os
valores, para o próximo dev saber o que preencher):

```bash
# .env
SECRET_KEY=cole-uma-chave-aqui
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost
```

Gere a chave na frente deles:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

E o `.gitignore` com `venv/`, `db.sqlite3`, `__pycache__/` e `.env`.

> Esse bloco de 7 minutos é o que separa "código de aula" de "código de
> trabalho". Vale o tempo, e é conteúdo de Segurança da Informação que eles
> reconhecem.

### ⏱ Ponto de sincronia
"Quem está vendo o foguete, levanta a mão." Não avance com menos de 90% das
mãos levantadas.

**Erros comuns aqui:**
| Sintoma | Causa |
|---|---|
| `python: command not found` | usar `python3` no macOS/Linux |
| `(venv)` não aparece no terminal | esqueceu de ativar o venv |
| Windows barra a ativação | `Set-ExecutionPolicy -Scope Process RemoteSigned` |
| `That port is already in use` | `python manage.py runserver 8001` |
| `Set the SECRET_KEY environment variable` | falta o `.env`, ou está fora da raiz |
| `ModuleNotFoundError: No module named 'apps'` | falta o `apps/__init__.py` |
| `No module named 'gastos'` | faltou trocar `name` para `apps.gastos` |

---

## Bloco 2 — Models, banco e admin (30 min)

**Objetivo:** as duas tabelas existindo, e um painel para cadastrar dados.

Esta é a hora em que o Django "vende o peixe". Guarde energia para ela.

### 2.1 — Os models (10 min)

`apps/gastos/models.py`:

```python
from django.db import models
from django.utils import timezone


class Categoria(models.Model):
    nome = models.CharField(max_length=50, unique=True)
    cor = models.CharField(max_length=7, default='#2a78d6')

    def __str__(self):
        return self.nome


class Gasto(models.Model):
    descricao = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    data = models.DateField(default=timezone.localdate)
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='gastos',
    )

    class Meta:
        ordering = ['-data', '-id']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'
```

Comece simples assim. Os campos `observacao`, `criado_em`, `choices` de cor e
`validators` entram no Bloco 6, se der tempo.

**Três decisões para explicar em voz alta** (é o conteúdo mais denso da noite):

1. **`DecimalField`, nunca `FloatField` para dinheiro.** Mostre no terminal:
   `python -c "print(0.1 + 0.2)"` → `0.30000000000000004`. Ninguém quer isso no
   extrato. Essa demonstração de 10 segundos vale por um semestre.
2. **`ForeignKey` é o "pertence a".** Um gasto pertence a uma categoria; uma
   categoria tem muitos gastos. É o 1-para-N que eles viram (ou vão ver) em
   Banco de Dados, agora em Python.
3. **`on_delete=PROTECT`.** O que acontece com os gastos se a categoria for
   apagada? `CASCADE` apaga junto, `PROTECT` proíbe. Escolhemos proibir. Faça
   a pergunta para a turma antes de responder.

O `__str__` também merece 30 segundos: é o que aparece no admin e nos `<select>`.

### 2.2 — Migrations (5 min)

```bash
python manage.py makemigrations   # escreve a receita
python manage.py migrate          # executa a receita no banco
```

Abra `apps/gastos/migrations/0001_initial.py` e mostre: **é Python, não SQL.**
E o SQL que sai dali:

```bash
python manage.py sqlmigrate gastos 0001
```

> Migration é o `git` do banco de dados: cada mudança no `models.py` vira um
> arquivo versionado que qualquer pessoa do time consegue aplicar.

### 2.3 — O admin (15 min)

O momento "uau" da aula. A técnica aqui é **revelar em camadas**: cada bloco
de código é 30 segundos de digitação e uma mudança visível no `/admin/`. Não
mostre o `admin.py` pronto — o efeito morre.

**Camada 1 — existir (3 min).** `apps/gastos/admin.py`:

```python
from django.contrib import admin
from .models import Categoria, Gasto

admin.site.register(Categoria)
admin.site.register(Gasto)
```

```bash
python manage.py createsuperuser
```

> Aviso: a senha **não aparece** enquanto digita. É normal, não travou.

Acesse `/admin/` — painel completo, com login, permissões, busca e CRUD, em 3
linhas. Pergunte: *"quanto tempo isso levaria na mão?"*

**Camada 2 — deixar de ser feio (2 min).** A listagem mostra
`Gasto object (1)`. Ninguém entende nada. Volte no `models.py`:

```python
def __str__(self):
    return f'{self.descricao} - R$ {self.valor}'
```

Recarregue. **Uma função mudou a tela inteira** — é a melhor demonstração de
`__str__` que existe.

**Camada 3 — virar ferramenta de trabalho (3 min).**

```python
@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['data', 'descricao', 'categoria', 'valor']
    list_filter = ['categoria', 'data']
    search_fields = ['descricao']
    date_hierarchy = 'data'
```

Recarregue a cada linha adicionada. `date_hierarchy` é a que mais impressiona:
uma navegação por ano → mês → dia aparece no topo, de graça.

**Camada 4 — ter dono (1 min).** Em `config/urls.py`:

```python
admin.site.site_header = 'Controle de Gastos'
admin.site.index_title = 'Administracao do sistema'
```

Some o "Django administration". Custa nada e é a hora em que a turma percebe
que dá para entregar isso **para um cliente**.

**Camada 5 — brincar (5 min).** Peça que cada um cadastre 4 categorias e uns
10 gastos. Eles vão precisar desses dados nos próximos blocos, e o dashboard
fica bem mais divertido com dados de verdade.

> Guarde o resto do admin (cores, filtro por faixa, exportar CSV, inline) para
> o Bloco 6 — está tudo no **cardápio** no fim deste roteiro. É o melhor
> material de desafio da noite: efeito visual grande, código pequeno.

### ⏱ Ponto de sincronia
Todos com dados cadastrados no admin.

**Se estiver atrasado:** pule as camadas 3 e 4 e o `sqlmigrate`. As camadas
1 e 2 são o essencial.

---

## Bloco 3 — URL → view → template (30 min)

**Objetivo:** a primeira página *nossa*, listando os gastos do banco.

### 3.1 — A view mais simples possível (5 min)

`apps/gastos/views.py`:

```python
from django.http import HttpResponse

def gasto_lista(request):
    return HttpResponse('<h1>Meus gastos</h1>')
```

`apps/gastos/urls.py` (**arquivo novo** — o Django não cria):

```python
from django.urls import path
from . import views

app_name = 'gastos'

urlpatterns = [
    path('gastos/', views.gasto_lista, name='gasto_lista'),
]
```

`config/urls.py`:

```python
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gastos.urls')),
]
```

Acesse `/gastos/`. Funcionou? Ótimo — **esse é o ciclo inteiro**. Todo o resto
é enfeite.

### 3.2 — Trocando o HttpResponse por um template (15 min)

Diga: "ninguém escreve HTML dentro de `HttpResponse`". Crie
`templates/gastos/gasto_lista.html` e registre a pasta em `settings.py`:

```python
TEMPLATES = [{
    ...
    'DIRS': [BASE_DIR / 'templates'],
}]
```

```python
from django.shortcuts import render
from .models import Gasto

def gasto_lista(request):
    gastos = Gasto.objects.select_related('categoria')
    return render(request, 'gastos/gasto_lista.html', {'gastos': gastos})
```

```html
<h1>Meus gastos</h1>
<table>
  {% for gasto in gastos %}
    <tr>
      <td>{{ gasto.data|date:"d/m/Y" }}</td>
      <td>{{ gasto.descricao }}</td>
      <td>{{ gasto.categoria.nome }}</td>
      <td>R$ {{ gasto.valor|floatformat:2 }}</td>
    </tr>
  {% empty %}
    <tr><td>Nenhum gasto ainda.</td></tr>
  {% endfor %}
</table>
```

A sintaxe do template em uma frase:
- `{{ ... }}` **mostra** um valor.
- `{% ... %}` **faz** alguma coisa (`for`, `if`, `url`, `extends`).
- `|` aplica um **filtro** que formata o valor.
- `{# ... #}` é comentário — **de uma linha só**.

> **Pegadinha que falha em silêncio:** `{# #}` só funciona numa linha. Se o
> comentário passar para a linha de baixo, o Django deixa de tratar como
> comentário e **imprime o texto na página** — sem erro, sem aviso. Para várias
> linhas, use `{% comment %} ... {% endcomment %}`. Vale mostrar o erro ao vivo:
> é rápido de reproduzir e ninguém mais esquece.

`{% empty %}` é um presente: estado vazio de graça.

### 3.3 — base.html e arquivos estáticos (10 min)

Crie `templates/base.html` com o `{% block conteudo %}` e o menu, e faça a
página herdar com `{% extends 'base.html' %}`. Explique herança de template
como "não repetir o cabeçalho em 6 arquivos".

Registre a pasta de estáticos em `settings.py`:

```python
STATICFILES_DIRS = [BASE_DIR / 'static']
```

E carregue o CSS no `base.html`:

```html
{% load static %}
<link rel="stylesheet" href="{% static 'css/estilo.css' %}">
```

> **Não escreva o CSS na frente deles.** Mande o `static/css/estilo.css` pronto
> pelo grupo/repositório e peça que copiem. São 20 minutos de digitação que não
> ensinam Django nenhum — e o efeito visual instantâneo levanta a turma.

### ⏱ Ponto de sincronia
Todos vendo a lista de gastos estilizada.

---

## ☕ INTERVALO (15 min)

Anuncie a hora exata de voltar e escreva no quadro. Aproveite para socorrer
individualmente quem ficou para trás — este é o melhor momento da noite para
isso.

---

## Bloco 4 — CRUD com formulários (40 min)

**Objetivo:** cadastrar, editar e excluir gastos sem passar pelo admin.

### 4.1 — ModelForm (10 min)

`apps/gastos/forms.py` (**arquivo novo**):

```python
from django import forms
from .models import Gasto


class GastoForm(forms.ModelForm):
    class Meta:
        model = Gasto
        fields = ['descricao', 'valor', 'data', 'categoria']
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }
```

> O `ModelForm` lê o `models.py` e gera o formulário: os campos, os tipos, as
> validações e as mensagens de erro. Você descreveu os dados **uma vez**.

### 4.2 — A view de cadastro (15 min)

Este é o padrão mais importante do bloco. Escreva devagar:

```python
def gasto_novo(request):
    if request.method == 'POST':
        form = GastoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gastos:gasto_lista')
    else:
        form = GastoForm()

    return render(request, 'gastos/gasto_form.html', {'form': form})
```

**Leia o fluxo em voz alta**, é o que fixa:
> "Se veio POST, o usuário mandou dados: valido e salvo. Se veio GET, ele só
> abriu a página: mostro o formulário em branco. Se o formulário for inválido,
> caio no `render` do fim — com os erros e os dados que ele já digitou."

O template:

```html
<form method="post" novalidate>
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Salvar</button>
</form>
```

**`{% csrf_token %}`** merece 2 minutos de verdade — é segurança, é conteúdo de
SI, e é a causa do erro 403 que alguém *vai* ter. Explique curto: sem o token,
um site malicioso poderia enviar esse formulário em nome do usuário logado.

Comece com `{{ form.as_p }}`. Só depois troque pelo loop campo a campo
(`templates/gastos/_form_campos.html` neste projeto) para conseguir estilizar.

### 4.3 — Editar e excluir (15 min)

Editar é a **mesma view** com uma palavra a mais — `instance`:

```python
def gasto_editar(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        form = GastoForm(request.POST, instance=gasto)   # <-- a diferença
        if form.is_valid():
            form.save()
            return redirect('gastos:gasto_lista')
    else:
        form = GastoForm(instance=gasto)
    return render(request, 'gastos/gasto_form.html', {'form': form})
```

Peça para a turma comparar as duas views lado a lado e apontar a diferença.
Deixa a ficha cair sozinha.

Excluir, com página de confirmação:

```python
def gasto_excluir(request, pk):
    gasto = get_object_or_404(Gasto, pk=pk)
    if request.method == 'POST':
        gasto.delete()
        return redirect('gastos:gasto_lista')
    return render(request, 'gastos/confirmar_exclusao.html', {'objeto': gasto})
```

> **Por que POST e não um link?** Porque GET nunca deve alterar dados. Se
> excluir fosse um link, o robô do Google (ou o pré-carregamento do navegador)
> apagaria o banco inteiro sozinho. É uma história que ninguém esquece.

Não esqueça as URLs:

```python
path('gastos/novo/', views.gasto_novo, name='gasto_novo'),
path('gastos/<int:pk>/editar/', views.gasto_editar, name='gasto_editar'),
path('gastos/<int:pk>/excluir/', views.gasto_excluir, name='gasto_excluir'),
```

`<int:pk>` é a parte variável da URL — vira o parâmetro `pk` da view.

**Se sobrar fôlego** (2 min): `messages.success(request, 'Gasto salvo.')` e o
loop de mensagens no `base.html`. É barato e dá cara de sistema pronto.

### ⏱ Ponto de sincronia
Todos cadastrando gastos pelo próprio formulário.

**Se estiver atrasado:** faça só `gasto_novo`, e deixe editar/excluir como
exercício guiado — eles têm o código no repositório.

---

## Bloco 5 — Dashboard: agregações e filtros (30 min)

**Objetivo:** transformar a lista em informação. É o bloco que impressiona.

### 5.1 — Agregação (15 min)

```python
from django.db.models import Count, Sum

def dashboard(request):
    hoje = timezone.localdate()
    gastos_do_mes = Gasto.objects.filter(data__year=hoje.year, data__month=hoje.month)

    total = gastos_do_mes.aggregate(total=Sum('valor'))['total'] or 0

    agrupado = (
        gastos_do_mes
        .values('categoria__nome', 'categoria__cor')
        .annotate(total=Sum('valor'))
        .order_by('-total')
    )
    ...
```

**Vale mostrar o SQL gerado** — para quem já cursou Banco de Dados é a hora em
que o ORM faz sentido:

```python
print(agrupado.query)
```

Traduza: `.values()` é o `GROUP BY`, `.annotate()` é o `SUM(...)`,
`.order_by()` é o `ORDER BY`. O `__` atravessa a ForeignKey
(`categoria__nome` = "o nome da categoria do gasto").

> **`aggregate` x `annotate`:** `aggregate` devolve **um** número da consulta
> inteira. `annotate` devolve um número **por linha/grupo**.

### 5.2 — As barras (10 min)

A view calcula o percentual, o template só desenha a largura:

```python
'percentual': round(item['total'] / total * 100, 1) if total else 0,
```

```html
<div class="barra-trilho">
  <div class="barra-preenchimento"
       style="width: {{ item.percentual }}%; background: {{ item.cor }}"></div>
</div>
```

**Um gráfico sem biblioteca nenhuma.** Só uma `div` com `width` em
porcentagem. Isso costuma surpreender mais que qualquer Chart.js.

> Regra de bolso para levar da aula: **cálculo é na view, template só exibe.**
> Se você está fazendo conta no HTML, algo está no lugar errado.

### 5.3 — Filtros pela URL (5 min)

```python
busca = request.GET.get('busca', '').strip()
if busca:
    gastos = gastos.filter(descricao__icontains=busca)
```

Dois conceitos de graça:
- **QuerySets são preguiçosos.** Você pode encadear vários `.filter()`; o banco
  só é consultado quando o template percorre o resultado. Uma consulta só.
- **`method="get"`** coloca o filtro na URL — dá para copiar e mandar o link
  para alguém. É por isso que busca usa GET e cadastro usa POST.

### ⏱ Ponto de sincronia
Todos com o dashboard mostrando as barras coloridas.

---

## Bloco 6 — Acabamento e desafios (20 min)

Aqui a turma trabalha e você circula pela sala. Coloque a lista no telão e
deixe cada um escolher pelo próprio nível:

**Nível 1 — todo mundo consegue**
- Adicionar o campo `observacao` (`TextField(blank=True)`) — e rodar as duas
  migrations de novo, agora sozinhos. Repetir o ciclo `models → migrate` sem
  ajuda é o que fixa.
- Trocar as cores das categorias e ver o dashboard mudar.
- Mudar o texto do estado vazio.
- **Admin:** `list_per_page`, `ordering`, `list_display` na `Categoria`.

**Nível 2 — quem está confortável**
- Filtro por mês no dashboard com `<input type="month">`.
- Coluna "quantos lançamentos" na tela de categorias (`Count('gastos')`).
- Mostrar o total no rodapé da tabela de gastos.
- Bloquear valor negativo com `MinValueValidator(0.01)`.
- **Admin:** coluna colorida com `format_html`, `fieldsets`, `readonly_fields`,
  `autocomplete_fields`, `inlines`.

**Nível 3 — para os períodos mais avançados**
- Login: `LoginRequiredMixin`/`@login_required` e um campo `usuario` no `Gasto`,
  para cada um ver só os próprios gastos.
- Paginação com `Paginator` (20 por página).
- Comparar o mês atual com o anterior e mostrar a variação em %.
- Reescrever as views como Class-Based Views (`ListView`, `CreateView`) e
  discutir o trade-off: menos código, mais mágica.
- **Admin:** `SimpleListFilter` por faixa de valor, action de exportar CSV,
  coluna calculada e ordenável com `annotate`, total no topo da listagem.
- **Multiusuário completo** — login + cada um vê só os próprios gastos. É o
  maior salto de todos: transforma o exercício num sistema de verdade. Passo a
  passo no [Apêndice A](#apêndice-a--multiusuário-e-login).

> Ter os três níveis prontos no slide resolve o problema do desnível melhor do
> que qualquer explicação: o veterano não fica entediado e o calouro não fica
> perdido.

> **O admin é o melhor desafio da noite.** É a única parte do sistema em que
> 3 linhas de código produzem uma mudança visual grande e imediata — quem está
> desanimado no fim de 3 horas volta a se animar. O cardápio completo, com
> tempo e código de cada item, está no fim deste roteiro.

---

## Bloco 7 — Fechamento (10 min)

1. **Recapitule o diagrama do início.** Agora eles reconhecem cada caixa —
   e é uma sensação boa de encerrar a noite.
2. **Mostre o que existe além:** deploy (PythonAnywhere ou Railway têm plano
   grátis e aceitam Django em minutos), Django REST Framework, testes,
   PostgreSQL no lugar do SQLite.
3. **Entregue os links:**
   - Este repositório (código completo + este roteiro)
   - [Tutorial oficial do Django](https://docs.djangoproject.com/pt-br/5.2/intro/tutorial01/) — em português
   - [Django Girls](https://tutorial.djangogirls.org/pt/) — o melhor material para iniciantes em PT-BR
4. **Dê a próxima tarefa concreta:** "adicione o campo de forma de pagamento
   sozinho até o fim de semana". Quem faz um exercício depois da aula é quem
   realmente continua.

---

# Apêndice A — Multiusuário e login

É o que separa "exercício de aula" de "sistema que dá para mostrar numa
entrevista". **Não cabe nas 3h30** — são uns 40 minutos honestos e mexe em
todas as views. Use como desafio de Nível 3, tarefa de casa ou segundo
encontro. O repositório já está nesta versão; abaixo é o que muda.

## A boa notícia: a autenticação já está pronta

Não existe nada para "ligar". O backend padrão é este, e é o **mesmo que o
`/admin/` usa**:

```python
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']
```

Mesma tabela `auth_user`, mesmo hash de senha, mesma sessão. A única diferença
entre a tela do admin e a sua é uma validação a mais:

| | Formulário | Checagem extra |
|---|---|---|
| `/admin/login/` | `AdminAuthenticationForm` | exige `is_staff=True` |
| `/contas/login/` | `AuthenticationForm` | só exige `is_active=True` |

Bom para mostrar em aula: entre com um usuário comum no `/admin/` e leia a
resposta do Django — *"insira um usuário e senha corretos para uma conta de
equipe"*. É a separação de papéis acontecendo na frente deles.

## Os 6 passos

**1. URLs e settings** — login, logout e reset de senha prontos:

```python
# config/urls.py
path('contas/', include('django.contrib.auth.urls')),
```

```python
# config/settings.py
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'gastos:dashboard'
LOGOUT_REDIRECT_URL = 'login'
```

**2. O template** vai em `templates/registration/login.html` — pasta
`registration`, **não** `contas`. O nome da pasta não acompanha o prefixo da
URL. É o tropeço nº 1.

**3. O dono nos models:**

```python
usuario = models.ForeignKey(
    settings.AUTH_USER_MODEL,   # e nao `User` importado direto
    on_delete=models.CASCADE,
    related_name='gastos',
)
```

> Use `settings.AUTH_USER_MODEL`, nunca `from django.contrib.auth.models import User`
> na FK. É a recomendação oficial: mantém o projeto capaz de trocar o model de
> usuário depois. Custa a mesma linha.

Vale também tornar a categoria por usuário — senão a "Alimentação" é
compartilhada e um aluno renomeia a do outro. Isso muda o `unique`:

```python
constraints = [
    models.UniqueConstraint(fields=['usuario', 'nome'],
                            name='categoria_nome_unico_por_usuario'),
]
```

**4. `@login_required` em todas as views.**

**5. Filtrar tudo por `request.user`** — ver a seção de segurança abaixo.

**6. Definir o dono ao criar:**

```python
gasto = form.save(commit=False)   # monta sem gravar
gasto.usuario = request.user      # o dono vem do request, nunca do form
gasto.save()
```

## As 4 camadas de segurança — e todas são necessárias

| Camada | Onde | Impede |
|---|---|---|
| `@login_required` | todas as views | acesso anônimo |
| `.filter(usuario=request.user)` | listagens e dashboard | ver dados alheios na lista |
| `get_object_or_404(..., usuario=request.user)` | editar / excluir | trocar o id na URL |
| `queryset` do campo no form | `GastoForm.__init__` | POST com id de categoria alheia |

**A quarta é a que todo mundo esquece**, e é a melhor aula de segurança da
noite:

```python
self.fields['categoria'].queryset = Categoria.objects.filter(usuario=usuario)
```

Filtrar só o `<select>` na tela não protege nada — quem manda o POST na mão
passa direto. Limitar o `queryset` do campo faz o **Django rejeitar** o valor
na validação, com a mensagem *"Faça uma escolha válida"*.

> **Demonstre isso.** Abra o DevTools, troque o `value` de uma `<option>` para
> o id de uma categoria de outro usuário e envie. Sem a camada 4, o gasto é
> criado no nome errado. Com ela, o formulário recusa. É o momento em que a
> turma entende que **validação no cliente não é validação**.

Repare também que a camada 3 devolve **404, não 403**. É de propósito: para
quem não é dono, o registro simplesmente não existe. Um 403 confirmaria que
aquele id existe — vaza informação.

## A pegadinha da migration

Adicionar uma FK obrigatória numa tabela **que já tem dados** trava: o Django
pergunta no terminal qual valor usar para as linhas existentes, e não há
resposta boa.

Em aula, com banco de brincadeira, o caminho rápido é honesto: apagar o
`db.sqlite3` e o `0001_initial.py`, e gerar tudo de novo. Foi o que este
repositório faz.

Em produção, com dados reais, não dá — e a receita profissional são **três
migrations**:

1. `AddField` com `null=True` — passa sem reclamar
2. `RunPython` — uma migration de dados que preenche o dono de cada linha
3. `AlterField` para `null=False` — agora que ninguém está vazio

Vale mostrar isso mesmo sem executar. É o tipo de coisa que separa quem já
mexeu em banco em produção de quem não mexeu.

## O logout mudou no Django 5

```html
<a href="{% url 'logout' %}">Sair</a>   <!-- 405 Method Not Allowed -->
```

A documentação é direta: *"Logs a user out on POST requests."* Tem que ser
formulário:

```html
<form method="post" action="{% url 'logout' %}">
  {% csrf_token %}
  <button type="submit">Sair</button>
</form>
```

**Avise antes.** Suporte a GET saiu no Django 5.0, mas a internet inteira ainda
ensina do jeito antigo — o aluno vai pesquisar, copiar o link, tomar 405 e não
entender por quê.

## Como demonstrar em aula (2 minutos)

O comando `popular_dados` cria dois usuários, `ana` e `bruno`, cada um com as
suas categorias e gastos (senha `senha-de-teste-123`).

1. Entre como `ana` → total do mês, digamos, R$ 204,74
2. Saia, entre como `bruno` → outro total, outras categorias
3. Copie a URL de editar um gasto da `ana`, cole logado como `bruno` → **404**
4. Entre no `/admin/` com o superusuário → **ele vê os dois**

O passo 4 é o que fecha o raciocínio da noite: *o admin é a ferramenta do
operador, o site é a do usuário — e os dois usam a mesma autenticação.*

---

# Apêndice B — Cardápio do Django Admin

Tudo aqui está **implementado e funcionando** em `apps/gastos/admin.py`. Use
como banco de desafios do Bloco 6, como plano B se sobrar tempo, ou como
material de um segundo encontro.

A coluna **efeito** é o que importa para escolher: com a turma cansada, prefira
sempre o item de efeito alto e código curto.

| # | Recurso | O que faz | Linhas | Efeito |
|---|---|---|---|---|
| 1 | `site_header` / `index_title` | tira o "Django administration" | 2 | ⭐⭐⭐ |
| 2 | `list_display` | escolhe as colunas da listagem | 1 | ⭐⭐⭐ |
| 3 | `date_hierarchy` | navegação ano → mês → dia no topo | 1 | ⭐⭐⭐ |
| 4 | `list_filter` | barra de filtros na lateral | 1 | ⭐⭐⭐ |
| 5 | `search_fields` | caixa de busca | 1 | ⭐⭐ |
| 6 | `list_editable` | editar valor na própria listagem | 2 | ⭐⭐⭐ |
| 7 | `format_html` | bolinha colorida da categoria | 6 | ⭐⭐⭐ |
| 8 | `fieldsets` + `collapse` | agrupa campos em seções dobráveis | 8 | ⭐⭐ |
| 9 | `readonly_fields` | campo que aparece mas não se edita | 1 | ⭐ |
| 10 | `autocomplete_fields` | `<select>` com busca | 1 | ⭐⭐ |
| 11 | `TabularInline` | gastos dentro da tela da categoria | 7 | ⭐⭐⭐ |
| 12 | `@admin.display` + `annotate` | coluna calculada e **ordenável** | 8 | ⭐⭐ |
| 13 | `SimpleListFilter` | filtro por regra (faixa de valor) | 18 | ⭐⭐ |
| 14 | `actions` | exportar CSV / duplicar em lote | 15 | ⭐⭐⭐ |
| 15 | `changelist_view` | total do que está filtrado, no topo | 10 | ⭐⭐⭐ |
| 16 | `list_select_related` | corrige N+1 — invisível, mas é o certo | 1 | — |

## Os quatro que valem mais a pena

### 1. Coluna colorida (`format_html`)

```python
@admin.display(description='categoria', ordering='categoria__nome')
def categoria_colorida(self, obj):
    return format_html(
        '<span style="display:inline-block;width:10px;height:10px;'
        'border-radius:3px;background:{};margin-right:6px"></span>{}',
        obj.categoria.cor, obj.categoria.nome,
    )
```

> **Ensine `format_html`, não f-string.** Ele escapa os valores antes de montar
> o HTML. Se você concatenar string com dado do usuário, criou um XSS. Essa é
> uma aula de segurança de 1 minuto que cabe em qualquer período.

O `ordering=` no decorator é o detalhe que quase ninguém conhece: sem ele a
coluna não é clicável; com ele, o Django ordena pelo campo indicado.

### 2. Filtro por regra (`SimpleListFilter`)

`list_filter` só filtra por campo existente. Quando o filtro é uma **regra**,
escreve-se assim:

```python
class FaixaDeValorFilter(admin.SimpleListFilter):
    title = 'faixa de valor'
    parameter_name = 'faixa'        # vira ?faixa=... na URL

    def lookups(self, request, model_admin):
        return [('baixo', 'Ate R$ 50'), ('alto', 'Acima de R$ 200')]

    def queryset(self, request, queryset):
        if self.value() == 'baixo':
            return queryset.filter(valor__lte=50)
        if self.value() == 'alto':
            return queryset.filter(valor__gt=200)
        return queryset

# e depois:  list_filter = ['categoria', FaixaDeValorFilter, 'data']
```

Duas funções: `lookups` são as opções na tela, `queryset` é o que cada uma faz.

### 3. Ação em lote (`actions`)

Aparece no combo acima da listagem e recebe os itens marcados:

```python
@admin.action(description='Exportar selecionados para CSV')
def exportar_csv(modeladmin, request, queryset):
    resposta = HttpResponse(content_type='text/csv')
    resposta['Content-Disposition'] = 'attachment; filename="gastos.csv"'
    resposta.write('﻿')                        # BOM: Excel em PT-BR
    escritor = csv.writer(resposta, delimiter=';')  # PT-BR usa ; e não ,
    escritor.writerow(['Data', 'Descricao', 'Categoria', 'Valor'])
    for gasto in queryset.select_related('categoria'):
        escritor.writerow([gasto.data.strftime('%d/%m/%Y'), gasto.descricao,
                           gasto.categoria.nome, str(gasto.valor).replace('.', ',')])
    return resposta
```

> O BOM e o `;` são o detalhe que faz o arquivo abrir **certo** no Excel
> brasileiro. Sem isso o acento vira lixo e tudo cai numa coluna só. É o tipo
> de coisa que só se aprende apanhando — dê de presente.

Uma action que devolve `HttpResponse` vira download. Se devolver `None`, o
admin volta para a listagem.

### 4. Total no topo da listagem (`changelist_view`)

O mais impressionante do cardápio, e o mais útil num sistema de gastos: filtre
por categoria e o **total do que está na tela** muda junto.

```python
def changelist_view(self, request, extra_context=None):
    resposta = super().changelist_view(request, extra_context)
    try:
        gastos_na_tela = resposta.context_data['cl'].queryset
    except (AttributeError, KeyError):
        return resposta          # não é a listagem (ex.: um redirect)
    total = gastos_na_tela.aggregate(total=Sum('valor'))['total']
    resposta.context_data['title'] = f'Gastos — total filtrado: {moeda(total)}'
    return resposta
```

O truque: chame `super()` **primeiro** e só então pegue o queryset já filtrado,
que o Django deixa em `context_data['cl']`. Escrever no `title` evita ter que
sobrescrever template — por isso cabe em 10 linhas.

## Duas armadilhas que você vai encontrar

**`UnorderedObjectListWarning`.** Se você usar `annotate()` no `get_queryset`
do admin, o Django cria um `GROUP BY` e deixa de enxergar o `ordering` do
`Meta` — aí solta esse aviso no terminal. A correção é declarar `ordering`
explicitamente no `ModelAdmin`. Warning no console vira pergunta em sala;
melhor já estar corrigido.

**`autocomplete_fields` exige `search_fields` no admin do outro model.** Se
`GastoAdmin` tem `autocomplete_fields = ['categoria']`, então `CategoriaAdmin`
precisa de `search_fields`. Sem isso o projeto nem sobe:

```
(admin.E040) CategoriaAdmin must define "search_fields",
because it's referenced by GastoAdmin.autocomplete_fields.
```

**Provoque esse erro de propósito na aula.** Ele diz qual classe, qual atributo
e por quê — é o melhor exemplo possível de "leia a mensagem, ela tem a
resposta". A turma passa a noite inteira com medo do texto vermelho; mostrar
um erro que resolve o próprio problema muda essa relação.

## Onde isso encaixa no curso

- **Bloco 2.3 (na aula):** itens 1 a 5 — as camadas do reveal.
- **Bloco 6 (desafio):** itens 6 a 11, que são configuração pura.
- **Segundo encontro / estudo em casa:** 12 a 16, que envolvem escrever lógica.

> Se você tiver **um segundo encontro**, "Django Admin avançado" é um tema de
> 2 horas que se sustenta sozinho — e é o que mais aparece em trabalho real:
> muita empresa entrega o admin customizado como o sistema interno inteiro.

---

## Colas rápidas

**Se estiver 20 minutos atrasado no intervalo,** corte nesta ordem:
1. O `.env` (Bloco 1.4) — entregue o `settings.py` pronto, explique em 1 minuto
2. Editar e excluir (Bloco 4.3) — só mostre pronto no repositório
3. Os filtros (Bloco 5.3)
4. O Bloco 6 vira "leve para casa"

**Nunca corte:** o admin (2.3) e o dashboard (5.1/5.2). São os dois momentos em
que a turma se anima.

**Erros que vão aparecer — tenha a resposta na ponta da língua:**

| Erro | Resposta |
|---|---|
| `TemplateDoesNotExist` | app fora de `INSTALLED_APPS`, ou caminho/pasta errada |
| `NoReverseMatch` | nome da URL errado no `{% url %}`, ou faltou o `gastos:` |
| `no such table: gastos_gasto` | esqueceu de rodar `migrate` |
| `403 CSRF verification failed` | faltou `{% csrf_token %}` no `<form>` |
| Página em branco / CSS sumiu | `STATICFILES_DIRS` ou `{% load static %}` |
| Texto estranho aparecendo na página | comentário `{# #}` quebrado em duas linhas |
| Mudou o model e nada aconteceu | faltou `makemigrations` + `migrate` |
| `ModuleNotFoundError: django` | venv não está ativo |
| `valor: Informe um número` | digitou `42,50` — veja a nota da vírgula abaixo |

**A nota da vírgula.** O `DecimalField` do Django só aceita ponto: quem digita
`42,50` leva erro. Normalmente o `<input type="number">` resolve sozinho (o
navegador converte conforme o idioma do sistema), mas numa sala com 30 máquinas
de configurações diferentes **isso vai pegar alguém**. Neste projeto já existe
a solução em `apps/gastos/forms.py` — a classe `CampoValor`, 4 linhas que trocam a
vírgula por ponto antes de validar. Ensine o formulário simples primeiro e
mostre o `CampoValor` no Bloco 6: é um ótimo exemplo de "dá para customizar
qualquer pedaço do Django".

**Frases que funcionam:**
- "Erro vermelho no terminal não é fracasso, é o Django conversando com você.
  Leia a **última** linha primeiro."
- "Se está repetindo, tem um jeito melhor. O Django inteiro é isso."
- "Anota a dúvida e me chama no intervalo" — protege o ritmo da turma.
