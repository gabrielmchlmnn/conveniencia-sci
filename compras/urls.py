from django.urls import path,include
from .views import AdicionarItem,RegistrarCompra,DeletarItem,ComecarCompra,ConferirGastos,GerarRelatorio,Carrinho,Deletar_compra,Compras



urlpatterns = [
    path('adicionar-item/',AdicionarItem,name='AdicionarItem'),
    path('registrar-compra/',RegistrarCompra,name='RegistrarCompra'),
    path('deletar-item/<int:id>',DeletarItem,name='DeletarItem'),
    path('comecar-compra/',ComecarCompra,name='ComecarCompra'),
    path('conferir-gastos/',ConferirGastos,name="ConferirGastos"),
    path('gerar-relatorios/',GerarRelatorio,name='GerarRelatorio'),
    path('carrinho/',Carrinho,name='Carrinho'),
    path('deletar-compra/<int:id>',Deletar_compra,name='DeletarCompra'),
    path('compras/',Compras,name='Compra'),
]   