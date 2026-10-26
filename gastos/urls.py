from django.urls import path
from . import views

app_name = 'gastos'

urlpatterns = [
    path('gastos/', views.gasto_lista, name='gasto_lista'),
    path('gastos/novo/', views.gasto_novo, name='gasto_novo'),
    path('gastos/<int:pk>/editar/', views.gasto_editar, name='gasto_editar'),
    path('gastos/<int:pk>/excluir/', views.gasto_excluir, name='gasto_excluir'),
]
