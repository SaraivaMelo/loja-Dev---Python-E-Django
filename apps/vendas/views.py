from django.shortcuts import render, redirect
from django.contrib import messages
from collections import Counter
from .models import Venda, ItemVenda
from apps.produtos.models import Produto
from apps.clientes.models import CustomerProfile

def cadastrar_venda(request):
    if request.method == "POST":
        cliente = request.user
        carrinho = request.session.get('carrinho', {})
        forma_pagamento = request.POST.get('forma_pagamento')

        if not carrinho:
             return redirect('produtos:carrinho_detalhado')

        total = 0
        for item in carrinho.values():
            total += float(item['preco']) * int(item['quantidade'])

        # Aqui cria a venda, ou seja, vai pra tabela venda
        venda = Venda.objects.create(
            cliente = cliente,  
            forma_pagamento = forma_pagamento,
            total = total
        )   

        for produto_id, item in carrinho.items():

            produto = Produto.objects.get(id=produto_id)

            qtd = int(item['quantidade'])

            if produto.qtd >= qtd:
                produto.qtd -= qtd
                produto.save()
            else:
                messages.error(request, f'Estoque insuficiente para {produto.name}.')
                return redirect('produtos:finalizar')
            ItemVenda.objects.create(

                venda=venda,
                produto=produto,
                quantidade=item['quantidade'],
                preco_unitario=item['preco']
            )

        #Atualizar a coluna de pontos do cliente 
        profile = CustomerProfile.objects.get(user=cliente)

        if forma_pagamento == 'pontos':
            # Se ele tiver usado os pontos para pagar, então retira pontos 
            profile.points -= int(total)
        else:
            # caso contrário, ele ganha pontos 
            profile.points += int(total)

        profile.save()

        # Limpa o carrinho da sessão
        request.session['carrinho'] = {}
        request.session['desconto'] = 0
        request.session['total_com_desconto'] = 0

        return redirect('home') 