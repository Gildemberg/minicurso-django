from django.apps import AppConfig


class ContasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'

    # Este app nao tem models: ele so cuida do cadastro de conta. Toda a parte
    # de usuario e senha continua sendo do django.contrib.auth.
    name = 'apps.contas'
    label = 'contas'
    verbose_name = 'Contas de usuario'
