
from datetime import date
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *
from ..Views.V_TransactionNumberfun import SystemBatchCodeGeneration
from ..Serializer.S_Production import *
from ..models import *         

class MaterialIssueDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                MaterialIssueIDdata = JSONParser().parse(request)
                MaterialIssueID = MaterialIssueIDdata['MaterialIssueID']
                query1 = T_MaterialIssue.objects.filter(id=MaterialIssueID)
                MaterialIssue_Serializer=H_ProductionSerializer2(query1,many=True).data
                return JsonResponse({'StatusCode':200, 'Status': True, 'Message': '', 'Data':MaterialIssue_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class ProductionList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Productiondata = JSONParser().parse(request)
                FromDate = Productiondata['FromDate']
                ToDate = Productiondata['ToDate']
                query = T_Production.objects.filter(ProductionDate__range=[FromDate,ToDate])
                if query:
                    Production_Serializer = H_ProductionSerializerforGET(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Production_Serializer})  
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
            

class ProductionView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
   
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Productiondata = JSONParser().parse(request)
                Customer = Productiondata['Division']
                Item = Productiondata['Item']
                
                query1 = T_Production.objects.filter(Item_id=Item, BatchDate=date.today()).values('id')
                
                BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(Item, Customer, query1.count())
                
                BaseUnitQuantity=UnitwiseQuantityConversion(Item,Productiondata['ActualQuantity'],Productiondata['Unit'],0,0,0,1).GetBaseUnitQuantity()
                
                Gst = GSTHsnCodeMaster(Item, Productiondata['ProductionDate']).GetTodaysGstHsnCode()
                GSTID = Gst[0]['Gstid']

                Productiondata['BatchCode'] = BatchCode
                Productiondata['BatchDate'] = date.today()
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                O_BatchWiseLiveStockList.append({
                    "Item": Productiondata['Item'],
                    "Quantity": Productiondata['ActualQuantity'],
                    "Unit": Productiondata['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Customer,
                    "CreatedBy":Productiondata['CreatedBy'],
                    
                    
                    })

                O_LiveBatchesList.append({
                    
                    "MRP": Productiondata['MRP'],
                    "Rate": Productiondata['Rate'],
                    "GST": GSTID,
                    "SystemBatchDate": Productiondata['BatchDate'],
                    "SystemBatchCode": Productiondata['BatchCode'],
                    "BatchDate": Productiondata['BatchDate'],
                    "BatchCode": Productiondata['PrintedBatchCode'],
                    "ItemExpiryDate":Productiondata['BestBefore'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList                   
                    
                    })    

                # print(GRNdata)
                Productiondata.update({"O_LiveBatchesList":O_LiveBatchesList}) 
                
                Production_Serializer = H_ProductionSerializer(data=Productiondata)
                if Production_Serializer.is_valid():
                    Production_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Production_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})       

class ProductionViewSecond(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Productiondata = T_Production.objects.get(id=id)
                Production_Serializer = H_ProductionSerializerforGET(Productiondata)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Production_Serializer.data})
        except T_Production.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Production Not available', 'Data': []})
           

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                O_BatchWiseLiveStockData = O_BatchWiseLiveStock.objects.filter(Production_id=id).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Production Quantity Used in another Transaction', 'Data': []})  
                Productiondata = T_Production.objects.get(id=id)
                Productiondata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production  Deleted Successfully', 'Data':[]})
        except T_Production.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Production Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Production used in another table', 'Data': []})    