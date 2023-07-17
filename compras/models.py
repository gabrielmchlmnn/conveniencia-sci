from django.db import models
from colaboradores.models import Colaboradore
from produtos.models import Produtos
from django.utils import timezone

# Create your models here.

class Compra(models.Model):
    colaborador = models.ForeignKey(Colaboradore,on_delete=models.DO_NOTHING)
    produtos = models.ManyToManyField(Produtos,through='ItemCompra')
    data = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=8,decimal_places=2)

    def __str__(self) -> str:
        return self.id


class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra,on_delete=models.DO_NOTHING)
    produto = models.ForeignKey(Produtos,on_delete=models.DO_NOTHING)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=8,decimal_places=2)
    total = models.DecimalField(max_digits=8,decimal_places=2)
