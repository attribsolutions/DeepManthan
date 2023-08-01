from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix, SystemBatchCodeGeneration
from ..Serializer.S_CreditDebit import *
from ..Serializer.S_Items import *
from ..Serializer.S_GRNs import *
from django.db.models import Sum
from ..models import *
import datetime
import base64
from io import BytesIO
from PIL import Image



class PurchaseReturnListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Returndata = JSONParser().parse(request)
                FromDate = Returndata['FromDate']
                ToDate = Returndata['ToDate']
                Customer = Returndata['CustomerID']
                Party = Returndata['PartyID']

                
                if(Customer == ''):
                    cust=Q()
                else:
                    cust=Q(Customer=Customer) 
                
                if(Party == ''):
                    par=Q()
                else:
                    par=Q(Party=Party)
                
                query = T_PurchaseReturn.objects.filter(ReturnDate__range=[FromDate, ToDate]).filter( cust ).filter(par)
                
                # print(query.query)
                if query:
                    Return_serializer = PurchaseReturnSerializerSecond(query, many=True).data
                    ReturnListData = list()
                    for a in Return_serializer:
                        q0=TC_PurchaseReturnReferences.objects.filter(SubReturn=a['id'])
                       
                        if q0.count() > 0:
                            IsSendToSS = 1
                        else:
                            IsSendToSS = 0

                        if (IsSendToSS == 1):
                            Status = "Send To Supplier"
                            
                        elif a["IsApproved"] == 1: 
                            
                            Status = "Approved" 
                        else:
                            Status = "Open"    
                        ReturnListData.append({
                            "id": a['id'], 
                            "ReturnDate": a['ReturnDate'],
                            "ReturnNo": a['ReturnNo'],
                            "FullReturnNumber": a['FullReturnNumber'],
                            "ReturnReasonID":a['ReturnReason']['id'],
                            "ReturnReasonName":a['ReturnReason']['Name'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "IsApproved" : a["IsApproved"],
                            "Status" : Status
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReturnListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    


class PurchaseReturnView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser,MultiPartParser,FormParser]
    # authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_PurchaseReturn.objects.filter(id=id)
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query, many=True).data 
                    
                    PuchaseReturnList=list()

                    for a in PurchaseReturnSerializer:
                        PurchaseReturnItemList=list()
                        for b in a['ReturnItems']:
                            PurchaseReturnItemList.append({
                                "id":b['id'],
                                "ItemComment":b['ItemComment'],
                                "Quantity":b['Quantity'],
                                "BaseUnitQuantity":b['BaseUnitQuantity'],
                                "MRPValue":b['MRPValue'],
                                "Rate":b['Rate'],
                                "BasicAmount":b['BasicAmount'],
                                "TaxType":b['TaxType'],
                                "GSTPercentage":b['GSTPercentage'],
                                "GSTAmount":b['GSTAmount'],
                                "Amount":b['Amount'],
                                "CGST":b['CGST'],
                                "SGST":b['SGST'],
                                "IGST":b['IGST'],
                                "CGSTPercentage":b['CGSTPercentage'],
                                "SGSTPercentage":b['SGSTPercentage'],
                                "IGSTPercentage":b['IGSTPercentage'],
                                "BatchDate":b['BatchDate'],
                                "BatchCode":b['BatchCode'],
                                "CreatedOn":b['CreatedOn'],
                                "GST":b['GST'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'],
                                "MRP":b['MRP'],
                                "PurchaseReturn":b['PurchaseReturn'],
                                "Unit":b['Unit']['id'],
                                "UnitName" : b['Unit']['UnitID']['Name'],
                                "ItemReasonID":b['ItemReason']['id'],
                                "ItemReason":b['ItemReason']['Name'],
                                "Comment":b['Comment'],
                                "DiscountType":b['DiscountType'],
                                "Discount":b['Discount'],
                                "DiscountAmount":b['DiscountAmount'],

                                "ApprovedQuantity":b['ApprovedQuantity']
                                

                            })
                        
                        PuchaseReturnList.append({
                            "ReturnDate":a['ReturnDate'],
                            "ReturnNo":a['ReturnNo'],
                            "FullReturnNumber":a['FullReturnNumber'],
                            "GrandTotal":a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Comment":a['Comment'],
                            "CreatedOn":a['CreatedOn'],
                            "UpdatedOn":a['UpdatedOn'],
                            "Customer":a['Customer'],
                            "Party":a['Party'],
                            "ReturnReason":a['ReturnReason'],
                            "IsApproved" : a["IsApproved"],
                            "ReturnItems":PurchaseReturnItemList
                        })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PuchaseReturnList})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def post(self, request,format=None):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                Party = PurchaseReturndata['Party']
                Date = PurchaseReturndata['ReturnDate']
                Mode = PurchaseReturndata['Mode']
                
                c = GetMaxNumber.GetPurchaseReturnNumber(Party,Date)
                PurchaseReturndata['ReturnNo'] = str(c)
                if Mode == 1: # Sales Return
                    d= 'SRN'
                else:
                    d = GetPrifix.GetPurchaseReturnPrifix(Party)
                    
                PurchaseReturndata['FullReturnNumber'] = str(d)+""+str(c)
                
                item = ""
                query = T_PurchaseReturn.objects.filter(Party_id=Party).values('id')
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                UpdateO_BatchWiseLiveStockList = list()
                
                # if PurchaseReturndata['ReturnReason'] == 56:   
                #     IsDamagePieces =False
                # else:
                #     IsDamagePieces =True 
                
               
                for a in PurchaseReturndata['ReturnItems']:

                    if a['ItemReason'] == 56:
                        
                        IsDamagePieces =False
                    else:
                        IsDamagePieces =True 
                    
                    
                    query1 = TC_PurchaseReturnItems.objects.filter(Item_id=a['Item'], BatchDate=date.today(), PurchaseReturn_id__in=query).values('id')
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                    if(item == ""):
                        item = a['Item']
                        b = query1.count()

                    elif(item == a['Item']):
                        item = 1
                        b = b+1
                    else:
                        item = a['Item']
                        b = 0
                        
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'],Party, b)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                    
                    
                    O_BatchWiseLiveStockList.append({
                    "id":a['BatchID'],    
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Party,
                    "IsDamagePieces":IsDamagePieces,
                    "CreatedBy":PurchaseReturndata['CreatedBy']
                    
                    })
                    
                    # Sales Returnconsoldated Stock Minus When Send to Supplier AND Self Purchase Return 
                    UpdateO_BatchWiseLiveStockList.append({
                    "id":a['BatchID'],    
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "PurchaseReturn":a['PurchaseReturn'],
                    
                    })
                    
                    
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "MRPValue": a['MRPValue'],
                    "Rate": a['Rate'],
                    "GST": a['GST'],
                    "GSTPercentage": a['GSTPercentage'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList,
                    "UpdateO_BatchWiseLiveStockList":UpdateO_BatchWiseLiveStockList                   
                    
                    })
                    O_BatchWiseLiveStockList=list()
                    UpdateO_BatchWiseLiveStockList = list()
                    
                # print(GRNdata)
                PurchaseReturndata.update({"O_LiveBatchesList":O_LiveBatchesList}) 
               
                PurchaseReturn_Serializer = PurchaseReturnSerializer(data=PurchaseReturndata)
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':'', 'Data':PurchaseReturn_Serializer.data})
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    # Purchase Return DELETE API New code Date 25/07/2023
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_PurchaseReturn.objects.filter(id=id).values('Mode')
                Mode = str(Query[0]['Mode'])
                if Mode == '1':   # Sales Return Mode
                    PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
                    PurchaseReturn_Data.delete()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []})
                else:
                    Query2 = T_PurchaseReturn.objects.filter(id=id)
                    if Query2.exists():
                        PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query2, many=True).data 
                        for a in PurchaseReturnSerializer:
                            for b in a['ReturnItems']:
                                Qty =0.00
                                if Mode == '2': # Purchase Return Mode 
                                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
                                else:    
                                    OBatchQuantity=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
                                Qty=float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
                                if(OBatchQuantity[0]['OriginalBaseUnitQuantity'] >= float(Qty)):
                                    if Mode == '2': # Purchase Return Mode
                                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) 
                                    else:
                                        OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) #float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
                                    Qty =0.00
                                else:    
                                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Qty greater than Consolidated return qty', 'Data': []})     
                        PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
                        PurchaseReturn_Data.delete()        
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []}) 
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 
    
    #Purchase Return Delete API code Date Working code  Date 24/07/2023
    
    # @transaction.atomic()
    # def delete(self, request, id=0):
    #     try:
    #         with transaction.atomic():
    #             Query = TC_PurchaseReturnReferences.objects.filter(PurchaseReturn=id)
    #             if Query:
    #                 Query2 = T_PurchaseReturn.objects.filter(id=id)
    #                 if Query2.exists():
    #                     PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query2, many=True).data 
    #                     for a in PurchaseReturnSerializer:
    #                         for b in a['ReturnItems']:
    #                             Qty =0.00 
    #                             OBatchQuantity=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
    #                             Qty=float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
    #                             if(OBatchQuantity[0]['OriginalBaseUnitQuantity'] >= float(Qty)):
    #                                 OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(PurchaseReturn=b['SubReturn'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) #float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
    #                                 Qty =0.00
    #                             else:    
    #                                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Qty greater than Consolidated return qty', 'Data': []})     
    #                     PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
    #                     PurchaseReturn_Data.delete()        
    #                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []}) 
    #             else:
    #                 Query = T_PurchaseReturn.objects.filter(id=id).values('Mode')
    #                 if str(Query[0]['Mode'])== '2':
    #                     Query = T_PurchaseReturn.objects.filter(id=id)
    #                     PurchaseReturnSerializer = PurchaseReturnSerializerThird(Query, many=True).data
    #                     for a in PurchaseReturnSerializer:
                            
    #                         for b in a['ReturnItems']:
    #                             Qty =0.00
    #                             OBatchQuantity=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
    #                             Qty=float(OBatchQuantity[0]['BaseUnitQuantity']) + float(b['BaseUnitQuantity'])
    #                             if(OBatchQuantity[0]['OriginalBaseUnitQuantity'] >= float(Qty)):
    #                                 OBatchWiseLiveStock=O_BatchWiseLiveStock.objects.filter(id=b['BatchID'],Item=b['Item']['id']).update(BaseUnitQuantity = Qty ) 
    #                                 Qty =0.00
    #                             else:    
    #                                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Qty greater than Consolidated return qty', 'Data': []})
    #                     PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
    #                     PurchaseReturn_Data.delete()    
    #                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []})
    #                 else:
    #                     PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
    #                     PurchaseReturn_Data.delete()
    #                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []}) 
    #     except IntegrityError:
    #         return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
    #     except Exception as e:
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})                 
        
##################### Purchase Return Item View ###########################################        
        
class ReturnItemAddView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Items.objects.filter(id=id)
                if query.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Itemsdata = ItemSerializerSecond(query, many=True).data
                    # return JsonResponse({'query':  Itemsdata})
                    Itemlist = list()
                    InvoiceItems=list()
                    for a in Itemsdata:
                        Item=a['id']
                        Unitquery = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                        if Unitquery.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                            ItemUnitDetails = list()
                            for c in Unitdata:
                                ItemUnitDetails.append({
                                "Unit": c['id'],
                                "BaseUnitQuantity": c['BaseUnitQuantity'],
                                "IsBase": c['IsBase'],
                                "UnitName": c['BaseUnitConversion'],
                            })
                        
                        MRPquery = M_MRPMaster.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        if MRPquery.exists():
                            MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                            ItemMRPDetails = list()
                            
                            for d in MRPdata:
                                ItemMRPDetails.append({
                                "MRP": d['id'],
                                "MRPValue": d['MRP'],   
                            })
                        
                        GSTquery = M_GSTHSNCode.objects.filter(Item_id=Item).order_by('-id')[:3] 
                        if GSTquery.exists():
                            Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                            ItemGSTDetails = list()
                            for e in Gstdata:
                                ItemGSTDetails.append({
                                "GST": e['id'],
                                "GSTPercentage": e['GSTPercentage'],   
                            }) 
                        InvoiceItems.append({
                            "Item": a['id'],
                            "ItemName": a['Name'],
                            "ItemUnitDetails": ItemUnitDetails, 
                            "ItemMRPDetails":ItemMRPDetails,
                            "ItemGSTDetails":ItemGSTDetails
                        })
                    
                    Itemlist.append({"InvoiceItems":InvoiceItems})    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Itemlist[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Items Not available ', 'Data': []})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        



class ReturnItemBatchCodeAddView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                ItemID = PurchaseReturndata['ItemID']
                BatchCode = PurchaseReturndata['BatchCode']
                CustomerID =PurchaseReturndata['Customer']

                Itemquery = M_Items.objects.filter(id=ItemID).values("id","Name")
                Item =Itemquery[0]["id"]
                Unitquery = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0,UnitID_id=1).values("id")
                MRPquery = M_MRPMaster.objects.filter(Item_id=Item).order_by('-id')[:3] 
                if MRPquery.exists():
                    MRPdata = ItemMRPSerializerSecond(MRPquery, many=True).data
                    ItemMRPDetails = list()

                    for d in MRPdata:
                        CalculatedRateusingMRPMargin=RateCalculationFunction(0,Item,CustomerID,0,1,0,0,d['MRP']).RateWithGST()
                        Rate=CalculatedRateusingMRPMargin[0]["NoRatewithOutGST"]
                        ItemMRPDetails.append({
                        "MRP": d['id'],
                        "MRPValue": d['MRP'],   
                        "Rate" : round(Rate,2),
                    })

                GSTquery = M_GSTHSNCode.objects.filter(Item_id=Item).order_by('-id')[:3] 
                if GSTquery.exists():
                    Gstdata = ItemGSTHSNSerializerSecond(GSTquery, many=True).data
                    ItemGSTDetails = list()
                    for e in Gstdata:
                        ItemGSTDetails.append({
                        "GST": e['id'],
                        "GSTPercentage": e['GSTPercentage'],   
                    }) 

                obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=CustomerID,BaseUnitQuantity__gt=0,IsDamagePieces=0)
                if obatchwisestockquery == "":
                    StockQtySerialize_data =[]
                else:
                    StockQtySerialize_data = StockQtyserializerForPurchaseReturn(obatchwisestockquery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': StockQtySerialize_data})
                    StockDatalist = list()
                    
                    for ad in StockQtySerialize_data:
                        Rate=RateCalculationFunction(ad['LiveBatche']['id'],ad['Item']['id'],CustomerID,0,1,0,0).RateWithGST()
                        # print(Rate)

                        if(ad['LiveBatche']['MRP']['id'] is None):
                            MRPValue=ad['LiveBatche']['MRPValue']
                        else:
                            MRPValue=ad['LiveBatche']['MRP']['MRP']
                        
                        if(ad['LiveBatche']['GST']['id'] is None):
                            GSTPercentage=ad['LiveBatche']['GSTPercentage']
                        else:
                            GSTPercentage=ad['LiveBatche']['GST']['GSTPercentage']
                        
                        QtyInNo=UnitwiseQuantityConversion(ad['Item']['id'],ad['BaseUnitQuantity'],0,0,0,1,0).ConvertintoSelectedUnit()
                        
                        StockDatalist.append({
                            "id": ad['id'],
                            "Item":ad['Item']['id'],
                            "BatchDate":ad['LiveBatche']['BatchDate'],
                            "BatchCode":ad['LiveBatche']['BatchCode'],
                            "SystemBatchDate":ad['LiveBatche']['SystemBatchDate'],
                            "SystemBatchCode":ad['LiveBatche']['SystemBatchCode'],
                            "LiveBatche" : ad['LiveBatche']['id'],
                            "LiveBatcheMRPID" : ad['LiveBatche']['MRP']['id'],
                            "LiveBatcheGSTID" : ad['LiveBatche']['GST']['id'],
                            "Rate":round(Rate[0]["NoRatewithOutGST"],2),
                            "MRP" : MRPValue,
                            "GST" : GSTPercentage,
                            "BaseUnitQuantity":QtyInNo,
                            })

                if BatchCode != "":

                    query = TC_GRNItems.objects.filter(Item=ItemID,BatchCode=BatchCode).order_by('id')[:1]
                    
                    if query:
                        GRNItemsdata = TC_GRNItemsSerializerSecond(query, many=True).data
                        Rate=RateCalculationFunction(0,Itemquery[0]["id"],CustomerID,0,1,0,0).RateWithGST()
                        for a in GRNItemsdata:
                            MRP = a['MRP']["id"]
                            MRPValue= a['MRPValue']
                            Rate= round(float(Rate[0]["NoRatewithOutGST"]),2)
                            GST= a['GST']["id"]
                            GSTPercentage= a['GSTPercentage']
                            BatchCode= a['BatchCode']
                            BatchDate= a['BatchDate']
                            Unit = Unitquery[0]["id"]
                            UnitName = "No"
                    else:  
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message' : 'Batch Code is Not Available', 'Data': []})      

                else: 

                        MRP = ""
                        MRPValue= ""
                        Rate= ""
                        GST= ""
                        GSTPercentage= ""
                        BatchCode= ""
                        BatchDate= ""
                        Unit = Unitquery[0]["id"]
                        UnitName = "No"


                GRMItems = list()
                GRMItems.append({
                        "Item": Itemquery[0]["id"],
                        "ItemName": Itemquery[0]["Name"],
                        "MRP": MRP,
                        "MRPValue": MRPValue,
                        "Rate": Rate,
                        "GST": GST,
                        "GSTPercentage": GSTPercentage,
                        "BatchCode": BatchCode,
                        "BatchDate": BatchDate,
                        "Unit" : Unitquery[0]["id"],
                        "UnitName" : "No",
                        # "ItemUnitDetails": ItemUnitDetails, 
                        "ItemMRPDetails":ItemMRPDetails,
                        "ItemGSTDetails":ItemGSTDetails,
                        "StockDetails":StockDatalist 
                })   
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRMItems})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})      


class SalesReturnconsolidatePurchaseReturnView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                ReturnItemdata = JSONParser().parse(request)
                Party= ReturnItemdata['PartyID']
                ReturnID= ReturnItemdata['ReturnID']
                a=ReturnID.split(',')
                Query = TC_PurchaseReturnItems.objects.filter(PurchaseReturn__id__in=a)
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnItemsSerializer2(Query, many=True).data 
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnSerializer})
                    # PuchaseReturnList=list()
                    PurchaseReturnItemList=list()
                    for b in PurchaseReturnSerializer:
                        Rate=RateCalculationFunction(0,b['Item']['id'],Party,0,1,0,0).RateWithGST()
                        PurchaseReturnItemList.append({
                            "ItemComment":b['ItemComment'],
                            "Quantity":b['Quantity'],
                            "ApprovedQuantity" : b["ApprovedQuantity"],
                            "BaseUnitQuantity":b['BaseUnitQuantity'],
                            "MRPValue":b['MRPValue'],
                            "Rate":round(float(Rate[0]["NoRatewithOutGST"]),2),
                            "BasicAmount":b['BasicAmount'],
                            "TaxType":b['TaxType'],
                            "GSTPercentage":b['GSTPercentage'],
                            "GSTAmount":b['GSTAmount'],
                            "Amount":b['Amount'],
                            "CGST":b['CGST'],
                            "SGST":b['SGST'],
                            "IGST":b['IGST'],
                            "CGSTPercentage":b['CGSTPercentage'],
                            "SGSTPercentage":b['SGSTPercentage'],
                            "IGSTPercentage":b['IGSTPercentage'],
                            "BatchDate":b['BatchDate'],
                            "BatchCode":b['BatchCode'],
                            "CreatedOn":b['CreatedOn'],
                            "GST":b['GST'],
                            "Item" : b["Item"]["id"],
                            "ItemName":b['Item']['Name'],
                            "MRP":b['MRP'],
                            "PurchaseReturn":b['PurchaseReturn'],
                            "Unit":b['Unit']["id"],
                            "UnitName" : b["Unit"]["UnitID"]["Name"],
                            "ItemReason":b['ItemReason']['id'],
                            "ItemReasonName":b['ItemReason']['Name'],
                            "Comment":b['Comment'],
                            "DiscountType":b['DiscountType'],
                            "Discount":b['Discount'],
                            "DiscountAmount":b['DiscountAmount']
                            
                        })
                        
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnItemList})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})     
        

class SalesReturnItemApproveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                
                PurchaseReturndata = JSONParser().parse(request)
                ReturnID = PurchaseReturndata['ReturnID']
                CreatedBy = PurchaseReturndata['UserID']  
                ReturnItem = PurchaseReturndata['ReturnItem']
                # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':'', 'Data':PurchaseReturndata})
                aa=T_PurchaseReturn.objects.filter(id=ReturnID).update(IsApproved=1)
                Partyquery = T_PurchaseReturn.objects.filter(id=ReturnID).values('Party')
                Party = Partyquery[0]["Party"]
                item = ""
                query = T_PurchaseReturn.objects.filter(Party_id=Party).values('id')
               
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                
               
                for a in ReturnItem:
                    
                    SetFlag=TC_PurchaseReturnItems.objects.filter(id=a["id"]).update(ApprovedQuantity=a["ApprovedQuantity"],ApprovedBy=a["Approvedby"],ApproveComment=a["ApproveComment"])
 
                    # Company Division Pricelist not assign we got error
                    # Rate=RateCalculationFunction(0,a['Item'],Party,0,1,0,0).RateWithGST()
                    
                    Rate =0.00

                    if a['ItemReason'] == 56:
                        
                        IsDamagePieces =False
                    else:
                        IsDamagePieces =True 
                    
                    query1 = TC_PurchaseReturnItems.objects.filter(Item_id=a['Item'], BatchDate=date.today(), PurchaseReturn_id__in=query).values('id')
                    query2=MC_ItemShelfLife.objects.filter(Item_id=a['Item'],IsDeleted=0).values('Days')
                   
                    if(item == ""):
                        item = a['Item']
                        b = query1.count()

                    elif(item == a['Item']):
                        item = 1
                        b = b+1
                    else:
                        item = a['Item']
                        b = 0
                        
                   
                        
                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'],Party, b)
                  
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a["ApprovedQuantity"],0,0,0,1,0)
                   
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                  
                   
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                    
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Party,
                    "IsDamagePieces":IsDamagePieces,
                    "PurchaseReturn":ReturnID,
                    "CreatedBy":CreatedBy
                    
                    })
                    
                    
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "MRPValue": a['MRPValue'],

                    "Rate": Rate,                  '''round(float(Rate[0]["NoRatewithOutGST"]),2)'''

                    "GST": a['GST'],
                    "GSTPercentage": a['GSTPercentage'],
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList            
                    
                    })
                   
                PurchaseReturndata.update({"O_LiveBatchesList":O_LiveBatchesList})
                PurchaseReturn_Serializer = ReturnApproveQtySerializer(data=PurchaseReturndata)
                if PurchaseReturn_Serializer.is_valid():
                    PurchaseReturn_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Item Approve Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})     
                
                
                
class PurchaseReturnPrintView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Query = T_PurchaseReturn.objects.filter(id=id)
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnPrintSerilaizer(Query, many=True).data 
                    PuchaseReturnList=list()
                    for a in PurchaseReturnSerializer:
                        PurchaseReturnItemList=list()
                    
                        DefCustomerAddress = ''  
                        for ad in a['Customer']['PartyAddress']:
                            if ad['IsDefault'] == True :
                                DefCustomerAddress = ad['Address']
                                
                        DefPartyAddress = ''
                        for x in a['Party']['PartyAddress']:
                            if x['IsDefault'] == True :
                                DefPartyAddress = x['Address']
                        
                        for b in a['ReturnItems']:
                            PurchaseReturnItemList.append({
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'],
                                "ItemComment":b['ItemComment'],
                                "HSNCode":b['GST']['HSNCode'],
                                "Quantity":b['Quantity'],
                                "BaseUnitQuantity":b['BaseUnitQuantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRPValue'],
                                "Rate":b['Rate'],
                                "BasicAmount":b['BasicAmount'],
                                "TaxType":b['TaxType'],
                                "GSTPercentage":b['GSTPercentage'],
                                "GSTAmount":b['GSTAmount'],
                                "Amount":b['Amount'],
                                "CGST":b['CGST'],
                                "SGST":b['SGST'],
                                "IGST":b['IGST'],
                                "CGSTPercentage":b['CGSTPercentage'],
                                "SGSTPercentage":b['SGSTPercentage'],
                                "IGSTPercentage":b['IGSTPercentage'],
                                "BatchDate":b['BatchDate'],
                                "BatchCode":b['BatchCode'],
                                "CreatedOn":b['CreatedOn'],
                                "PurchaseReturn":b['PurchaseReturn'],
                                "Unit":b['Unit']['id'],
                                "UnitName" : b['Unit']['UnitID']['Name'],
                                "ItemReasonID":b['ItemReason']['id'],
                                "ItemReason":b['ItemReason']['Name'],
                                "Comment":b['Comment'],
                                "DiscountType":b['DiscountType'],
                                "Discount":b['Discount'],
                                "DiscountAmount":b['DiscountAmount']
                            })
                
                        PuchaseReturnList.append({
                            "ReturnDate":a['ReturnDate'],
                            "ReturnNo":a['ReturnNo'],
                            "FullReturnNumber":a['FullReturnNumber'],
                            "GrandTotal":a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Comment":a['Comment'],
                            "CreatedOn":a['CreatedOn'],
                            "UpdatedOn":a['UpdatedOn'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "CustomerMobileNo": a['Customer']['MobileNo'],
                            "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                            "CustomerState": a['Customer']['State']['Name'],     
                            "CustomerAddress": DefCustomerAddress,
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "PartyMobileNo": a['Party']['MobileNo'],
                            "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
                            "PartyState": a['Party']['State']['Name'],
                            "PartyAddress": DefPartyAddress,       
                            "ReturnReason":a['ReturnReason'],
                            "IsApproved" : a["IsApproved"],
                            "ReturnItems":PurchaseReturnItemList
                        })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PuchaseReturnList[0]})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})                