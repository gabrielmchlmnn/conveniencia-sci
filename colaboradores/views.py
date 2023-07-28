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
from hashlib import md5
from django.urls import reverse
from validate_docbr import CPF
from django.db.models import Q
from estoque.models import Estoque
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from produtos.models import Produtos
from django.db.models import Count



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
    total_arrecadado_ultima_ref = 0
    maiores_compradores = Compra.objects.exclude(data__lte=ultimo_26).values('colaborador_id').annotate(total_compras=Round(Sum('total'),2)).order_by('-total_compras')   
    for i in maiores_compradores:
       i['colaborador_id'] = Colaboradore.objects.get(id=i['colaborador_id'])
       total_arrecadado_ultima_ref += float(i['total_compras'])
       total_compras_formatado = f"{float(i['total_compras']):,.2f}".replace(',', '|').replace('.', ',').replace('|', '.')
       i['total_compras'] = total_compras_formatado


    quantidade_compras = Compra.objects.exclude(data__lte=ultimo_26).count()
    dois_meses_atras = hoje.replace(day=26, month=hoje.month-2)
    dia_25_mes_passado = hoje.replace(day=25, month=hoje.month-1)
    if hoje.day > 25:
        dois_meses_atras = hoje.replace(day=26, month=hoje.month-1)
        dia_25_mes_passado = hoje.replace(day=25)

    quantidade_compras_ultima_ref = Compra.objects.filter(data__gte=dois_meses_atras,data__lte = dia_25_mes_passado).count()
    estoque = Estoque.objects.filter(Q(quantidade__lt=4) & Q(produto__situacao="Ativo")).order_by('quantidade')
    produtos_mais_vendidos = Produtos.objects.filter(itemcompra__compra__data__gte=ultimo_26).annotate(total_vendas=Count('itemcompra')).order_by('-total_vendas')
    context = {
       "maiores_compradores":maiores_compradores,'compras_mensal':quantidade_compras,
       'compras_ultima_ref':quantidade_compras_ultima_ref,'estoque':estoque,
       'total_arrecadado':f"{float(total_arrecadado_ultima_ref):,.2f}".replace(',', '|').replace('.', ',').replace('|', '.'),
       'produtos_mais_vendidos':produtos_mais_vendidos
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
        confirmacao = request.POST.get('confirmacao')

        cpf_validator = CPF()
        try:
            if cpf_validator.validate(cpf):
                    lista_cpf = Colaboradore.objects.values_list('cpf',flat=True)
                    if cpf not in lista_cpf:
                        lista_usernames = Colaboradore.objects.values_list('login',flat=True)
                        if login not in lista_usernames:
                            lista_emails = Colaboradore.objects.values_list('email',flat=True)
                            if email not in lista_emails:
                                if senha == confirmacao:
                                    senha = str(senha).encode("utf8")
                                    senha_criptografada = md5(senha).hexdigest()
                                    user = Colaboradore(nome=nome,cpf=cpf,login=login,senha=senha_criptografada,email=email)
                                    user.save()
                                    Enviar_email_bem_vindo({'nome':nome,'email':email})
                                    limpar_cache_sessao(request)
                                    return redirect('MostrarColab')
                                else:
                                    ultima_tentativa = {
                                    'nome':nome,
                                    'cpf':cpf,
                                    'login':login,
                                    'senha':senha,
                                    'email':email,
                                    'confirmacao':confirmacao
                                    }
                                    request.session['ultima_tentativa'] = ultima_tentativa
                                    raise Exception('As senhas não coincidem!')
                            else:
                                ultima_tentativa = {
                                    'nome':nome,
                                    'cpf':cpf,
                                    'login':login,
                                    'senha':senha,
                                    'email':'',
                                    'confirmacao':confirmacao
                                }
                                request.session['ultima_tentativa'] = ultima_tentativa
                                raise Exception('Email indisponível!')
                        else:
                            ultima_tentativa = {
                            'nome':nome,
                            'cpf':cpf,
                            'login':'',
                            'senha':senha,
                            'email':email,
                            'confirmacao':confirmacao
                            }
                            request.session['ultima_tentativa'] = ultima_tentativa
                            raise Exception('Nome de usuário indisponível!')

                    else:
                        ultima_tentativa = {
                            'nome':nome,
                            'cpf':'',
                            'login':login,
                            'senha':senha,
                            'email':email,
                            'confirmacao':confirmacao
                        }
                        request.session['ultima_tentativa'] = ultima_tentativa
                        raise Exception('CPF já cadastrado!')
            else:
                ultima_tentativa = {
                            'nome':nome,
                            'cpf':'',
                            'login':login,
                            'senha':senha,
                            'email':email,
                            'confirmacao':confirmacao
                }
                request.session['ultima_tentativa'] = ultima_tentativa
                raise Exception('Digite um CPF válido!')
        except Exception as erro:
            messages.error(request,f'{erro}')
            return redirect('MostrarColab')

    else:
        return render(request,'colab/mostrar_colab.html')
    

@login_required(login_url='Login')
def MostrarColab(request):
    colaboradores = Colaboradore.objects.all().order_by('nome')
    ultima_tentativa = request.session.get('ultima_tentativa')

    paginator = Paginator(colaboradores, 9) 

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)


    if ultima_tentativa is None:
        return render(request,'colab/mostrar_colab.html',{'colaboradores':page_obj})
    

    else:
        context = {
            'colaboradores':page_obj,'nome':ultima_tentativa['nome'],
            'cpf':ultima_tentativa['cpf'],'login':ultima_tentativa['login'],
            'email':ultima_tentativa['email'],'senha':ultima_tentativa['senha'],
            'confirmacao':ultima_tentativa['confirmacao']
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
            situacao = "Ativo"
        else:
            situacao = "Inativo"

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
                        'cpf':cpf,
                        'login':login,
                        'email':'',
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
        procura = request.session.get('procura_colaboradores')
        if procura is None:
            search_term = request.GET.get('search')
            request.session['procura_colaboradores'] = search_term
        else:
            busca = request.GET.get('search')
            if busca is not None or busca == '':
                search_term = busca
            else:
                search_term = procura
        

        colaboradores_filtrados = Colaboradore.objects.filter(Q(nome__icontains=search_term) | Q(cpf__icontains=search_term) | Q(situacao=search_term) | Q(email__icontains=search_term)|Q(login__icontains=search_term)).order_by('nome')
        paginator = Paginator(colaboradores_filtrados, 9)  

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        return render(request, 'colab/mostrar_colab.html', {'colaboradores': page_obj,'filtro':'filtro'})
    


    
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


def Enviar_email_bem_vindo(destinatario):
        html_content = render_to_string('colab/email_bem_vindo.html', {'nome_colaborador':destinatario['nome']})
        email = EmailMessage(
            'Seu cadastro foi realizado com sucesso!',
            html_content,
            'testeacademia@sci.com.br',
            [f'{destinatario["email"]}']
            )       
        email.content_subtype = 'html'
        email.send()

