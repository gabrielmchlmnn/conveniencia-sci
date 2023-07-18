# Create your views here.
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Colaboradore
from compras.models import Compra
from django.db.models import Sum
from django.db.models.functions import Round
from datetime import datetime
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from hashlib import md5
from django.urls import reverse
from validate_docbr import CPF
from django.views.decorators.cache import never_cache
from django.db.models import Q
from estoque.models import Estoque
from django.http import JsonResponse



# Create your views here.

@login_required(login_url='Login')
def Voltar(request):
    limpar_cache_sessao(request)
    return redirect('MostrarColab')

def limpar_cache_sessao(request):
    chaves = list(request.session.keys())  
    for chave in chaves:
        if chave != '_auth_user_id' and chave != '_auth_user_backend' and chave != '_auth_user_hash':
            del request.session[chave] 

def Login(request):
   if request.method == 'POST':
       username = request.POST.get('username')
       senha = request.POST.get('senha')
       user = authenticate(username=username,password=senha)
       if user is not None:
            login(request,user)
            return redirect('Home')
       else:
            messages.error(request,'Credenciais inválidas!')
            return redirect('Login')
   else:
       return render(request,'login/login.html')



@login_required(login_url='Login')
def Home(request):
    hoje = datetime.now()
    ultimo_26 = datetime(hoje.year, hoje.month, 26)
    maiores_compradores = Compra.objects.exclude(data__gte=ultimo_26).values('colaborador_id').annotate(total_compras=Round(Sum('total'),2)).order_by('-total_compras')   
    for i in maiores_compradores:
       i['colaborador_id'] = Colaboradore.objects.get(id=i['colaborador_id'])
       total_compras_formatado = '{:.2f}'.format(i['total_compras'])
       i['total_compras'] = total_compras_formatado

    quantidade_compras = Compra.objects.exclude(data__gte=ultimo_26).count()
    dois_meses_atras = hoje.replace(day=26, month=hoje.month-2)
    dia_25_mes_passado = hoje.replace(day=25, month=hoje.month-1)
    if hoje.day > 25:
        dois_meses_atras = hoje.replace(day=26, month=hoje.month-1)
        dia_25_mes_passado = hoje.replace(day=25)
        
    quantidade_compras_ultima_ref = Compra.objects.filter(data__gte=dois_meses_atras,data__lte = dia_25_mes_passado).count()
    estoque = Estoque.objects.filter(quantidade__lt=4).order_by('quantidade')
    lista_estoque = []
    for i in estoque:
        if i.produto.situacao == True:
            if i.quantidade <4 and i.quantidade>0:
                lista_estoque.append({'produto':i.produto,'quantidade':i.quantidade,'cor':'amarelo'})
            elif i.quantidade <=0:
                    lista_estoque.append({'produto':i.produto,'quantidade':i.quantidade,'cor':'vermelho'})
    context = {
       "maiores_compradores":maiores_compradores,'compras_mensal':quantidade_compras,'compras_ultima_ref':quantidade_compras_ultima_ref,'estoque':lista_estoque
    }
    return render(request,'home/home.html',context=context)



def Logout(request):
   logout(request)
   return redirect('Login') 

@login_required(login_url='Login')
def AdicionarColab(request):
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        login = request.POST.get('username')
        senha = request.POST.get('senha')
        email = request.POST.get('email')

        cpf_validator = CPF()
        try:
            if cpf_validator.validate(cpf):
                    lista_cpf = Colaboradore.objects.values_list('cpf',flat=True)
                    if cpf not in lista_cpf:
                        lista_usernames = Colaboradore.objects.values_list('login',flat=True)
                        if login not in lista_usernames:
                            lista_emails = Colaboradore.objects.values_list('email',flat=True)
                            if email not in lista_emails:
                                senha = str(senha).encode("utf8")
                                senha_criptografada = md5(senha).hexdigest()
                                user = Colaboradore(nome=nome,cpf=cpf,login=login,senha=senha_criptografada,email=email)
                                user.save()
                                limpar_cache_sessao(request)
                                return redirect('MostrarColab')
                            else:
                                ultima_tentativa = {
                                    'nome':nome,
                                    'cpf':cpf,
                                    'login':login,
                                    'senha':senha,
                                    'email':''
                                }
                                request.session['ultima_tentativa'] = ultima_tentativa
                                raise Exception('Email indisponível!')
                        else:
                            ultima_tentativa = {
                            'nome':nome,
                            'cpf':cpf,
                            'login':'',
                            'senha':senha,
                            'email':email
                            }
                            request.session['ultima_tentativa'] = ultima_tentativa
                            raise Exception('Nome de usuário indisponível!')

                    else:
                        ultima_tentativa = {
                            'nome':nome,
                            'cpf':'',
                            'login':login,
                            'senha':senha,
                            'email':email
                        }
                        request.session['ultima_tentativa'] = ultima_tentativa
                        raise Exception('CPF já cadastrado!')
            else:
                raise Exception('Digite um CPF válido!')
        except Exception as erro:
            messages.error(request,f'{erro}')
            return redirect('MostrarColab')

    else:
        return render(request,'colab/mostrar_colab.html')
    

@login_required(login_url='Login')
def MostrarColab(request):
    colaboradores = Colaboradore.objects.all()
    ultima_tentativa = request.session.get('ultima_tentativa')
    for i in colaboradores:
        if i.situacao:
            i.situacao = "Ativo"
        else:
            i.situacao = "Inativo"
    if ultima_tentativa is None:
        print('nao teve')
        return render(request,'colab/mostrar_colab.html',{'colaboradores':colaboradores})
    else:
        print('teve')
        context = {
            'colaboradores':colaboradores,'nome':ultima_tentativa['nome'],
            'cpf':ultima_tentativa['cpf'],'login':ultima_tentativa['login'],
            'email':ultima_tentativa['email'],'senha':ultima_tentativa['senha']
        }
        return render(request,'colab/mostrar_colab.html',context=context)

@login_required(login_url='Login')
def EditarColab(request,id):
    colab = Colaboradore.objects.get(id=id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cpf = request.POST.get('cpf')
        login = request.POST.get('login')
        situacao = request.POST.get('ativo')
        email = request.POST.get('email')

        if situacao == 'on':
            situacao = True
        else:
            situacao = False

        cpf_validator = CPF()


        lista_cpf = Colaboradore.objects.exclude(id=id).values_list('cpf',flat=True)
        try:
            if cpf not in lista_cpf and cpf_validator.validate(cpf):
                lista_usernames = Colaboradore.objects.exclude(id=id).values_list('login',flat=True)
                if login not in lista_usernames:
                    lista_emails = Colaboradore.objects.exclude(id=id).values_list('email',flat=True)
                    if email not in lista_emails:
                        Colaboradore.objects.filter(id=id).update(nome=nome,cpf=cpf,login=login,situacao=situacao,email=email)
                        limpar_cache_sessao(request)
                        return redirect('MostrarColab')
                    else:
                        ultima_tentativa = {
                        'nome':nome,
                        'cpf':'',
                        'login':login,
                        'email':email,
                        'situacao':situacao
                        }
                        request.session['ultima_tentativa'] = ultima_tentativa
                        raise Exception('Email já cadastrado!')
                else:
                    ultima_tentativa = {
                        'nome':nome,
                        'cpf':cpf,
                        'login':'',
                        'email':email,
                        'situacao':situacao
                    }
                    request.session['ultima_tentativa'] = ultima_tentativa
                    raise Exception('Nome de usuário indisponível!')
            else:
                ultima_tentativa = {
                    'nome':nome,
                    'cpf':'',
                    'login':login,
                    'email':email,
                    'situacao':situacao
                }
                request.session['ultima_tentativa'] = ultima_tentativa
                raise Exception('CPF já cadastrado ou inválido!')
        except Exception as erro:
            messages.error(request,f'{erro}')
            url = reverse('EditarColab',args=[colab.id])
            return redirect(url)
  
    else:
        ultima_tentativa = request.session.get('ultima_tentativa')

        if ultima_tentativa is None:
            context = {
                'id': colab.id,'nome':colab.nome,'login':colab.login,'cpf':colab.cpf,'situacao':colab.situacao,'email':colab.email
            }
            return render(request,'colab/editar_colab.html',context=context)
        else:
            context = {
                'id':colab.id,'nome':ultima_tentativa['nome'],'login':ultima_tentativa['login'],
                'cpf':ultima_tentativa['cpf'],'situacao':ultima_tentativa['situacao'],'email':ultima_tentativa['email']
            }
            return render(request,'colab/editar_colab.html',context=context)


@login_required(login_url='Login')
def FiltrarColab(request):
    if request.method == 'GET':
        search_term = request.GET.get('search')
        colaboradores_filtrados = Colaboradore.objects.filter(Q(nome__icontains=search_term) | Q(cpf__icontains=search_term))
        for i in colaboradores_filtrados:
            if i.situacao:
                i.situacao = "Ativo"
            else:
                i.situacao = "Inativo"
        return render(request, 'colab/mostrar_colab.html', {'colaboradores': colaboradores_filtrados})
    


    
@login_required(login_url='Login')
def RedefinirSenha(request,id):
    colab = Colaboradore.objects.get(id=id)
    if request.method == 'POST':
        antiga_senha = request.POST.get('senha_antiga')
        senha = request.POST.get('senha_nova')
        confirmacao = request.POST.get('confirmacao')
        antiga_senha = str(antiga_senha).encode('utf8')
        senha_criptografada = md5(antiga_senha).hexdigest()

        if colab.senha != senha_criptografada:
            url = reverse('RedefinirSenha',args=[colab.id])
            messages.error(request,'A senha antiga está incorreta!')
            return redirect(url)
        
        else:
            if senha != confirmacao:
                print(senha,confirmacao)
                url = reverse('RedefinirSenha',args=[colab.id])
                messages.error(request,'As novas senhas não coincidem!')
                return redirect(url)
            else:
                senha = str(senha).encode('utf8')
                Colaboradore.objects.filter(id=id).update(senha=md5(senha).hexdigest())
                return redirect('MostrarColab')
            


    else:
        return render(request,'colab/redefinir_senha.html',{'id':colab.id})




# senha = request.POST.get('senha')
# senha = str(senha).encode('utf8')
# senha_criptografada = md5(senha).hexdigest()
# senha=senha_criptografada