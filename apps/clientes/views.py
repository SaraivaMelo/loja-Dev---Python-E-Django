from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .cliente_forms import UserRegisterForm, AddressForm, CustomerProfileForm
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.contrib.auth import logout
from .models import CustomerProfile, Address
from apps.vendas.models import ItemVenda, Venda


@login_required(login_url='clientes:login')
def clientes(request):
    user = request.user
    
    try:
       profile = CustomerProfile.objects.get(user=user)
       address = profile.address
       vendas = Venda.objects.filter(cliente=user).order_by('-data')
       itens_venda = ItemVenda.objects.filter(venda__in=vendas)

    except CustomerProfile.DoesNotExist:
        profile = None
        address = None
        vendas = []
        itens_venda = []

    data_user = {
        'user': user,
        'profile': profile,
        'address': address,
        'vendas': vendas,
        'itens_venda': itens_venda,
    }
    
    return render(request, 'clientes/area_cliente.html', data_user)

def cadastro(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        address_form = AddressForm(request.POST)
        profile_form = CustomerProfileForm(request.POST)

        if user_form.is_valid() and address_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            address = address_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.address = address
            profile.save()

            login(request, user)
            return redirect('clientes:clientes')
    else:
        user_form = UserRegisterForm()
        address_form = AddressForm()
        profile_form = CustomerProfileForm()

    return render(request, 'clientes/cadastro.html', {
        'user_form': user_form,
        'address_form': address_form,
        'profile_form': profile_form,
    })

def login_cliente(request):
    if request.method == 'POST':
        email = request.POST['email']
        senha = request.POST['senha']

        try:
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=senha)

            if user is not None:
                login(request, user)
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)

                # Exemplo de redirecionamento condicional
                if user.is_staff:  # ou user.is_superuser
                    return redirect('produtos:cadastrar')
                else:
                    return redirect('clientes:clientes')
            else:
                messages.error(request, 'E-mail e/ou senha inválidos.')
        except User.DoesNotExist:
            messages.error(request, 'E-mail não encontrado.')

    return render(request, 'clientes/login.html')


def logout_cliente(request):
    logout(request)
    messages.success(request, "Logout realizado com sucesso.")  # <-- Use success, não error
    return redirect('clientes:login')


@login_required(login_url='clientes:login')
def atualiza_dados(request):
    if request.method == 'POST':
        user = request.user
        name = request.POST.get('name')
        phone = request.POST.get('phone')

        user.first_name = name
        user.save()

        profile = CustomerProfile.objects.get(user=user)
        profile.phone = phone
        profile.save()

        data_user = {
            'name': name,
            'profile': profile
        }
        # return redirect('clientes:clientes')
        return render(request, 'clientes/dados_content.html', {data_user})