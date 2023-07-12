from django.urls import path,include
from .views import ListarEstoque,AdicionarEntrada,AdicionarBaixa,ListarMovimentacoes,FiltrarMovimentacoes,FiltrarEstoque


urlpatterns = [
    path('estoque/',ListarEstoque,name='ListarEstoque'),
    path('adicionar-entrada/',AdicionarEntrada,name='AdicionarEntrada'),
    path('adicionar-baixa/',AdicionarBaixa,name='BaixarEstoque'),
    path('movimentacoes/',ListarMovimentacoes,name='ListarMovimentacoes'),
    path('filtrar-movimentacoes/',FiltrarMovimentacoes,name="FiltrarMovimentacoes"),
    path('filtrar-estoque/',FiltrarEstoque,name='FiltrarEstoque')
]