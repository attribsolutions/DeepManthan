
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
                DivisionID=Productiondata['Party']
                query = T_Production.objects.filter(ProductionDate__range=[FromDate,ToDate],Division_id=DivisionID)
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
                PrintedBatchCode=Productiondata['PrintedBatchCode']
                NoOfLotsQty=Productiondata['NumberOfLot']
                NoOfQuantity=Productiondata['EstimatedQuantity']
                Materialissueid=Productiondata['ProductionMaterialIssue'][0]['MaterialIssue']
                ProdctionDate=Productiondata['ProductionDate']
                # print(ProdctionDate)
                query1 = T_Production.objects.filter(Item_id=Item, BatchDate=date.today()).values('id')                
                BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(Item, Customer, query1.count())
                
                BaseUnitQuantity=UnitwiseQuantityConversion(Item,Productiondata['ActualQuantity'],Productiondata['Unit'],0,0,0,1).GetBaseUnitQuantity()
                
                Gst = GSTHsnCodeMaster(Item, Productiondata['ProductionDate']).GetTodaysGstHsnCode()                
                GSTID = Gst[0]['Gstid']
                GSTValue=Gst[0]['GST']                
                
            
                CssCustomerPriceList=M_Settings.objects.filter(id=62).values("DefaultValue")
                CustomerPriceList=str(CssCustomerPriceList[0]['DefaultValue'])  
                CustomerRateQuery=M_RateMaster.objects.raw( f'''Select 1 id, Round(GetTodaysDateRate({Item}, '{ProdctionDate}',0,{CustomerPriceList},2),2) AS Rate''')
                CustomerRate = CustomerRateQuery[0].Rate 
                # print(CustomerRate)
                # MRPs=M_MRPMaster.objects.raw(f'''SELECT 1 id ,GetTodaysDateMRP({Item},'{ProductionDate}',1,0,0,0) MRPID,GetTodaysDateMRP({Item},'{ProductionDate}',2,0,0,0) MRPValue ''') 
                # first_row = MRPs[0]
                # MRPID = first_row.MRPID               
                # MRPValue=first_row.MRPValue
                # CustomPrint(MRPID)
                # CustomPrint(MRPValue)
               
                
                # ProductionItemCount=T_Production.objects.filter(Item_id=Item, ProductionDate=ProductionDate).count()
                # ProductionItemCount_str = str(ProductionItemCount)
                
                # CustomPrint(Productiondata['BatchCode'])
                Productiondata['BatchCode'] = BatchCode
                # CustomPrint(ProductionItemCount_str)
                # productionbatchcode = Productiondata['BatchCode'] 
                # CustomPrint(Productiondata['BatchCode'])
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
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Production Quantity Used in another Transaction', 'Data': []})  
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
                Productiondata = T_Production.objects.get(id=id)
                Productiondata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Production  Deleted Successfully', 'Data':[]})
        except T_Production.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Production Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Production used in another table', 'Data': []})    