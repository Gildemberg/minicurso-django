from django.urls import path
from . import views

app_name = 'gastos'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('gastos/', views.gasto_lista, name='gasto_lista'),
    path('gastos/novo/', views.gasto_novo, name='gasto_novo'),
    path('gastos/<int:pk>/editar/', views.gasto_editar, name='gasto_editar'),
    path('gastos/<int:pk>/excluir/', views.gasto_excluir, name='gasto_excluir'),

    path('categorias/', views.categoria_lista, name='categoria_lista'),
    path('categorias/nova/', views.categoria_nova, name='categoria_nova'),
    path('categorias/<int:pk>/editar/', views.categoria_editar, name='categoria_editar'),
    path('categorias/<int:pk>/excluir/', views.categoria_excluir, name='categoria_excluir'),
]
