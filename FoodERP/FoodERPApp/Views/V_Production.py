
from datetime import date
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Views.V_TransactionNumberfun import SystemBatchCodeGeneration

from ..Serializer.S_Production import *

from ..models import *


class ProductionformMaterialIssue(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIssueIDdata = JSONParser().parse(request)
                MaterialIssueID = MaterialIssueIDdata['MaterialIssueID']
                query1 = T_MaterialIssue.objects.filter(id=MaterialIssueID)
                MaterialIssue_Serializer=H_ProductionSerializer2(query1,many=True).data
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': '', 'Data':MaterialIssue_Serializer})
        except Exception as e  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e , 'Data':[]}) 

class ProductionFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Productiondata = JSONParser().parse(request)
                FromDate = Productiondata['FromDate']
                ToDate = Productiondata['ToDate']
                
                query1 = T_Production.objects.filter(ProductionDate__range=[FromDate,ToDate])
                
                Production_Serializer = H_ProductionSerializerforGET(query1, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Production_Serializer.data })
                
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})
         

class ProductionView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Productiondata = T_Production.objects.all()
                if Productiondata.exists():
                    Production_Serializer = H_ProductionSerializerforGET(
                    Productiondata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Production_Serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Production Not available', 'Data': []})    
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})
         

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Productiondata = JSONParser().parse(request)
                Customer = Productiondata['Division']
                Item = Productiondata['Item']
                
                query1 = T_Production.objects.filter(Item_id=Item, BatchDate=date.today()).values('id')
                BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(Item, Customer, query1.count())

                Productiondata['BatchCode'] = BatchCode
                Productiondata['BatchDate'] = date.today()
                O_BatchWiseLiveStockList=list()
                O_BatchWiseLiveStockList.append({
                    "Item": Productiondata['Item'],
                    "Quantity": Productiondata['ActualQuantity'],
                    "Unit": Productiondata['Unit'],
                    "BaseUnitQuantity": Productiondata['ActualQuantity'],
                    "MRP": Productiondata['MRP'],
                    "Rate": Productiondata['Rate'],
                    "GST": Productiondata['GST'],
                    "Party": Customer,
                    "SystemBatchDate": Productiondata['BatchDate'],
                    "SystemBatchCode": Productiondata['BatchCode'],
                    "BatchDate": Productiondata['BatchDate'],
                    "BatchCode": Productiondata['SupplierBatchCode'],
                    "CreatedBy":Productiondata['CreatedBy'],
                    
                    })

                # print(GRNdata)
                Productiondata.update({"O_BatchWiseLiveStockItems":O_BatchWiseLiveStockList}) 
                
                Production_Serializer = H_ProductionSerializer(data=Productiondata)
                if Production_Serializer.is_valid():
                    Production_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Production_Serializer.errors, 'Data': []})
        except Exception as e  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e , 'Data':[]})       

class ProductionViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Productiondata = T_Production.objects.get(id=id)
                Production_Serializer = H_ProductionSerializerforGET(Productiondata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Production_Serializer.data})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})
           

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Productiondata = JSONParser().parse(request)
                ProductiondataByID = T_Production.objects.get(id=id)
                Production_Serializer = H_ProductionSerializer(ProductiondataByID, data=Productiondata)
                if Production_Serializer.is_valid():
                    Production_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Production_Serializer.errors,'Data' :[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})            

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Productiondata = T_Production.objects.get(id=id)
                Productiondata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production  Deleted Successfully', 'Data':[]})
        except H_Modules.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Module Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Production used in another table', 'Data': []})    