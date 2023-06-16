import datetime
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_GRNs import *
from ..Serializer.S_Orders import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Invoices import *
from ..Serializer.S_Bom import *
from ..Serializer.S_Dashboard import *
from ..models import *
from django.db.models import *

class DashBoardView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_Invoices.objects.filter(Party_id = id, InvoiceDate = date.today()).count()
                query1 = T_GRNs.objects.filter(Customer_id = id,GRNDate = date.today()).count()
                query2 = T_Orders.objects.filter(Supplier_id = id, OrderDate = date.today()).count()
                Invoice_list = list() 
                Invoice_list.append({
                        "OrderCount": query2,
                        "GRNsCount": query1,
                        "InvoiceCount": query
                    })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Invoice_list[0]})
                
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})