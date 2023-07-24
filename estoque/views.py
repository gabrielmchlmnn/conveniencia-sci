from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest
from .models import Estoque,Movimentacao_estoque
from django.contrib import messages
from produtos.models import Produtos
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator




# Create your views here.

def VoltarMovimentacoes(request):
    limpar_cache_sessao(request)
    return redirect('ListarMovimentacoes')


def VoltarEstoque(request):
    limpar_cache_sessao(request)
    return redirect('ListarEstoque')

def limpar_cache_sessao(request):
    chaves = list(request.session.keys())  
    for chave in chaves:
        if chave != '_auth_user_id' and chave != '_auth_user_backend' and chave != '_auth_user_hash':
            del request.session[chave] 

@login_required(login_url='Login')
def ListarEstoque(request):
    estoque = Estoque.objects.all().order_by('quantidade')
    lista_estoque = []
    for i in estoque:
        if i.produto.situacao == True:
            lista_estoque.append({'produto':i.produto,'quantidade':i.quantidade})

    paginator = Paginator(lista_estoque, 15)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'estoque':page_obj
    }
    return render(request,'estoque/estoque.html',context=context)



@login_required(login_url='Login')
def FiltrarEstoque(request):

    procura = request.session.get('procura_estoque')
    if procura is None:

        search_term = request.GET.get('search')
        request.session['procura_estoque'] = search_term
    else:
        busca = request.GET.get('search')
        if busca is not None or busca == '':
            search_term = busca
        else:
            search_term = procura
    produtos_filtrados = Estoque.objects.filter(produto__nome__icontains=search_term).filter(produto__situacao=True)

    paginator = Paginator(produtos_filtrados, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'estoque/estoque.html',{'estoque':page_obj,'filtro':'filtro'})






@login_required(login_url='Login')
def AdicionarEntrada(request):
        try:
            quantidade = request.POST.get('quantidade')
            produto_selecionado = request.POST.get('produto')
            produto = Estoque.objects.get(produto=int(produto_selecionado))
            estoque_atualizado = int(produto.quantidade) + int(quantidade)
            Estoque.objects.filter(produto_id=int(produto_selecionado)).update(quantidade=estoque_atualizado)
            usuario = request.user
            movimentacao = Movimentacao_estoque(usuario=usuario,produto=Produtos.objects.get(id=int(produto_selecionado)),quantidade=quantidade,tipo='Entrada')
            movimentacao.save() 
            return redirect('ListarEstoque')
        except Exception:
            messages.error(request,f'Escolha um produto!')
            return redirect('ListarEstoque')



@login_required(login_url='Login')
def AdicionarBaixa(request):
    try:
        quantidade = request.POST.get('quantidade')
        produto_selecionado = request.POST.get('produto')
        if produto_selecionado is not None:
            produto = Estoque.objects.get(produto=int(produto_selecionado))
            estoque_atualizado = int(produto.quantidade) - int(quantidade)
            if estoque_atualizado >= 0:
                produto = Estoque.objects.filter(produto_id=int(produto_selecionado)).update(quantidade=estoque_atualizado)
                usuario = request.user
                movimentacao = Movimentacao_estoque(usuario=usuario,produto=Produtos.objects.get(id=produto_selecionado),quantidade=quantidade,tipo='Saída')
                movimentacao.save() 
                return redirect('ListarEstoque')
            else:
                raise Exception('A quantidade da baixa é maior do que a atual no estoque!') 
        else:
            raise Exception('Selecione um produto!')
    except Exception as erro:
        messages.error(request,f'{erro}')
        return redirect('ListarEstoque')


@login_required(login_url='Login')
def ListarMovimentacoes(request):
    movimentacoes = Movimentacao_estoque.objects.all().order_by('-data')

    paginator = Paginator(movimentacoes, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request,'estoque/movimentacoes.html',{'movimentacoes':page_obj,'usuarios':User.objects.all()})

@login_required(login_url='Login')
def FiltrarMovimentacoes(request):
    data_inicio = request.GET.get('data_inicio')
    data_final = request.GET.get('data_final')
    usuario = request.GET.get('usuario')
    tipo = request.GET.get('botao_tipo')

    filtro = request.session.get('filtro_movimentacoes')
    
    if filtro is not None:
        if data_inicio and data_final:
            request.session['filtro_movimentacoes'] = {'data_inicio':data_inicio,'data_final':data_final}
            movimentacoes_filtradas = Movimentacao_estoque.objects.filter(data__range=(data_inicio,data_final)).order_by('-data')
        elif usuario:
            request.session['filtro_movimentacoes'] = usuario
            movimentacoes_filtradas = Movimentacao_estoque.objects.filter(usuario__username__icontains=usuario).order_by('-data')
        elif tipo:
            request.session['filtro_movimentacoes'] = tipo
            movimentacoes_filtradas = Movimentacao_estoque.objects.filter(tipo=tipo).order_by('-data')

        else:
            if type(filtro) == dict:
                movimentacoes_filtradas = Movimentacao_estoque.objects.filter(data__range=(filtro['data_inicio'],filtro['data_final'])).order_by('-data')
        
            elif filtro == "Entrada" or filtro == "Saída":
                movimentacoes_filtradas = Movimentacao_estoque.objects.filter(tipo__icontains=(filtro)).order_by('-data')
            
            else:
                movimentacoes_filtradas = Movimentacao_estoque.objects.filter(usuario__username__icontains=(filtro)).order_by('-data')
    else:
            
        if data_inicio and data_final:
            request.session['filtro_movimentacoes'] = {'data_inicio':data_inicio,'data_final':data_final}
            movimentacoes_filtradas = Movimentacao_estoque.objects.filter(data__range=(data_inicio,data_final)).order_by('-data')

        if usuario:
            request.session['filtro_movimentacoes'] = usuario
            movimentacoes_filtradas = Movimentacao_estoque.objects.filter(usuario__username__icontains=(usuario)).order_by('-data')
        
        if tipo:
            request.session['filtro_movimentacoes'] = tipo
            movimentacoes_filtradas = Movimentacao_estoque.objects.filter(tipo__icontains=(tipo)).order_by('-data')
        
        

    paginator = Paginator(movimentacoes_filtradas, 15) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    
    return render(request, 'estoque/movimentacoes.html', {'movimentacoes': page_obj,'usuarios':User.objects.all(),'filtro':'filtro'})