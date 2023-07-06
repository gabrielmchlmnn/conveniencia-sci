from django.db import models
from django.contrib.auth.hashers import make_password

# Create your models here.


class Colaboradore(models.Model):
    nome = models.CharField(max_length=70)
    cpf = models.CharField(max_length=14)
    login = models.CharField(unique=True,max_length=50)
    senha = models.CharField(max_length=30)
    situacao = models.BooleanField(default=True)
    email = models.EmailField(default='michelmanngabriel@gmail.com')
    

    def __str__(self) -> str:
        return self.nome
    