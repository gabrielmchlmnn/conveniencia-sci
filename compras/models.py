from django.db import models
from colaboradores.models import Colaboradore
from produtos.models import Produtos

# Create your models here.

class Compra(models.Model):
    colaborador = models.ForeignKey(Colaboradore,on_delete=models.DO_NOTHING)
    produtos = models.ManyToManyField(Produtos,through='ItemCompra')
    data = models.DateTimeField()
    total = models.DecimalField(max_digits=8,decimal_places=2)


class ItemCompra(models.Model):
    compra = models.ForeignKey(Compra,on_delete=models.DO_NOTHING)
    produto = models.ForeignKey(Produtos,on_delete=models.DO_NOTHING)
    quantidade = models.IntegerField()
    preco_unitario = models.DecimalField(max_digits=8,decimal_places=2)
    total = models.DecimalField(max_digits=8,decimal_places=2,default=10)
