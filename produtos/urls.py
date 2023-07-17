from django.urls import path,include
from .views import AdicionarProdu,EditarProdu,ListarProdu,FiltrarProdu,Voltar

urlpatterns = [
    path('adicionar-produto/',AdicionarProdu,name='AdicionarProdu'),
    path('editar-produto/<int:id>',EditarProdu,name="EditarProdu"),
    path('listar-produtos/',ListarProdu,name="ListarProdu"),
    path('filtrar-produtos/',FiltrarProdu,name="FiltrarProdu"),
    path('voltar-produtos/',Voltar,name='VoltarProdutos')

]