from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.


class Colaboradore(models.Model):
    nome = models.CharField(max_length=70)
    cpf = models.CharField(max_length=14)
    login = models.CharField(unique=True,max_length=50)
    senha = models.CharField(max_length=30)
    situacao = models.CharField(default="Ativo",max_length=7)
    email = models.EmailField(default='michelmanngabriel@gmail.com')
    cod_barras_colab = models.CharField(max_length=10,default='1009463')

    def __str__(self) -> str:
        return self.nome
    
    @property
    def codigo_de_barras(self):
        return self.cpf