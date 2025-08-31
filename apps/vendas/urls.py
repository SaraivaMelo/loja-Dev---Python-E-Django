from django.urls import path
from . import views

app_name = 'vendas'

urlpatterns = [
    path('cadastrar/', views.cadastrar_venda, name='cadastrar_venda'),
]
