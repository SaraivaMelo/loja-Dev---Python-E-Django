from django.db import models
# Create your models here.

class Categoria(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Produto(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    qtd = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='produtos/', null=True, blank=True)
    categorie = models.ForeignKey(
        Categoria,
        on_delete = models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} (Estoque: {self.qtd})"