from django.shortcuts import render,redirect
from .models import Produtos
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from estoque.models import Estoque
from decimal import Decimal
from django.core.paginator import Paginator


@login_required(login_url='Login')
def Voltar(request):
    limpar_cache_sessao(request)
    return redirect('ListarProdu')


def limpar_cache_sessao(request):
    chaves = list(request.session.keys())  
    for chave in chaves:
        if chave != '_auth_user_id' and chave != '_auth_user_backend' and chave != '_auth_user_hash':
            del request.session[chave] 



@login_required(login_url='Login')
def AdicionarProdu(request):
        
        nome = request.POST.get('nome')
        cod_barras = request.POST.get('cod_barras')
        cod_barras = cod_barras.replace('-','').replace('_','')
        preco = request.POST.get('preco')
        tipo = request.POST.get('tipo')
        request.session['nome'] = nome
        request.session['cod_barras'] = cod_barras
        request.session['preco'] = preco
        request.session['tipo'] = tipo

        lista_cods = Produtos.objects.values_list('cod_barras',flat=True)
        try:
            if len(cod_barras) == 12:
                if int(cod_barras) not in lista_cods:
                    preco = preco.replace('R$ ','').replace(',','.')
                    novo_produto = Produtos(nome=nome,cod_barras=int(cod_barras),preco=Decimal(preco),tipo=tipo)
                    novo_produto.save()
                    estoque_novo = Estoque(produto=novo_produto,quantidade=0)
                    estoque_novo.save()
                    limpar_cache_sessao(request)
                    return redirect('ListarProdu')
                else:
                    raise Exception('Código de barras já cadastrado!')
            else:
                ultimo_produto = {
                'nome': nome,
                'cod_barras': cod_barras,
                'preco': preco,
                'tipo': tipo
                }
                request.session['ultimo_produto'] = ultimo_produto
                raise Exception('O código de barras deve ter 12 números!')
        except Exception as erro:
            ultimo_produto = {
                'nome': nome,
                'cod_barras': '',
                'preco': preco,
                'tipo': tipo
            }
            request.session['ultimo_produto'] = ultimo_produto
            messages.error(request,f'{erro}')

            return redirect('ListarProdu')


@login_required(login_url='Login')
def ListarProdu(request):
    ultimo_produto = request.session.get('ultimo_produto')
    produtos = Produtos.objects.all().order_by('nome')
    for i in produtos:
        if i.situacao == True:
            i.situacao = 'Ativo'
            i.cod_barras = str(i.cod_barras)
        else:
            i.situacao = "Inativo"
            i.cod_barras = str(i.cod_barras)

    paginator = Paginator(produtos, 9)  

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if ultimo_produto is None:
        return render(request, 'produtos/listar_produ.html', {'produto': page_obj})
    else:
        context = {'produto': page_obj, 'nome': ultimo_produto['nome'], 'cod_barras': ultimo_produto['cod_barras'],
                   'preco': ultimo_produto['preco'], 'tipo': ultimo_produto['tipo']}
        return render(request, 'produtos/listar_produ.html', context=context)



@login_required(login_url='Login')
def EditarProdu(request,id):
    produto = Produtos.objects.get(id=id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cod_barras = request.POST.get('cod_barras')
        cod_barras = cod_barras.replace('-','').replace('_','')
        preco = request.POST.get('preco')
        tipo = request.POST.get('tipo')
        situacao =  request.POST.get('ativo')
        lista_cods = Produtos.objects.exclude(id=id).values_list('cod_barras',flat=True)
        try:
            if len(cod_barras) == 12:
                if int(cod_barras) not in lista_cods:
                    if situacao == 'on':
                        situacao = True
                    else:
                        situacao = False
                    preco = preco.replace('R$ ','').replace(',','.')
                    print(preco)
                    produto = Produtos.objects.filter(id=id).update(nome=nome,cod_barras=int(cod_barras),preco=Decimal(preco),tipo=tipo,situacao=situacao)
                    limpar_cache_sessao(request)
                    return redirect('ListarProdu')
                
                else:
                    ultima_tentativa = {
                        'nome':nome,
                        'cod_barras':cod_barras,
                        'preco':preco,
                        'tipo':tipo,
                        'situacao':situacao,
                    }
                    request.session['ultima_tentativa'] = ultima_tentativa
                    raise Exception('Código de barras já cadastrado!')
            else:
                ultima_tentativa = {
                    'nome':nome,
                    'cod_barras':cod_barras,
                    'preco':preco,
                    'tipo':tipo,
                    'situacao':situacao,
                }
                request.session['ultima_tentativa'] = ultima_tentativa
                raise Exception('O código de barra precisa ter 12 números!')
        except Exception as erro:
            messages.error(request,f'{erro}')
            url = reverse('EditarProdu',args=[produto.id])
            return redirect(url)
        
    else:  
        ultima_tentativa = request.session.get('ultima_tentativa')
        if ultima_tentativa is None:
            context = {     
            "nome":produto.nome,'cod_barras':produto.cod_barras,'preco':produto.preco,'id':produto.id,
            'tipo':produto.tipo,'situacao':produto.situacao
            }
            return render(request,'produtos/editar_produ.html',context=context)
        else:
            context = {     
            "nome":ultima_tentativa['nome'],'cod_barras':ultima_tentativa['cod_barras'],
            'preco':ultima_tentativa['preco'],'id':produto.id,'tipo':ultima_tentativa['tipo'],
            'situacao':ultima_tentativa['situacao']
            }
            return render(request,'produtos/editar_produ.html',context=context)
    



@login_required(login_url='Login')
def FiltrarProdu(request):
    if request.method == 'GET':
        procura = request.session.get('procura')
        if procura is None:

            search_term = request.GET.get('search')
            request.session['procura'] = search_term
        else:
            busca = request.GET.get('search')
            if busca is not None or busca == '':
                search_term = busca
            else:
                search_term = procura

        produtos_filtrados = Produtos.objects.filter(Q(nome__icontains=search_term) | Q(cod_barras__icontains=search_term)).order_by('nome')
        for i in produtos_filtrados:
            if i.situacao == True:
                i.situacao = 'Ativo'
            else: 
                i.situacao = 'Inativo'

        paginator = Paginator(produtos_filtrados, 9) 

        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'produtos/listar_produ.html', {'produto': page_obj,'filtro':'filtro'})

    

