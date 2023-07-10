from django.urls import path,include
from .views import AdicionarProdu,EditarProdu,ListarProdu,FiltrarProdu,ListarEstoque,AtualizarEstoque

urlpatterns = [
    path('adicionar-produto/',AdicionarProdu,name='AdicionarProdu'),
    path('editar-produto/<int:id>',EditarProdu,name="EditarProdu"),
    path('listar-produtos/',ListarProdu,name="ListarProdu"),
    path('filtrar-produtos',FiltrarProdu,name="FiltrarProdu"),
    path('estoque/',ListarEstoque,name='ListarEstoque'),
    path('atualizar-estoque/<int:id>/',AtualizarEstoque,name='AtualizarEstoque')
]