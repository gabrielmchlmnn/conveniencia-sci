from django.shortcuts import render,redirect
from .models import Produtos
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.http import HttpResponseBadRequest
from estoque.models import Estoque
from django.core.cache import cache


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
        preco = request.POST.get('preco')
        tipo = request.POST.get('tipo')
        request.session['nome'] = nome
        request.session['cod_barras'] = cod_barras
        request.session['preco'] = preco
        request.session['tipo'] = tipo

        lista_cods = Produtos.objects.values_list('cod_barras',flat=True)
        try:
            if int(cod_barras) not in lista_cods:
                novo_produto = Produtos(nome=nome,cod_barras=int(cod_barras),preco=preco,tipo=tipo)
                novo_produto.save()
                estoque_novo = Estoque(produto=novo_produto,quantidade=0)
                estoque_novo.save()
                limpar_cache_sessao(request)
                return redirect('ListarProdu')
            else:
                raise Exception('Código de barras já cadastrado!')
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
    produtos = Produtos.objects.all()
    for i in produtos:
        if i.situacao == True:
            i.situacao = 'Ativo'
        else:
            i.situacao = "Inativo"

    if ultimo_produto is None:
        return render(request,'produtos/listar_produ.html',{'produto':produtos})
    else:
        context = {'produto':produtos,'nome':ultimo_produto['nome'],'cod_barras':ultimo_produto['cod_barras'],
                 'preco':ultimo_produto['preco'],'tipo':ultimo_produto['tipo']}
        return render(request,'produtos/listar_produ.html',context=context)



@login_required(login_url='Login')
def EditarProdu(request,id):
    produto = Produtos.objects.get(id=id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cod_barras = request.POST.get('cod_barras')
        preco = request.POST.get('preco')
        tipo = request.POST.get('tipo')
        situacao =  request.POST.get('ativo')
        if situacao == 'on':
            situacao = True
        else:
            situacao = False
        lista_cods = Produtos.objects.exclude(id=id).values_list('cod_barras',flat=True)
        try:
            if int(cod_barras) not in lista_cods:
                if situacao == 'on':
                    situacao = True
                else:
                    situacao = False
                Produtos.objects.filter(id=id).update(nome=nome,cod_barras=int(cod_barras),preco=preco,tipo=tipo,situacao=situacao)
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
        search_term = request.GET.get('search')
        produtos_filtrados = Produtos.objects.filter(Q(nome__icontains=search_term) | Q(cod_barras__icontains=search_term))
        for i in produtos_filtrados:
            if i.situacao == True:
                i.situacao = 'Ativo'
            else: 
                i.situacao = 'Inativo'
        return render(request, 'produtos/listar_produ.html', {'produto': produtos_filtrados})
    

