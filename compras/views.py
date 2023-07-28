from django.shortcuts import render,redirect
from produtos.models import Produtos
from .models import Compra,ItemCompra
from colaboradores.models import Colaboradore
from datetime import datetime
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.contrib import messages
from hashlib import md5
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from estoque.models import Estoque
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph,Spacer
from reportlab.lib import colors
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib.styles import getSampleStyleSheet
import cv2
from pyzbar.pyzbar import decode



def limpar_cache_sessao(request):
    chaves = list(request.session.keys())  
    for chave in chaves:
        if chave != '_auth_user_id' and chave != '_auth_user_backend' and chave != '_auth_user_hash':
            del request.session[chave] 


def Voltar(request):
    limpar_cache_sessao(request)
    return redirect('ComecarCompra')


def DeletarItem(request, id):
    carrinho = request.session.get('carrinho',[])
    for produto in carrinho:
        if produto['id'] == id:
            carrinho.remove(produto)
            break

    request.session['carrinho'] = carrinho  
    if len(carrinho) < 1:
        limpar_cache_sessao(request)
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

        carrinho = request.session.get('carrinho', [])
        try:
            if int(input_codbarras) in lista_cods:
                produto = Produtos.objects.get(cod_barras=int(input_codbarras))
                if produto.situacao == "Ativo":
                    if Conferir_estoque(carrinho,produto.id):
                        carrinho.append({'produto':produto.nome, 'preco':float(produto.preco),'id':produto.id})
                        request.session['carrinho'] = carrinho
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
    carrinho = request.session.get('carrinho')
    for i in carrinho:
        soma += i['preco'] 
    if user:
        user = Colaboradore.objects.get(login=usuario)
        mensal = 0
        data = datetime.now()
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

        if user.situacao == "Ativo":
                nova_compra = Compra.objects.create(colaborador=Colaboradore.objects.get(login=usuario),total=soma)
                nova_compra.save()

                carrinho_quantidades = {}
                lista_ids = []
                for produto in carrinho:
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
                gastos = Compra.objects.exclude(data__lte=ultimo_26).filter(colaborador_id=user.id).values_list('total',flat=True)
                mensal = sum(gastos)
                context = {
                    'aviso':'aviso','colaborador':user.nome,'total':soma,'ultima_ref':f"{float(ultima_referencia):,.2f}".replace(',', '|').replace('.', ',').replace('|', '.'),'mensal':f"{float(mensal):,.2f}".replace(',', '|').replace('.', ',').replace('|', '.')
                }

                if ingresso:
                        EnviarEmailIngresso(lista_ingressos,f'{user.nome}',sum(dicionario['total'] for dicionario in lista_ingressos))

                if roupa:
                        EnviarEmailRoupa(lista_roupas,f'{user.nome}',sum(dicionario['total'] for dicionario in lista_roupas))

                EnviarEmailColaborador(f'{user.email}',itens_da_compra,f'{user.nome}',soma,f'{timezone.now}')
                limpar_cache_sessao(request)
                return render(request,'compras/registrar_compra.html',context=context)
        else:
            messages.error(request,'Colaborador desligado!Consulte o RH.')
            return redirect('Carrinho')

    else:
        messages.error(request,'Login inválido!!')
        return redirect('Carrinho')


def Carrinho(request):
    totalCarrinho = 0
    carrinho = request.session.get('carrinho',[])
    if len(carrinho) > 0:
        for i in carrinho:
            totalCarrinho += i['preco']
    totalCarrinho = f"{totalCarrinho:,.2f}".replace(',', '|').replace('.', ',').replace('|', '.')
    return render(request,'compras/registrar_compra.html',{'itens':carrinho,'totalCarrinho':totalCarrinho})


def ComecarCompra(request):
    limpar_cache_sessao(request)
    return render(request,'compras/registrar_compra.html')

def Ligar_camera():
    cap = cv2.VideoCapture(0)

    # Verificar se a câmera foi aberta corretamente
    if not cap.isOpened():
        raise Exception("Falha ao acessar a câmera. Verifique se ela está disponível.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                continue

            # Mostrar a imagem ao vivo no navegador (opcional, apenas para depuração)
            cv2.imshow("Camera", frame)

            # Tente decodificar o código de barras da imagem
            barcodes = decode(frame)
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                print("Código de barras encontrado:", barcode_data)

            # Pressione a tecla 'q' para sair do loop e encerrar a captura
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Libere os recursos da câmera
        cap.release()
        cv2.destroyAllWindows()

def ConferirGastos(request):
    usuario = request.POST.get('login')
    senha = request.POST.get('senha')
    senha = str(senha).encode('utf8')

    user = Colaboradore.objects.filter(login=usuario,senha=md5(senha).hexdigest())
    soma = 0
    carrinho = request.session.get('carrinho')
    try:
        if carrinho is not None:
            for i in carrinho:
                soma += i['preco'] 
        if user:
            data = datetime.now()
            user = Colaboradore.objects.get(login=usuario)
            if user.situacao == "Inativo":
                raise Exception('Colaborador desligado!Consulte o RH.')
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
            gastos = Compra.objects.exclude(data__lte=ultimo_26).filter(colaborador_id=user.id).values_list('total',flat=True)
            mensal = sum(gastos)
            context = {
                'aviso2':'aviso2','colaborador':user.nome,'ultima_ref':f"{float(ultima_referencia):,.2f}".replace(',', '|').replace('.', ',').replace('|', '.'),'mensal':f"{float(mensal):,.2f}".replace(',', '|').replace('.', ',').replace('|', '.'),'totalCarrinho':soma,'itens':carrinho
                }
            return render(request,'compras/registrar_compra.html',context=context)
        else:
            raise Exception('Login inválido!')
    except Exception as erro:
        messages.error(request,f'{erro}')
        return redirect('Carrinho')



def ativar_camera(request):
    # Inicializar a câmera (use o índice correto para selecionar a câmera apropriada)
    cap = cv2.VideoCapture(0)

    # Verificar se a câmera foi aberta corretamente
    if not cap.isOpened():
        print('erro')
        raise Exception("Falha ao acessar a câmera. Verifique se ela está disponível.")

    # Loop para capturar uma imagem da câmera
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        # Mostrar a imagem ao vivo no navegador (opcional, apenas para depuração)
        cv2.imshow("Camera", frame)
        
        # Pressione a tecla 'q' para sair do loop e capturar a imagem
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

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
            if data_inicio > data_fim:
                raise Exception ('A data de início não pode ser maior que a data final!')
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
                    dados.append([item.id, item.colaborador, item.data.strftime('%d/%m/%Y %H:%M'), itens.produto.nome, itens.quantidade, f" R$ ","{{:,.2f}.format(itens.preco_unitario)}", f'R$ {itens.total} '])

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
            messages.error(request,f'{e}')
            return redirect('GerarRelatorio')


def EnviarEmailColaborador(destinatario,itens_da_compra:list,colaborador,soma,data):
        
            # Definir o nome do arquivo PDF
    nome_arquivo = "compra.pdf"

    # Configurar o tamanho da página (usando o estilo "letter")
    pdf = SimpleDocTemplate(nome_arquivo, pagesize=letter)

    # Lista para armazenar os elementos do PDF
    elementos = []

    # Estilos para o texto
    estilos = getSampleStyleSheet()
    estilo_titulo = estilos["Heading1"]
    estilo_subtitulo = estilos["Heading3"]
    estilo_paragrafo = estilos["Normal"]
    data = timezone.now()
    # Criar o conteúdo do PDF
    preco_formatado = '{:,.2f}'.format(soma)
    titulo = Paragraph(f"Olá colaborador {colaborador}!", estilo_titulo)
    subtitulo = Paragraph("Confira abaixo os dados da sua compra!", estilo_subtitulo)
    data_compra = Paragraph(f"Data: {data.strftime('%d/%m/%Y %H:%M')}", estilo_paragrafo)
    total_compra = Paragraph(f"Total: R$ {preco_formatado}", estilo_paragrafo)

    # Montar a tabela de produtos
    dados_tabela = [["Nome do produto", "Preço", "Quantidade", "Total"]]
    for produto in itens_da_compra:
        preco_formatado = '{:,.2f}'.format(produto['preco'])
        dados_tabela.append([produto["nome"], f"R$ {preco_formatado}", produto["quantidade"], f"R${produto['total']}"])

    # Definir o estilo da tabela
    estilo_tabela = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.darkblue),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.aliceblue),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (0, 1), (-1, -1), colors.aliceblue),
    ])

    # Criar a tabela
    tabela = Table(dados_tabela)
    tabela.setStyle(estilo_tabela)
    espaco_vazio = Spacer(1, 50)
    # Adicionar os elementos ao PDF
    elementos.append(titulo)
    elementos.append(subtitulo)
    elementos.append(data_compra)
    elementos.append(total_compra)
    elementos.append(espaco_vazio)
    elementos.append(tabela)

    # Construir o PDF
    pdf.build(elementos)

    email_compra = EmailMessage(
        'Compra realizada na conveniência!',
        'Segue em anexo os detalhes da sua compra!\n\nAtt, Conveniência SCI!',
        'testeacademia@sci.com.br',
        [f'{destinatario}']
)
    with open('compra.pdf', 'rb') as pdf_file:
        mime_base = MIMEBase('application', 'pdf')
        mime_base.set_payload(pdf_file.read())
        encoders.encode_base64(mime_base)
        mime_base.add_header('Content-Disposition', 'attachment', filename='compra.pdf')

    email_compra.attach(mime_base)

    # Enviar o e-mail
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


