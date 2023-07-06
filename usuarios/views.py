from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.contrib import messages

                                                    

                                                    


# Create your views here.

@user_passes_test(lambda u: u.is_superuser)
def CadastrarUser(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        senha = request.POST.get('senha')
        lista_usuarios = User.objects.values_list('username',flat=True)
        if usuario not in lista_usuarios:
            user = User.objects.create_user(username=usuario,password=senha)
            user.save()
            return redirect('ListarUser')
        else:
            messages.error(request,'Nome de usuário indisponível!')
            return redirect('ListarUser')
    else:
        return render(request,'usuarios/criar_usuario.html')
        


@user_passes_test(lambda u: u.is_superuser)
def ListarUser(request):
    context = {
        'usuarios': User.objects.all()
    }
    return render(request,'usuarios/listar_usuario.html',context=context)




@user_passes_test(lambda u: u.is_superuser)
def EditarUser(request,id):
    usuario = User.objects.get(id=id)
    if request.method == 'POST':
        login = request.POST.get('username')
        lista_usuarios = User.objects.exclude(id=id).values_list('username',flat=True)
        if login not in lista_usuarios:
            user = User.objects.filter(id=id).update(username=login)
            return redirect('ListarUser')
        else:
            messages.error(request,'Nome de usuário indisponível!')
            url = reverse('EditarUser',args=[usuario.id])
            return redirect(url)

    else:
        context = {
            'username':usuario.username,'id':usuario.id
        }
        return render(request,'usuarios/editar_usuario.html',context=context)
    


@user_passes_test(lambda u: u.is_superuser)
def FiltrarUsuario(request):
    if request.method == 'GET':
        search_term = request.GET.get('search')
        usuarios_filtrados = User.objects.filter(username__icontains=search_term)
        return render(request, 'usuarios/listar_usuario.html', {'usuarios': usuarios_filtrados})
    

@user_passes_test(lambda u: u.is_superuser)
def RedefinirSenhaUser(request,id):
    usuario = User.objects.get(id=id)
    if request.method == 'POST':
        nova_senha = request.POST.get('senha_nova')
        confirmacao = request.POST.get('confirmacao')

        if nova_senha == confirmacao:
            usuario.set_password(confirmacao)
            usuario.save()
            return redirect('ListarUser')
        else:
            messages.error(request,'As novas senhas não coincidem!')
            url = reverse('RedefinirSenhaUser',args=[usuario.id])
            return redirect(url)

    else:
        return render(request, 'usuarios/redefinir_senha.html',{'id':usuario.id})
            