from django.contrib import admin
from .models import Categoria, Gasto

admin.site.register(Categoria)


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['data', 'descricao', 'categoria', 'valor']
    list_filter = ['categoria', 'data']
    search_fields = ['descricao']
    date_hierarchy = 'data'
