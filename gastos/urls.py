from django.urls import path
from . import views

app_name = 'gastos'

urlpatterns = [
    path('gastos/', views.gasto_lista, name='gasto_lista'),
]
