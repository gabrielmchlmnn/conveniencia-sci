from django.db import models

# Create your models here.


class Produtos(models.Model):

    nome = models.CharField(max_length=50)
    cod_barras = models.IntegerField()
    preco = models.DecimalField(max_digits=5,decimal_places=2)
    tipo = models.CharField(max_length=20)
    situacao = models.BooleanField(default=True)


    def __str__(self) -> str:
        return self.nome
    

class Estoque(models.Model):
    produto = models.OneToOneField(Produtos,on_delete=models.DO_NOTHING)
    quantidade = models.IntegerField()

    def __str__(self) -> str:
        return self.produto