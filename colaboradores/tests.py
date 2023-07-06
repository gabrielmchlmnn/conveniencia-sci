from django.test import TestCase
# from compras import models
# from .models import Colaboradore
# from datetime import datetime

# # Create your tests here.

# hoje = datetime.now()
# ultimo_26 = datetime(hoje.year, hoje.month, 26)
# maiores_compradores = models.Compra.objects.exclude(data__lte=ultimo_26).values('colaborador_id').annotate(total_compras=Round(Sum('total'),2)).order_by('-total_compras')   
# for i in maiores_compradores:
#     i['colaborador_id'] = Colaboradore.objects.get(id=i['colaborador_id'])
#     total_compras_formatado = '{:.2f}'.format(i['total_compras'])
#     i['total_compras'] = total_compras_formatado
#     print(i['total_compras'],i['colaborador_id'])

# quantidade_compras = models.Compra.objects.exclude(data__lte=ultimo_26).count()
# dois_meses_atras = hoje.replace(day=26, month=hoje.month-2)
# dia_25_mes_passado = hoje.replace(day=25, month=hoje.month-1)
# if hoje.day > 25:
#     dois_meses_atras = hoje.replace(day=26, month=hoje.month-1)
#     dia_25_mes_passado = hoje.replace(day=25)
    
# quantidade_compras_ultima_ref = models.Compra.objects.filter(data__gte=dois_meses_atras,data__lte = dia_25_mes_passado).count()


# print(quantidade_compras,quantidade_compras_ultima_ref)