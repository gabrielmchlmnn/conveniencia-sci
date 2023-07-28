from django.db import models

# Create your models here.


class Produtos(models.Model):
    TIPOS_CHOICES = (
    ('Alimento', 'Alimento'),
    ('Ingresso', 'Ingresso'),
    ('Roupa','Roupa')
    )   
    nome = models.CharField(max_length=50)
    cod_barras = models.IntegerField()
    preco = models.DecimalField(max_digits=200,decimal_places=2)
    tipo = models.CharField(max_length=8,choices=TIPOS_CHOICES)
    situacao = models.CharField(default="Ativo", max_length=7)


    def __str__(self) -> str:
        return self.nome
    

