from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.contrib import messages
from django.core.paginator import Paginator


                                                    

                                                    


# Create your views here.
@user_passes_test(lambda u: u.is_superuser)
def Voltar(request):
    limpar_cache_sessao(request)
    return redirect('ListarUser')


def limpar_cache_sessao(request):
    chaves = list(request.session.keys())  
    for chave in chaves:
        if chave != '_auth_user_id' and chave != '_auth_user_backend' and chave != '_auth_user_hash':
            del request.session[chave] 


@user_passes_test(lambda u: u.is_superuser)
def CadastrarUser(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        usuario = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmacao = request.POST.get('confirmacao')
        try:
            lista_usuarios = User.objects.values_list('username',flat=True)
            if usuario not in lista_usuarios:
                lista_emails = User.objects.values_list('email',flat=True)
                if email not in lista_emails:
                    if senha == confirmacao:
                        user = User.objects.create_user(first_name=nome, username=usuario,email=email,password=senha)
                        user.save()
                        limpar_cache_sessao(request)
                        return redirect('ListarUser')
                    else:
                        ultima_tentativa = {
                            'nome':nome,
                            'usuario':usuario,
                            'email':email,
                            'senha':'',
                            'confirmacao':''
                        }
                        request.session['ultima_tentativa'] = ultima_tentativa
                        raise Exception('As senhas não coincidem!')
                else:
                    ultima_tentativa = {
                            'nome':nome,
                            'usuario':usuario,
                            'email':'',
                            'senha':senha,
                            'confirmacao':confirmacao
                        }
                    request.session['ultima_tentativa'] = ultima_tentativa
                    raise Exception('Email indisponível!')
            else:
                ultima_tentativa = {
                            'nome':nome,
                            'usuario':'',
                            'email':email,
                            'senha':senha,
                            'confirmacao':confirmacao
                        }
                request.session['ultima_tentativa'] = ultima_tentativa
                raise Exception('Nome de usuário indisponível!')
        except Exception as erro:
            messages.error(request,f'{erro}')
            return redirect('ListarUser')
    else:
        return render(request,'usuarios/listar_usuario.html')
        


@user_passes_test(lambda u: u.is_superuser)
def ListarUser(request):
    ultima_tentativa = request.session.get('ultima_tentativa')
    usuarios = User.objects.all()


    paginator = Paginator(usuarios, 9)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    if ultima_tentativa is None:
        
        context = {
            'usuarios': page_obj
        }
    else:
        context = {
            'usuarios':page_obj,'nome':ultima_tentativa['nome'],'username':ultima_tentativa['usuario'],'email':ultima_tentativa['email'],
            'senha':ultima_tentativa['senha'],'confirmacao':ultima_tentativa['confirmacao']
        }
    return render(request,'usuarios/listar_usuario.html',context=context)




@user_passes_test(lambda u: u.is_superuser)
def EditarUser(request,id):
    usuario = User.objects.get(id=id)
    if request.method == 'POST':
        login = request.POST.get('username')
        nome = request.POST.get('nome')
        email = request.POST.get('email')
        lista_usernames = User.objects.exclude(id=id).values_list('username',flat=True)
        try:
            if login not in lista_usernames:
                lista_email = User.objects.exclude(id=id).values_list('email',flat=True)
                if email not in lista_email:
                    User.objects.filter(id=id).update(username=login,first_name=nome,email=email)
                    limpar_cache_sessao(request)
                    return redirect('ListarUser')
                else:
                    ultima_edicao = {
                        'nome':nome,
                        'email':'',
                        'login':login
                    }
                    request.session['ultima_edicao'] = ultima_edicao
                    raise Exception('Email indisponível!')
            else:  
                ultima_edicao = {
                        'nome':nome,
                        'email':email,
                        'login':''
                    }
                request.session['ultima_edicao'] = ultima_edicao  
                raise Exception('Nome de usuário indisponível!')
        except Exception as erro:
            messages.error(request,f'{erro}')
            url = reverse('EditarUser',args=[usuario.id])
            return redirect(url)

    else:
        ultima_edicao = request.session.get('ultima_edicao')
        if ultima_edicao is None:
            context = {
                'username':usuario.username,'id':usuario.id,'nome':usuario.first_name,'email':usuario.email
            }
        else:
            context = {
                'username':ultima_edicao['login'],'id':usuario.id,'nome':ultima_edicao['nome'],'email':ultima_edicao['email']
            }
        return render(request,'usuarios/editar_usuario.html',context=context)




@user_passes_test(lambda u: u.is_superuser)
def FiltrarUsuario(request):
    if request.method == 'GET':
        filtro_usuarios = request.session.get('filtro_usuarios')

        if filtro_usuarios is None:
            search_term = request.GET.get('search')
            request.session['filtro_usuarios'] = search_term
        else:
            busca = request.GET.get('search')
            if busca is not None:
                search_term = busca
            else:
                search_term = filtro_usuarios
        
        usuarios_filtrados = User.objects.filter(username__icontains=search_term)

        paginator = Paginator(usuarios_filtrados, 9)  

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        return render(request, 'usuarios/listar_usuario.html', {'usuarios': page_obj,'filtro':'filtro'})
    

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
    

@user_passes_test(lambda u: u.is_superuser)
def DeletarUser(request,id):
    usuario = User.objects.get(id=id)
    print(usuario)
    usuario.delete()
    return redirect('ListarUser')

            