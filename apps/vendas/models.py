from django.db import models
from django.contrib.auth.models import User
from apps.produtos.models import Produto

class Venda(models.Model):
    cliente = models.ForeignKey(User, on_delete=models.CASCADE)
    data = models.DateTimeField(auto_now_add=True)
    forma_pagamento = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    nf = models.IntegerField(unique=True, blank=True, null=True) 
    
    # Na hora de salvar, o sistema gera uma NF e salva no banco 
    
    def save(self, *args, **kwargs):
        if not self.nf:
            ultima_nf = Venda.objects.aggregate(models.Max('nf'))['nf__max'] or 0
            self.nf = ultima_nf + 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venda #{self.id} - Cliente: {self.cliente.username}"
    
class ItemVenda(models.Model):
    venda = models.ForeignKey(Venda, on_delete=models.CASCADE, related_name='itens')
    produto = models.ForeignKey(Produto, on_delete=models.SET_NULL, null=True)
    quantidade = models.PositiveIntegerField()
    preco_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantidade}x {self.produto.name}"