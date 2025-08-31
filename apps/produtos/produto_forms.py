from django import forms
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['name', 'description', 'price', 'qtd', 'categorie', 'image']

def clean_price(self):
    price = self.cleaned_data['price']
    # Se for string e tiver vírgula, troca por ponto
    if isinstance(price, str):
        price = price.replace(',', '.')
    return price