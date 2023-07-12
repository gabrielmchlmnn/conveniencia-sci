from django.shortcuts import render,redirect
from django.http import HttpResponseBadRequest
from .models import Estoque,Movimentacao_estoque
from django.contrib import messages
from produtos.models import Produtos
from django.db.models import Q
from django.contrib.auth.models import User



# Create your views here.


def ListarEstoque(request):
        estoque = Estoque.objects.all()
        lista_estoque = []
        for i in estoque:
            if i.produto.situacao == True:
                lista_estoque.append({'produto':i.produto,'quantidade':i.quantidade})

        context = {
            'estoque':lista_estoque
        }
        return render(request,'estoque/estoque.html',context=context)


def FiltrarEstoque(request):
    produto = request.GET.get('search')
    produtos_filtrados = Estoque.objects.filter(produto__nome__icontains=produto)
    return render(request,'estoque/estoque.html',{'estoque':produtos_filtrados})




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




def AdicionarBaixa(request):
    try:
        quantidade = request.POST.get('quantidade')
        produto_selecionado = request.POST.get('produto')
        produto = Estoque.objects.get(produto=int(produto_selecionado))
        estoque_atualizado = int(produto.quantidade) - int(quantidade)
        produto = Estoque.objects.filter(produto_id=int(produto_selecionado)).update(quantidade=estoque_atualizado)
        usuario = request.user
        movimentacao = Movimentacao_estoque(usuario=usuario,produto=Produtos.objects.get(id=produto_selecionado),quantidade=quantidade,tipo='Saída')
        movimentacao.save() 
        return redirect('ListarEstoque')
    except Exception:
        messages.error(request,f'Selecione um produto!')
        return redirect('ListarEstoque')



def ListarMovimentacoes(request):
    return render(request,'estoque/movimentacoes.html',{'movimentacoes':Movimentacao_estoque.objects.all().order_by('-data'),'usuarios':User.objects.all()})


def FiltrarMovimentacoes(request):
    data_inicio = request.GET.get('data_inicio')
    data_final = request.GET.get('data_final')
    usuario = request.GET.get('usuario')
    tipo = request.GET.get('botao_tipo')
    if data_inicio and data_final:
        movimentacoes_filtradas = Movimentacao_estoque.objects.filter(data__range=(data_inicio,data_final))

    if usuario:
        movimentacoes_filtradas = Movimentacao_estoque.objects.filter(usuario__username__icontains=(usuario))
        print(movimentacoes_filtradas)
    
    if tipo:
        movimentacoes_filtradas = Movimentacao_estoque.objects.filter(tipo__icontains=(tipo))
    
    return render(request, 'estoque/movimentacoes.html', {'movimentacoes': movimentacoes_filtradas,'usuarios':User.objects.all()})