from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from decimal import Decimal, InvalidOperation
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

        if not carrinho:
            messages.error(request, "Seu carrinho está vazio.")
            return redirect('produtos:finalizar')

        # Pegar dados enviados do frontend, só para referência
        desconto_str = request.POST.get('desconto_aplicado', '0').strip()
        desconto_str = desconto_str.replace(',', '.')
        try:
            desconto_fornecido = Decimal(desconto_str)
        except ValueError:
            desconto_fornecido = 0

        # Contar quantidades dos produtos no carrinho
        count = Counter(carrinho)

        # Calcular total bruto (sem desconto)
        total_bruto = 0
        for produto_id, quantidade in count.items():
            try:
                produto = Produto.objects.get(id=produto_id)
                total_bruto += produto.price * quantidade
            except Produto.DoesNotExist:
                messages.error(request, f"Produto com ID {produto_id} não encontrado.")
                return redirect('produtos:finalizar')

        # evita desconto maior que o total
        desconto = min(desconto_fornecido, total_bruto)  
        total_com_desconto = total_bruto - desconto

        # Atualizar valores na sessão
        request.session['desconto'] = float(desconto)
        request.session['total_com_desconto'] = float(total_com_desconto)

        context = {
            'desconto': desconto,
            'total_com_desconto': total_com_desconto,
            'pontos': cliente.points,
            'carrinho': count,
            'total_bruto': total_bruto,
        }

        return render(request, 'produtos/pagamento_concluir.html', context)

    return redirect('produtos:finalizar')

#Concluir o pagamento 
def concluir_pagamento(request):
    if request.method != 'POST':
        return redirect('produtos:finalizar')

    cliente = CustomerProfile.objects.get(user=request.user)
    forma_pagamento = request.POST.get('forma_pagamento')
    valor_raw = request.session.get('total_com_desconto')

    # Valida o valor da sessão
    try:
        total_com_desconto = float(valor_raw)
    except (TypeError, ValueError):
        messages.error(request, "Erro ao processar o pagamento: valor inválido.")
        return redirect('produtos:finalizar')

    # Validação extra se a forma de pagamento for pontos
    if forma_pagamento == 'pontos':
        if cliente.points < total_com_desconto:
            messages.error(request, "Você não tem pontos suficientes para essa compra.")
            return redirect('produtos:finalizar')
        cliente.points -= int(total_com_desconto)
    else:
        cliente.points += int(total_com_desconto)

    carrinho_ids = request.session.get('carrinho', [])
    count = Counter(carrinho_ids)

    # Evitar erro caso o carrinho esteja vazio
    if not count:
        messages.error(request, "Seu carrinho está vazio.")
        return redirect('produtos:finalizar')

    try:
        with transaction.atomic():
            # Criar a venda
            venda = Venda.objects.create(
                cliente=request.user,
                forma_pagamento=forma_pagamento,
                total=total_com_desconto
            )

            # Atualizar estoque e criar itens da venda
            for produto_id, quantidade in count.items():
                produto = Produto.objects.get(id=produto_id)
                if produto.qtd < quantidade:
                    messages.error(request, f"Estoque insuficiente para {produto.name}.")
                    return redirect('produtos:finalizar')

                produto.qtd -= quantidade
                produto.save()

                ItemVenda.objects.create(
                    venda=venda,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.price
                )

            cliente.points = max(cliente.points, 0)  # nunca negativo
            cliente.save()

            # Limpar dados da sessão
            request.session.pop('desconto', None)
            request.session.pop('total_com_desconto', None)
            request.session.pop('carrinho', None)

            messages.success(request, "Compra finalizada com sucesso!")
            return redirect('home')

    except Exception as e:
        messages.error(request, f"Erro ao concluir pagamento: {str(e)}")
        return redirect('produtos:finalizar')
