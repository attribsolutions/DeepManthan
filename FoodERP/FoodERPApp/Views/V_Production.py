
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
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix       
from django.db.models import F, ExpressionWrapper, DecimalField,OuterRef, Subquery
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
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        

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
                DivisionID=Productiondata['Party']
                bom_subquery = M_BillOfMaterial.objects.filter(Item_id=OuterRef('Item_id'),IsDelete=0).values('EstimatedOutputQty')
                query = T_Production.objects.filter(ProductionDate__range=[FromDate,ToDate],Division_id=DivisionID,IsDelete=0).annotate(
                    EstimatedOutputQty=ExpressionWrapper(
                        Subquery(bom_subquery)  * F('NumberOfLot'),
                        output_field=DecimalField(max_digits=15, decimal_places=2)
                    ))
                # print(query.query)
                # query = T_Production.objects.raw(f'''SELECT 
                # T_Production.id,
                # T_Production.EstimatedQuantity,
                # T_Production.ActualQuantity,
                # T_Production.NumberOfLot,                
                # (M_BillOfMaterial.EstimatedOutputQty * T_Production.NumberOfLot) AS EstimatedOutputQty
                # FROM T_Production
                # JOIN M_BillOfMaterial ON M_BillOfMaterial.Item_id = T_Production.Item_id
                # WHERE T_Production.ProductionDate BETWEEN '{FromDate}' AND '{ToDate}'
                # AND T_Production.Division_id = {DivisionID}
                # AND T_Production.IsDelete = 0 ''')    
                # print(query.query)
                if query:
                    Production_Serializer = H_ProductionSerializerforGET(query, many=True).data                  
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Production_Serializer})  
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})        
            

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
                PrintedBatchCode=Productiondata['PrintedBatchCode']
                NoOfLotsQty=Productiondata['NumberOfLot']
                NoOfQuantity=Productiondata['EstimatedQuantity']
                Materialissueid=Productiondata['ProductionMaterialIssue'][0]['MaterialIssue']
                ProdctionDate=Productiondata['ProductionDate']
                # print(ProdctionDate)
                query1 = T_Production.objects.filter(Item_id=Item, BatchDate=date.today()).values('id')                
                BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(Item, Customer, query1.count())
                
                BaseUnitQuantity=UnitwiseQuantityConversion(Item,Productiondata['ActualQuantity'],Productiondata['Unit'],0,0,0,1).GetBaseUnitQuantity()
                
                # Gst = GSTHsnCodeMaster(Item, Productiondata['ProductionDate']).GetTodaysGstHsnCode()                
                Gst = M_GSTHSNCode.objects.raw(f'''select 1 as id, GSTHsnCodeMaster({Item},%s,1,0,0)GSTID,
                                                GSTHsnCodeMaster({Item},%s,2,0,0)GSTPercentage ''',[Productiondata['ProductionDate'],Productiondata['ProductionDate']])
                
                GSTID = Gst[0].GSTID
                
                GSTValue=round(float(Gst[0].GSTPercentage),2)          
                
            
                CssCustomerPriceList=M_Settings.objects.filter(id=62).values("DefaultValue")
                CustomerPriceList=str(CssCustomerPriceList[0]['DefaultValue'])  
                CustomerRateQuery=M_RateMaster.objects.raw( f'''Select 1 id, Round(GetTodaysDateRate({Item}, '{ProdctionDate}',0,{CustomerPriceList},2),2) AS Rate''')
                CustomerRate = CustomerRateQuery[0].Rate 
                # print(CustomerRate)
                # MRPs=M_MRPMaster.objects.raw(f'''SELECT 1 id ,GetTodaysDateMRP({Item},'{ProductionDate}',1,0,0,0) MRPID,GetTodaysDateMRP({Item},'{ProductionDate}',2,0,0,0) MRPValue ''') 
                # first_row = MRPs[0]
                # MRPID = first_row.MRPID               
                # MRPValue=first_row.MRPValue
              
               
                
                # ProductionItemCount=T_Production.objects.filter(Item_id=Item, ProductionDate=ProductionDate).count()
                # ProductionItemCount_str = str(ProductionItemCount)
                a = GetMaxNumber.GetProductionNumber(Customer,ProdctionDate)
                Productiondata['ProductionNumber'] = a
                b = GetPrifix.GetProductionPrifix(Customer)
                b = b.strip() if b else ""                
                Productiondata['FullProductionNumber'] = b+""+str(a)
               
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
                    
                    "MRP": "",
                    "Rate":CustomerRate,
                    "GST": GSTID,
                    "SystemBatchDate": Productiondata['BatchDate'],
                    "SystemBatchCode": Productiondata['BatchCode'],
                    "BatchDate": Productiondata['BatchDate'],
                    "BatchCode": PrintedBatchCode,
                    "ItemExpiryDate":Productiondata['BestBefore'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList, 
                    "MRPValue":0,
                    "GSTPercentage":GSTValue,
                    
                    }) 
                # CustomPrint(O_LiveBatchesList)   
                
                # print(GRNdata)
                Productiondata.update({"O_LiveBatchesList":O_LiveBatchesList})                 
                Production_Serializer = H_ProductionSerializer(data=Productiondata)
                # CustomPrint(Production_Serializer)
                if Production_Serializer.is_valid():                    
                    Production_Serializer.save() 
                    MaterialissueNOofLots = T_MaterialIssue.objects.filter(id=Materialissueid).values('RemainNumberOfLot','RemaninLotQuantity')
                    if MaterialissueNOofLots:
                        RemaningLots=MaterialissueNOofLots[0]['RemainNumberOfLot']
                        RamaningQty = float(MaterialissueNOofLots[0]['RemaninLotQuantity']) 
                        RemainNumberOfLot=float(RemaningLots)-float(NoOfLotsQty)
                        RemaninQuantity=float(RamaningQty)-float(NoOfQuantity) 
                    # if(RemaningLots==NoOfLotsQty):  
                    if RemainNumberOfLot == 0:                      
                       query = T_MaterialIssue.objects.filter(id=Materialissueid).update(Status=2,RemainNumberOfLot=RemainNumberOfLot,RemaninLotQuantity=RemaninQuantity)
                    else:                       
                       query = T_MaterialIssue.objects.filter(id=Materialissueid).update(Status=1,RemainNumberOfLot=RemainNumberOfLot,RemaninLotQuantity=RemaninQuantity)                   
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production Save Successfully', 'Data':[]})
                else:
                    
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Production_Serializer.errors, 'Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request, 0, 0, 'DemandDetailsForChallan:' + str(e), 33, 0)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})       

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
                # print(O_BatchWiseLiveStockData.query)
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Production Quantity Used in another Transaction', 'Data': []})  
                    else:
                        batch_stock = O_BatchWiseLiveStock.objects.filter(Production_id=id)                        
                        parent_ids = batch_stock.values_list('LiveBatche_id', flat=True)  
                        O_LiveBatches.objects.filter(id__in=parent_ids).delete()
                        batch_stock.delete() 
                CustomPrint(id)
                MaterialissueidOnProd = TC_ProductionMaterialIssue.objects.filter(Production_id=id).values('MaterialIssue_id')
                CustomPrint(MaterialissueidOnProd.query)
                Productioninfo = T_Production.objects.filter(id=id).values('EstimatedQuantity','NumberOfLot')  
                CustomPrint(Productioninfo.query)              
                PLot=Productioninfo[0]['NumberOfLot']
                CustomPrint(PLot)
                PQuantity=Productioninfo[0]['EstimatedQuantity']
                CustomPrint(PQuantity)
                Materialissueid=MaterialissueidOnProd[0]['MaterialIssue_id']
                CustomPrint(Materialissueid)
                query1 = T_MaterialIssue.objects.filter(id=Materialissueid).values('RemainNumberOfLot','RemaninLotQuantity','NumberOfLot')
                ActualLot=query1[0]['RemainNumberOfLot']+PLot
                ActualQty=float(query1[0]['RemaninLotQuantity'])+float(PQuantity)
                orignalLot=query1[0]['NumberOfLot']                
                if(orignalLot==ActualLot):
                     Status=0
                else:
                     Status=1
                query = T_MaterialIssue.objects.filter(id=Materialissueid).update(Status=Status,RemainNumberOfLot=ActualLot,RemaninLotQuantity=ActualQty)
                # Productiondata = T_Production.objects.get(id=id)
                # Productiondata.delete()
                Productiondata = T_Production.objects.filter(id=id).update(IsDelete = 1)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production  Deleted Successfully', 'Data':[]})
        except T_Production.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Production Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Production used in another table', 'Data': []})    