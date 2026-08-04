from django.apps import AppConfig


class GastosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # Caminho de importacao real do app (ele mora dentro da pasta apps/).
    name = 'apps.gastos'

    # Sem o label, o Django chamaria este app de "apps.gastos" e as tabelas
    # ficariam com nomes estranhos. Com ele, as tabelas sao gastos_gasto etc.
    label = 'gastos'
    verbose_name = 'Controle de gastos'
