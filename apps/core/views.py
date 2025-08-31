from django.shortcuts import render
from apps.produtos.models import Produto

def home(request):
    produtos = Produto.objects.all()
    print(produtos)
    return render(request, 'home.html', {'produtos': produtos})