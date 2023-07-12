from django.db import models
from produtos.models import Produtos
from datetime import datetime
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Estoque(models.Model):
    produto = models.OneToOneField(Produtos,on_delete=models.DO_NOTHING)
    quantidade = models.IntegerField()

    def __str__(self) -> str:
        return self.produto.nome
    

class Movimentacao_estoque(models.Model):
    MOVIMENTACOES_CHOICES = (
    ('Saída', 'Saída'),
    ('Entrada', 'Entrada'),
    )
    data = models.DateTimeField(default=timezone.now)
    usuario = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    produto = models.ForeignKey(Produtos,on_delete=models.DO_NOTHING)
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=7, choices=MOVIMENTACOES_CHOICES)


    