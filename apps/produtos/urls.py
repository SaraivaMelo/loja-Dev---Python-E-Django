from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('cadastrar/', views.cadastrar_produto, name='cadastrar'),
    path('listar/', views.get_all_produto, name='listar_produtos'),
    path('comprar/<int:produto_id>', views.comprar_produto, name='comprar_produto'),
    path('adicionar/<int:produto_id>', views.kart_adicionar, name='kart_adicionar'),
    path('remover/<int:produto_id>', views.kart_remover, name='kart_remover'),
    path('carrinho/detalhado/', views.carrinho_detalhado, name='carrinho_detalhado'),
    path('carrinho/count/', views.carrinho_count, name='ver_carrinho'),
    path('finalizar/', views.finalizar_compra, name='finalizar'),
    path('pagamento/', views.pagamento, name='pagamento'),
    path('pagamento/concluir/', views.concluir_pagamento, name='concluir_pagamento'),

]
