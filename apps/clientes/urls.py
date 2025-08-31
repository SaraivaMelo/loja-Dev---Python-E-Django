from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    path('clientes/', views.clientes, name='clientes'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('login/', views.login_cliente, name='login'),
    path('logout/', views.logout_cliente, name='logout'),
    path('atualizar-dados/', views.atualiza_dados, name='atualizar_dados'),

]
