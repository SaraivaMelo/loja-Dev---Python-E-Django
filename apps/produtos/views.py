from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Categoria, Produto
from .produto_forms import ProdutoForm
from django.http import JsonResponse
from collections import Counter
from ..clientes.models import CustomerProfile
from apps.vendas.models import Venda, ItemVenda

def is_admin(user):
    return user.is_authenticated and user.is_staff


#Cadastrar no banco
@user_passes_test(is_admin)
def cadastrar_produto(request):

    categorias_padrao = ['Eletrônicos', 'Roupas']
    for nome in categorias_padrao:
        Categoria.objects.get_or_create(name=nome)

    categorias = Categoria.objects.all()
    
    if request.method == 'POST':
        form = ProdutoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Produto cadastrado com sucesso!')
            return redirect('produtos:cadastrar')

        else:
            messages.error(request, 'Erro ao cadastrar o produto. Verifique os dados.')
            print("Form inválido!")
            print(form.errors)  
    else:
        form = ProdutoForm()
    
    produtos = Produto.objects.all()
    context = {
        'form': form,
        'categorias': categorias,
        'produtos': produtos,
    }

    return render(request, 'produtos/cadastrar.html', context)

#Buscar todos os produtos no bancopra mostrar na tela.
def get_all_produto(request):
    prods = Produto.objects.all()
    # print(prods)
    context = {
        'produtos': prods
    }
    return render(request, "produtos/listar_produtos.html", context)         

#Se o cliente clicar em comprar, chama essa view
def comprar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    carrinho_ids = request.session.get('carrinho', [])
    carrinho_produtos = Produto.objects.filter(id__in=carrinho_ids)

    context = {
        'produto': produto,
        'carrinho': carrinho_produtos
    }
    return render(request, "produtos/cart_produto.html", context)

#Se ele clicar em adicionar no carrinho, chama essa  
def kart_adicionar(request, produto_id):
    try:
        if request.method == 'POST':
            produto = get_object_or_404(Produto, id=produto_id)

            carrinho = request.session.get('carrinho', [])
            if produto_id not in carrinho:
                carrinho.append(produto_id)
                request.session['carrinho'] = carrinho

            produtos = Produto.objects.filter(id__in=carrinho)

            produtos_data = [
                {
                    'id': p.id,
                    'name': p.name,
                    'price': str(p.price)
                } for p in produtos
            ]

            return JsonResponse({'produtos': produtos_data})

        return JsonResponse({'erro': 'Método não permitido'}, status=405)

    except Exception as e:
        return JsonResponse({'erro': str(e)}, status=500)

#Se ele desistir de comprar ele clica no X e chama essa view 
def kart_remover(request, produto_id):
    if request.method == 'POST':
        carrinho = request.session.get('carrinho', [])

        produto_id = int(produto_id)
        carrinho = [int(id) for id in carrinho]
        
        if produto_id in carrinho:
            carrinho.remove(produto_id)
            request.session['carrinho'] = carrinho

        produtos = Produto.objects.filter(id__in=carrinho)
        produtos_data = [
            {
                'id': p.id,
                'name': p.name,
                'price': str(p.price)
            } for p in produtos
        ]
        return JsonResponse({'produtos': produtos_data})

    return JsonResponse({'erro': 'Método não permitido'}, status=405)

#Quantidade de itens no carrinho
def carrinho_count(request):
    carrinho = request.session.get('carrinho', [])
    return JsonResponse({'quantidade': len(carrinho)})

#mostrar os itens do carinho sem precisar clicar em adicionar
def carrinho_detalhado(request):
    carrinho = request.session.get('carrinho', [])
    produtos = Produto.objects.filter(id__in=carrinho)
    produtos_data = [
        {
            'id': p.id,
            'name': p.name,
            'price': str(p.price)
        } for p in produtos
    ]
    return JsonResponse({'produtos': produtos_data})



def adicionar_ao_carrinho(request, produto_id):
    carrinho = request.session.get('carrinho', [])
    if produto_id not in carrinho:
        carrinho.append(produto_id)
        request.session['carrinho'] = carrinho
    return redirect('produtos:ver_carrinho')


# Processo de concluir a compra
def finalizar_compra(request):
    carrinho_ids = request.session.get('carrinho', [])
    count = Counter(carrinho_ids)
    produtos = Produto.objects.filter(id__in=count.keys())

    produtos_detalhados = []
    total = 0
    cliente = CustomerProfile.objects.get(user=request.user)
    for produto in produtos:
        quantidade = count[produto.id]
        subtotal = produto.price * quantidade
        total += subtotal
        produtos_detalhados.append({
            'produto': produto,
            'quantidade': quantidade,
            'subtotal': subtotal
        })

    context = {
        'produtos': produtos_detalhados,
        'total': total,
        'pontos': cliente.points,

    }

    return render(request, 'produtos/finalizar.html', context)

def pagamento(request):
    if request.method == 'POST':
        
        carrinho = request.session.get('carrinho', [])
        cliente = CustomerProfile.objects.get(user=request.user)

        # Dados que vêm do formulário
        desconto = request.POST.get('desconto_aplicado')
        total_com_desconto = request.POST.get('total_com_desconto')

        # Salvar na sessão (opcional, caso precise usar depois)
        request.session['desconto'] = desconto
        request.session['total_com_desconto'] = total_com_desconto

        context = {
            'desconto': desconto,
            'total_com_desconto': total_com_desconto,
            'pontos': cliente.points
        }

        return render(request, 'produtos/pagamento_concluir.html', context)

    return redirect('produtos:finalizar')

def concluir_pagamento(request):
    if request.method == 'POST':
        forma_pagamento = request.POST.get('forma_pagamento')
        cliente = CustomerProfile.objects.get(user=request.user)

        total_com_desconto = float(request.session.get('total_com_desconto', 0))
        pontos_cliente = cliente.points or 0

        # Atualizar pontuação na base se o pagamento for com pontos 
        if forma_pagamento == 'pontos':
            # Cliente paga com pontos, então subtrai
            cliente.points -= int(total_com_desconto)
        else:
            # Cliente paga normal, então acumula pontos
            cliente.points += int(total_com_desconto)
        
        #Criar os itens para a tabela vendas
        venda = Venda(
            cliente=request.user,
            forma_pagamento=forma_pagamento,
            total=total_com_desconto
        )
        venda.save()
        
        cliente.save()
        carrinho_ids = request.session.get('carrinho', [])
        count = Counter(carrinho_ids)

        #Cria os itens na tabela item_venda
        for produto_id, quantidade in count.items():
            try:
                produto = Produto.objects.get(id=produto_id)
                if produto.qtd >= quantidade:
                    produto.qtd -= quantidade
                    produto.save()
                else:
                    messages.error(request, f'Estoque insuficiente para {produto.name}.')
                    return redirect('produtos:finalizar')
                
                ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.price
                )
            except Produto.DoesNotExist:
                print(f"Produto com ID {produto_id} não encontrado. Ignorado.")

         # Limpar dados de pagamento da sessão 
        request.session.pop('desconto', None)
        request.session.pop('total_com_desconto', None)
        request.session.pop('carrinho', None)
        
        messages.success(request, 'Compra finalizada com sucesso!')
        return redirect('home')

    return redirect('produtos:finalizar')
