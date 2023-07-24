from django.shortcuts import render,redirect
from produtos.models import Produtos
from .models import Compra,ItemCompra
from colaboradores.models import Colaboradore
from datetime import datetime
from django.views.decorators.http import require_GET
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.contrib import messages
from hashlib import md5
from django.core.mail import send_mail,EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from estoque.models import Estoque
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from reportlab.lib import colors
from django.db.models import Q
from django.contrib.auth.decorators import login_required




lista_carrinho = []

def DeletarItem(request,id):
    for produto in lista_carrinho:
        if produto['id'] == id:
            lista_carrinho.remove(produto)
            break
    return redirect('Carrinho')


def Conferir_estoque(carrinho:list,id):
    cont = 0
    for i in carrinho:
        if i['id'] == id:
            cont += 1
    try:
        estoque = Estoque.objects.get(produto=id)
        if cont >= estoque.quantidade:
            return False
        else:
            return True
    except Exception as erro:
        print(erro)





def AdicionarItem(request):
    if request.method == 'POST':
        input_codbarras = request.POST.get('valores[]')
        input_codbarras = input_codbarras.replace('-','').replace('_','')
        lista_cods = Produtos.objects.values_list('cod_barras',flat=True)
        try:
            if int(input_codbarras) in lista_cods:
                produto = Produtos.objects.get(cod_barras=int(input_codbarras))
                if produto.situacao == True:
                    if Conferir_estoque(lista_carrinho,produto.id):
                        lista_carrinho.append({'produto':produto.nome, 'preco':produto.preco,'id':produto.id})
                        return redirect('Carrinho')
                    else:
                        raise Exception('Produto não disponível em estoque!')
                else:
                    raise Exception('Produto inativo!')
            
            else:
                raise Exception('Código de barras inválido!')
        except Exception as erro:
            messages.error(request,f'{erro}')
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
                        EnviarEmailIngresso(lista_ingressos,f'{user.nome}',sum(dicionario['total'] for dicionario in lista_ingressos))

                if roupa:
                        EnviarEmailRoupa(lista_roupas,f'{user.nome}',sum(dicionario['total'] for dicionario in lista_roupas))

                EnviarEmailColaborador(f'{user.email}',itens_da_compra,f'{user.nome}',soma)
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




@login_required(login_url='Login')
def GerarRelatorio(request):
    if request.method == 'GET':
        return render(request, 'relatorios/relatorios.html',{'colaboradores':Colaboradore.objects.all().order_by('nome')})
    elif request.method == 'POST':
        data_inicio = request.POST.get('data_inicio')
        data_fim = request.POST.get('data_final')

        colaborador = request.POST.get('colaborador')


        if colaborador is not None:
            compras_filtradas = Compra.objects.filter(Q(data__range=(data_inicio,data_fim)) & Q(colaborador__cpf__icontains=colaborador)).order_by('-data')
        else:
            compras_filtradas = Compra.objects.filter(data__range=(data_inicio,data_fim)).order_by('-data')
        try:    
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="relatorio_compras.pdf"'

            # Criação do documento PDF
            doc = SimpleDocTemplate(response, pagesize=letter)


            # Criação da tabela
            dados = []

            dados.append(['Compra', 'Nome', 'Data', 'Itens', 'Quantidade', 'Preço Unit.', 'Total'])

            for item in compras_filtradas:
                itens_compra = ItemCompra.objects.filter(compra=item.id)
                for itens in itens_compra:
                    dados.append([item.id, item.colaborador, item.data.strftime('%d/%m/%Y %H:%M'), itens.produto.nome, itens.quantidade, f' R$ {itens.preco_unitario}', f'R$ {itens.total} '])

            table = Table(dados, colWidths=[50, 100, 80, 145, 65, 75, 75])

            # Estilo da tabela
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ])
            table.setStyle(style)

            # Adiciona a tabela ao documento
            elementos = [table]
            doc.build(elementos)

            return response

        except Exception as e:
            print(f'{e}')
            return redirect('GerarRelatorio')


def EnviarEmailColaborador(destinatario,itens_da_compra:list,colaborador,soma):
        html_content = render_to_string('compras/template_email.html', {'produtos': itens_da_compra,'colaborador':colaborador,'total':soma,'data':timezone.now})
        pdf = 'relatorio_de_compra.pdf'
        HTML(string=html_content).write_pdf(pdf)
        email_compra = EmailMessage(
            'Compra realizada na conveniência!',
            'Segue em anexo os detalhes da sua compra!\n\nAtt, Conveniência SCI!',
            'testeacademia@sci.com.br',
            [f'{destinatario}']
)
        with open(pdf, 'rb') as f:
            email_compra.attach('relatorio_de_compra.pdf', f.read(), 'application/pdf')
        email_compra.send()



def EnviarEmailIngresso(lista_ingressos:list,colaborador,soma):
    html_content = render_to_string('compras/template_email_ingressos.html', {'produtos': lista_ingressos,'colaborador':colaborador,'total':soma,'data':timezone.now})
    email_ingresso = EmailMessage(
        'Compra de ingresso realizada na conveniência!',
        html_content,
        'testeacademia@sci.com.br',
        ['gabriel_michelmann@estudante.sc.senai.br'],
    )
    email_ingresso.content_subtype = 'html'
    email_ingresso.send()


def EnviarEmailRoupa(lista_roupas:list,colaborador,soma):
    html_content = render_to_string('compras/template_email_roupas.html', {'produtos': lista_roupas,'colaborador':colaborador,'total':soma,'data':timezone.now})
    email_ingresso = EmailMessage(
        'Compra de roupas realizada na conveniência!',
        html_content,
        'testeacademia@sci.com.br',
        ['gabriel_michelmann@estudante.sc.senai.br'],
    )
    email_ingresso.content_subtype = 'html'
    email_ingresso.send()


