from django.urls import path,include
from .views import ListarEstoque,AdicionarEntrada,AdicionarBaixa,ListarMovimentacoes,FiltrarMovimentacoes,FiltrarEstoque,VoltarEstoque,VoltarMovimentacoes


urlpatterns = [
    path('estoque/',ListarEstoque,name='ListarEstoque'),
    path('adicionar-entrada/',AdicionarEntrada,name='AdicionarEntrada'),
    path('adicionar-baixa/',AdicionarBaixa,name='BaixarEstoque'),
    path('movimentacoes/',ListarMovimentacoes,name='ListarMovimentacoes'),
    path('filtrar-movimentacoes/',FiltrarMovimentacoes,name="FiltrarMovimentacoes"),
    path('filtrar-estoque/',FiltrarEstoque,name='FiltrarEstoque'),
    path('voltar/estoque/',VoltarEstoque,name="VoltarEstoque"),
    path('voltar/movimentacoes/',VoltarMovimentacoes,name='VoltarMovimentacoes')
]