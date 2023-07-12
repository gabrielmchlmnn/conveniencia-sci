from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from produtos.models import Produtos
from .models import Compra,ItemCompra
from colaboradores.models import Colaboradore
from datetime import datetime
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from fpdf import FPDF
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.contrib import messages
from hashlib import md5
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from reportlab.pdfgen import canvas
from weasyprint import HTML
from estoque.models import Estoque
from django.utils import timezone

lista_carrinho = []




def DeletarItem(request,id):
    for produto in lista_carrinho:
        if produto['id'] == id:
            lista_carrinho.remove(produto)
            break
    return redirect('Carrinho')



def AdicionarItem(request):
    if request.method == 'POST':
        input_codbarras = request.POST.get('valores[]')
        lista_cods = Produtos.objects.values_list('cod_barras',flat=True)
        if int(input_codbarras) in lista_cods:
            produto = Produtos.objects.get(cod_barras=int(input_codbarras))
            if produto.situacao == True:
                lista_carrinho.append({'produto':produto.nome, 'preco':produto.preco,'id':produto.id})
                return redirect('Carrinho')
            else:
                messages.error(request,'Produto inativado!')
                return redirect('Carrinho')
        
        else:
            messages.error(request,'Código de barras inválido!')
            return redirect('Carrinho')
    else:
       return render(request,'compras/registrar_compra.html')
    

def DescontarEstoque(nmr_produto:int,quantidade_descontada):
    produto = Estoque.objects.get(produto=int(nmr_produto))
    Estoque.objects.filter(id=int(nmr_produto)).update(quantidade=produto.quantidade-quantidade_descontada)
    



def RegistrarCompra(request):
    soma = 0
    ingresso = False
    roupa = False
    lista_ingressos = []
    lista_roupas = []
    usuario = request.POST.get('login')
    senha = request.POST.get('senha')
    senha = str(senha).encode('utf8')
    user = Colaboradore.objects.filter(login=usuario,senha=md5(senha).hexdigest())
    global lista_carrinho
    for i in lista_carrinho:
        soma += i['preco'] 
    if user:
        user = Colaboradore.objects.get(login=usuario)
        mensal = 0
        data = datetime.now()
        print(data)
        user = Colaboradore.objects.get(login=usuario)
        ultimo_26 = datetime(data.year, data.month, 26)
        hoje = datetime.now().date()
        dois_meses_atras = hoje.replace(day=26, month=hoje.month-2)
        dia_25_mes_passado = hoje.replace(day=25, month=hoje.month-1)
        if hoje.day > 25:
            dois_meses_atras = hoje.replace(day=26, month=hoje.month-1)
            dia_25_mes_passado = hoje.replace(day=25)

        if dois_meses_atras.month == 12 or dois_meses_atras.month == 11:
            dois_meses_atras = dois_meses_atras.replace(year=dois_meses_atras.year-1)

        if user.situacao == True:
                nova_compra = Compra.objects.create(colaborador=Colaboradore.objects.get(login=usuario),total=soma)
                nova_compra.save()

                carrinho_quantidades = {}
                lista_ids = []
                for produto in lista_carrinho:
                    produto_id = produto['id']
                    lista_ids.append(produto_id)
                    if produto_id in carrinho_quantidades:
                        carrinho_quantidades[produto_id] += 1
                    else:
                        carrinho_quantidades[produto_id] = 1
                itens_da_compra = []
                cont = 0
                for produto_id, quantidade in carrinho_quantidades.items():
                    produto = Produtos.objects.get(id=int(produto_id))
                    if produto.tipo == 'Ingresso':
                        ingresso = True
                        lista_ingressos.append({'nome':produto.nome,'preco':produto.preco,'quantidade':quantidade,'total':quantidade*produto.preco})
                    elif produto.tipo == 'Roupa':
                        roupa = True
                        lista_roupas.append({'nome':produto.nome,'preco':produto.preco,'quantidade':quantidade,'total':quantidade*produto.preco})
                    else:
                        DescontarEstoque(int(produto_id),quantidade)
                    item_compra = ItemCompra(compra=nova_compra, produto_id=produto_id, quantidade=quantidade,preco_unitario=produto.preco,total=quantidade*produto.preco)
                    item_compra.save()
                    cont +=1
                    itens_da_compra.append({'nome':produto.nome,'preco':float(produto.preco),'quantidade':quantidade,'total':quantidade*produto.preco,'cod_barras':produto.cod_barras})

                
                gastos = Compra.objects.filter(data__range=(dois_meses_atras,dia_25_mes_passado)).filter(colaborador_id=user.id).values_list('total',flat=True)
                ultima_referencia = sum(gastos)
                gastos = Compra.objects.exclude(data__gte=ultimo_26).filter(colaborador_id=user.id).values_list('total',flat=True)
                mensal = sum(gastos)
                lista_carrinho = []
                context = {
                    'aviso':'aviso','colaborador':user.nome,'total':soma,'ultima_ref':ultima_referencia,'mensal':mensal
                }


                if ingresso:
                            html_content = render_to_string('compras/template_email_ingressos.html', {'produtos': lista_ingressos,'colaborador':user.nome,'total':sum(dicionario['total'] for dicionario in lista_ingressos),'data':timezone.now,'quantos':len(lista_ingressos)})
                            email_ingresso = EmailMessage(
                                'Compra de ingresso realizada na conveniência!',
                                html_content,
                                'testeacademia@sci.com.br',
                                ['gabriel_michelmann@estudante.sc.senai.br'],
                            )
                            email_ingresso.content_subtype = 'html'
                            email_ingresso.send()

                if roupa:
                        html_content = render_to_string('compras/template_email_roupas.html', {'produtos': lista_roupas,'colaborador':user.nome,'total':sum(dicionario['total'] for dicionario in lista_roupas),'data':timezone.now,'quantos':len(lista_roupas)})
                        email_ingresso = EmailMessage(
                            'Compra de roupas realizada na conveniência!',
                            html_content,
                            'testeacademia@sci.com.br',
                            ['gabriel_michelmann@estudante.sc.senai.br'],
                        )
                        email_ingresso.content_subtype = 'html'
                        email_ingresso.send()

                html_content = render_to_string('compras/template_email.html', {'produtos': itens_da_compra,'colaborador':user.nome,'total':soma,'data':timezone.now})
                pdf = 'relatorio_de_compra.pdf'
                HTML(string=html_content).write_pdf(pdf)
                email_compra = EmailMessage(
                    'Compra realizada na conveniência!',
                    'Segue em anexo os detalhes da sua compra!\n\nAtt, Conveniência SCI!',
                    'testeacademia@sci.com.br',
                    ['michelmanngabriel@gmail.com']
)
                with open(pdf, 'rb') as f:
                    email_compra.attach('relatorio_de_compra.pdf', f.read(), 'application/pdf')
                email_compra.send()
                return render(request,'compras/registrar_compra.html',context=context)
        else:
            messages.error(request,'Colaborador desligado!Consulte o RH.')
            return redirect('Carrinho')

    else:
        messages.error(request,'Login inválido!!')
        return redirect('Carrinho')


def Carrinho(request):
    totalCarrinho = 0
    for i in lista_carrinho:
        totalCarrinho += i['preco']
    return render(request,'compras/registrar_compra.html',{'itens':lista_carrinho,'totalCarrinho':totalCarrinho})



def ComecarCompra(request):
    global lista_carrinho
    lista_carrinho = []
    return render(request,'compras/registrar_compra.html')
    

def ConferirGastos(request):
    usuario = request.POST.get('login')
    senha = request.POST.get('senha')
    senha = str(senha).encode('utf8')

    user = Colaboradore.objects.filter(login=usuario,senha=md5(senha).hexdigest())
    soma = 0
    for i in lista_carrinho:
        soma += i['preco'] 
    if user:
        data = datetime.now()
        user = Colaboradore.objects.get(login=usuario)
        ultimo_26 = datetime(data.year, data.month, 26)
        hoje = datetime.now()
        dois_meses_atras = hoje.replace(day=26, month=hoje.month-2)
        dia_25_mes_passado = hoje.replace(day=25, month=hoje.month-1)

        if hoje.day > 25:
            dois_meses_atras = hoje.replace(day=26, month=hoje.month-1)
            dia_25_mes_passado = hoje.replace(day=25)

        if dois_meses_atras.month == 12:
            dois_meses_atras = dois_meses_atras.replace(year=dois_meses_atras.year-1)

        gastos = Compra.objects.filter(data__range=(dois_meses_atras,dia_25_mes_passado)).filter(colaborador_id=user.id).values_list('total',flat=True)
        ultima_referencia = sum(gastos)
        gastos = Compra.objects.exclude(data__gte=ultimo_26).filter(colaborador_id=user.id).values_list('total',flat=True)
        mensal = sum(gastos)
        context = {
            'aviso2':'aviso2','colaborador':user.nome,'ultima_ref':ultima_referencia,'mensal':mensal,'totalCarrinho':soma,'itens':lista_carrinho
            }
        return render(request,'compras/registrar_compra.html',context=context)

    else:
        messages.error(request,'Login inválido!')
        return redirect('Carrinho')





from reportlab.pdfgen import canvas

def GerarRelatorio(request):
    if request.method == 'GET':
        return render(request, 'relatorios/relatorios.html')
    elif request.method == 'POST':
        print('a')
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_final')
        try:
            compras_filtradas = Compra.objects.filter(data__range=(data_inicio,data_fim)).order_by('-colaborador_id')

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_compras.pdf"'

            p = canvas.Canvas(response, pagesize=letter)
            y = 700

            MAX_ITENS_POR_PAGINA = 7  # Número máximo de itens por página
            itens_processados = 0  # Contador de itens processados

            print('b')
            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y+30, "Relatório de Compras")
            p.setFont("Helvetica", 12)

            for compra in compras_filtradas:
                itens_compra = ItemCompra.objects.filter(compra=compra)
                lista_itens = []
                for item in itens_compra:
                    lista_itens.append({'produto':item.produto,'quantidade':item.quantidade,'total':item.total})

                if itens_processados % MAX_ITENS_POR_PAGINA == 0:
                    if itens_processados != 0:
                        p.showPage()  # Finaliza a página atual antes de criar uma nova

                    y = 700  # Reinicia a posição vertical para o início da nova página

                p.drawString(50, y - 20, f"Data: {compra.data.strftime('%d/%m/%Y %H:%M:%S')}")
                p.drawString(50, y - 40, f"Total: R$ {compra.total}")
                p.drawString(50, y - 60, f"Colaborador: {compra.colaborador.nome}")

                p.drawString(50, y - 80, "Itens:")
                y -= 100

                for item in lista_itens:
                    p.drawString(50, y, f"Produto: {item['produto'].nome}")
                    p.drawString(50, y - 20, f"Quantidade: {item['quantidade']}")
                    p.drawString(50, y - 40, f"Total: {item['total']}")

                    y -= 60

                p.drawString(50, y - 20, "----------------------------------------")
                y -= 40

                itens_processados += 1

            print('c')
            if itens_processados % MAX_ITENS_POR_PAGINA != 0:
                p.showPage()  # Finaliza a última página caso não esteja completa
            p.save()

            return response

        except Exception as e:
            return redirect('GerarRelatorio')



def Compras(request):
    context= {
        'compras':Compra.objects.all()
    }
    return render(request,'compras/compras.html',context=context)

def Deletar_compra(request,id):
    compra_excluida = Compra.objects.filter(id=id).delete()
    context= {
        'compras':Compra.objects.all()
    }
    return render(request,'compras/compras.html',context=context)
