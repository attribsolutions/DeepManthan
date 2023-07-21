from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix, SystemBatchCodeGeneration
from ..Serializer.S_CreditDebit import *
from ..Serializer.S_Items import *
from ..Serializer.S_GRNs import *
from django.db.models import Sum
from ..models import *
import datetime

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
                                "Comment":b['Comment']
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
    def post(self, request):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)
                Party = PurchaseReturndata['Party']
                Date = PurchaseReturndata['ReturnDate']
                c = GetMaxNumber.GetPurchaseReturnNumber(Party,Date)
                PurchaseReturndata['ReturnNo'] = str(c)
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
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Party,
                    "IsDamagePieces":IsDamagePieces,
                    "CreatedBy":PurchaseReturndata['CreatedBy']
                    
                    })
                    
                    # Sales Returnconsoldated Stock Minus When Send to Supplier
                    UpdateO_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "PurchaseReturn":a['PurchaseReturn']
                    
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Purchase Return Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PurchaseReturn_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    # GRN DELETE API 
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                O_BatchWiseLiveStockData = O_BatchWiseLiveStock.objects.filter(PurchaseReturn_id=id).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
              
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Return  Used in another Transaction', 'Data': []})   
                
                PurchaseReturn_Data = T_PurchaseReturn.objects.get(id=id)
                PurchaseReturn_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Deleted Successfully', 'Data': []})
        except T_PurchaseReturn.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Return Used in another Transaction', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
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
                # if Unitquery.exists():
                #     Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                #     ItemUnitDetails = list()
                #     for c in Unitdata:
                #         ItemUnitDetails.append({
                #         "Unit": c['id'],
                #         "BaseUnitQuantity": c['BaseUnitQuantity'],
                #         "IsBase": c['IsBase'],
                #         "UnitName": c['BaseUnitConversion'],
                #     })

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

                stockquery = O_BatchWiseLiveStock.objects.filter(Item=ItemID, Party=CustomerID,IsDamagePieces=0).aggregate(Qty=Sum('BaseUnitQuantity'))
                if stockquery['Qty'] is None:
                    Stock = 0.0
                else:
                    Stock = stockquery['Qty']


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
                        "Stock":Stock 
                })   
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRMItems})
        except M_Items.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})      


class T_PurchaseReturnView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                ReturnItemdata = JSONParser().parse(request)
                ReturnID= ReturnItemdata['ReturnItemID']
                a=ReturnID.split(',')
                Query = TC_PurchaseReturnItems.objects.filter(PurchaseReturn__id__in=a)
                if Query.exists():
                    PurchaseReturnSerializer = PurchaseReturnItemsSerializer2(Query, many=True).data 
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnSerializer})
                    # PuchaseReturnList=list()
                    PurchaseReturnItemList=list()
                    for b in PurchaseReturnSerializer:
                        PurchaseReturnItemList.append({
                            "ItemComment":b['ItemComment'],
                            "Quantity":b['Quantity'],
                            "ApprovedQuantity" : b["ApprovedQuantity"],
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
                            "Item" : b["Item"]["id"],
                            "ItemName":b['Item']['Name'],
                            "MRP":b['MRP'],
                            "PurchaseReturn":b['PurchaseReturn'],
                            "Unit":b['Unit']["id"],
                            "UnitName" : b["Unit"]["UnitID"]["Name"],
                            "ItemReason":b['ItemReason']['id'],
                            "ItemReasonName":b['ItemReason']['Name'],
                            "Comment":b['Comment']
                        })
                        
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :PurchaseReturnItemList})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Item not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})     
        
        

class ReturnItemApproveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PurchaseReturndata = JSONParser().parse(request)    
                ReturnID = PurchaseReturndata['ReturnID']
                ReturnItem = PurchaseReturndata['ReturnItem']
                aa=T_PurchaseReturn.objects.filter(id=ReturnID).update(IsApproved=1)
                for a in ReturnItem:
                    SetFlag=TC_PurchaseReturnItems.objects.filter(id=a["id"]).update(ApprovedQuantity=a["ApprovedQuantity"],ApprovedBy=a["Approvedby"],ApproveComment=a["ApproveComment"])
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Return Item Approve Successfully','Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})     
                