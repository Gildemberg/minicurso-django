# Minicurso de Django — Controle de Gastos

Este é o ponto de partida do minicurso. Durante a aula você vai construir, do
zero, um sistema de controle de gastos com Django.

## Os checkpoints (branches)

Cada bloco da aula tem uma branch com o código pronto **no fim** daquele bloco:

| Branch    | O que tem pronto                                   |
|-----------|----------------------------------------------------|
| `bloco-0` | só este README (ponto de partida)                    |
| `bloco-1` | `.gitignore`, projeto `config/`, app `gastos`, `.env` |
| `bloco-2` | models `Categoria` e `Gasto`, migrations e admin   |
| `bloco-3` | primeira página: lista de gastos com template e CSS |
| `bloco-4` | cadastrar, editar e excluir gastos e categorias    |
| `bloco-5` | dashboard com totais, barras e busca               |
| `bloco-6` | acabamento: campo `observacao` e admin da categoria |

## Primeira vez (Windows, no `cmd`)

```
python -m venv venv
venv\Scripts\activate
```

A partir da `bloco-1`, instale as dependências e crie o seu `.env`:

```
pip install -r requirements.txt
copy .env.example .env
```

## Me perdi! Como pular para um bloco

Pare o servidor (`Ctrl+C`) e rode, trocando `bloco-3` pelo bloco em que a
turma está:

```
git stash -u
git checkout bloco-3
del db.sqlite3
python manage.py migrate
```

- `git stash -u` guarda o seu código (inclusive arquivos novos) num canto,
  sem perder nada. O `.env` e o `venv` continuam no lugar.
- `del db.sqlite3` apaga o banco antigo, que pode não bater com os models do
  bloco novo. Depois do `migrate`, crie o admin de novo com
  `python manage.py createsuperuser`.

Quer recuperar o seu código depois da aula? Volte para a branch em que você
estava (por exemplo `git checkout bloco-0`) e rode:

```
git stash list
git stash pop
```

O `list` mostra o que foi guardado; o `pop` devolve o último que foi guardado.
