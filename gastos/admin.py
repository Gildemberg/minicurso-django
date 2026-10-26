from django.contrib import admin
from .models import Categoria, Gasto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'cor']
    ordering = ['nome']
    list_per_page = 20


@admin.register(Gasto)
class GastoAdmin(admin.ModelAdmin):
    list_display = ['data', 'descricao', 'categoria', 'valor']
    list_filter = ['categoria', 'data']
    search_fields = ['descricao']
    date_hierarchy = 'data'
