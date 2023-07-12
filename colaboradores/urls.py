from django.urls import path,include
from .views import Login,Home,Logout,AdicionarColab,MostrarColab,EditarColab,FiltrarColab,RedefinirSenha

urlpatterns = [
   path('',Login,name='Login'),
   path('home/',Home,name='Home'),
   path('',include('compras.urls')),
   path('logout/',Logout,name='Logout'),
   path('home/adicionar-colaborador/',AdicionarColab,name='AdicionarColab'),
   path('home/',include('produtos.urls')),
   path('home/mostrar-colaboradores/',MostrarColab,name='MostrarColab'),
   path('home/',include('usuarios.urls')),
   path('home/editar-colaborador/<int:id>/',EditarColab,name='EditarColab'),
   path('home/filtrar-colaboradores',FiltrarColab,name="FiltrarColab"),
   path('home/colaborador/redefinir-senha/<int:id>',RedefinirSenha,name='RedefinirSenha'),
   path('home/',include('estoque.urls')),
   ]
