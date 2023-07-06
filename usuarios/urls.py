from django.urls import path,include
from .views import CadastrarUser,ListarUser,EditarUser,FiltrarUsuario,RedefinirSenhaUser

urlpatterns = [
    path('listar-usuarios/',ListarUser,name="ListarUser"),
    path('cadastrar-usuario/',CadastrarUser,name="CadastrarUser"),
    path('editar-usuario/<int:id>/',EditarUser,name='EditarUser'),
    path('filtrar-usuarios/',FiltrarUsuario,name="FiltrarUser"),
    path('redefinir-senha/<int:id>/',RedefinirSenhaUser,name='RedefinirSenhaUser')
]