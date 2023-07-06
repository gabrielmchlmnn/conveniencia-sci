from django.shortcuts import render,redirect
from .models import Produtos
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse

# Create your views here.


@login_required(login_url='Login')
def AdicionarProdu(request):
        
        nome = request.POST.get('nome')
        cod_barras = request.POST.get('cod_barras')
        preco = request.POST.get('preco')
        tipo = request.POST.get('tipo')
        lista_cods = Produtos.objects.values_list('cod_barras',flat=True)
        if int(cod_barras) not in lista_cods:
            novo_produto = Produtos(nome=nome,cod_barras=int(cod_barras),preco=preco,tipo=tipo)
            novo_produto.save()
            return redirect('ListarProdu')
        else:
            messages.error(request,'Código de barras já cadastrado!')
            return redirect('ListarProdu')




@login_required(login_url='Login')
def EditarProdu(request,id):
    produto = Produtos.objects.get(id=id)
    if request.method == 'POST':
        nome = request.POST.get('nome')
        cod_barras = request.POST.get('cod_barras')
        preco = request.POST.get('preco')
        tipo = request.POST.get('tipo')
        lista_cods = Produtos.objects.exclude(id=id).values_list('cod_barras',flat=True)
        if int(cod_barras) not in lista_cods:
            Produtos.objects.filter(id=id).update(nome=nome,cod_barras=int(cod_barras),preco=preco,tipo=tipo)
            return redirect('ListarProdu')
        else:
            messages.error(request,'Código de barras já cadastrado!')
            url = reverse('EditarProdu',args=[produto.id])
            return redirect(url)
        
    else:  
        context = {
        "nome":produto.nome,'cod_barras':produto.cod_barras,'preco':produto.preco,'id':produto.id,'tipo':produto.tipo
        }
        return render(request,'produtos/editar_produ.html',context=context)
    

@login_required(login_url='Login')
def ListarProdu(request):
    context = {
        'produto':Produtos.objects.all()
    }
    return render(request,'produtos/listar_produ.html',context=context)

@login_required(login_url='Login')
def FiltrarProdu(request):
    if request.method == 'GET':
        search_term = request.GET.get('search')
        produtos_filtrados = Produtos.objects.filter(nome__icontains=search_term)
        return render(request, 'produtos/listar_produ.html', {'produto': produtos_filtrados})