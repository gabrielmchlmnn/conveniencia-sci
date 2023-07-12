from django.contrib import admin
from .models import Estoque,Movimentacao_estoque

# Register your models here.

admin.site.register(Estoque)
admin.site.register(Movimentacao_estoque)
