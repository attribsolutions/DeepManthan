import datetime
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_GRNs import *
from ..Serializer.S_InterbranchChallan import *
from ..Serializer.S_InterBranchInward import *
from ..Serializer.S_Orders import *
from ..models import *
from django.db.models import *


class BranchInvoiceDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                BranchInvoiceQuery = T_InterbranchChallan.objects.filter(id=id)
                if BranchInvoiceQuery.exists():
                    BranchInvoiceSerializedata = IBChallanSerializerThird(
                        BranchInvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    BranchInvoiceData = list()
                    for a in BranchInvoiceSerializedata:
                        BranchInvoiceItemDetails = list()
                        for b in a['IBChallanItems']:
                            BranchInvoiceItemDetails.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRP": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GSTPercentage": b['GSTPercentage'],
                                "BasicAmount": b['BasicAmount'],
                                "GSTAmount": b['GSTAmount'],
                                "CGST": b['CGST'],
                                "SGST": b['SGST'],
                                "IGST": b['IGST'],
                                "CGSTPercentage": b['CGSTPercentage'],
                                "SGSTPercentage": b['SGSTPercentage'],
                                "IGSTPercentage": b['IGSTPercentage'],
                                "Amount": b['Amount'],
                                "BatchCode": b['BatchCode'],
                                "BatchDate": b['BatchDate'],
                            })
                            
                        BranchInvoiceData.append({
                            "id": a['id'],
                            "InvoiceDate": a['IBChallanDate'],
                            "InvoiceNumber": a['IBChallanNumber'],
                            "FullInvoiceNumber": a['FullIBChallanNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount":a['RoundOffAmount'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "InvoiceItems": BranchInvoiceItemDetails,
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': BranchInvoiceData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Branch Invoice Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    

class InterBranchInwardListFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Inwarddata = JSONParser().parse(request)
                FromDate = Inwarddata['FromDate']
                ToDate = Inwarddata['ToDate']
                Customer = Inwarddata['Customer']
                Supplier = Inwarddata['Supplier']
                if(Supplier == ''):
                    query = T_InterBranchInward.objects.filter(IBInwardDate__range=[FromDate, ToDate], Customer_id=Customer)
                else:
                    query = T_InterBranchInward.objects.filter(IBInwardDate__range=[FromDate, ToDate], Customer_id=Customer, Supplier_id=Supplier)
                Inward_serializer = T_InterBranchInwardSerializerForGET(
                        query, many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data': Inward_serializer})
                if query.count() == 0:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                  
                    Inward_serializer = T_InterBranchInwardSerializerForGET(
                        query, many=True).data
                    InwardListData = list()
                    for a in Inward_serializer:
                        InwardListData.append({
                            "id": a['id'],
                            "IBInwardDate": a['IBInwardDate'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "IBInwardNumber": a['IBInwardNumber'],
                            "FullIBInwardNumber": a['FullIBInwardNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "Supplier": a['Supplier']['id'],
                            "SupplierName": a['Supplier']['Name'],
                            "CreatedOn" : a['CreatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InwardListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
        
class InterBranchInwardView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Inwarddata = JSONParser().parse(request)
                Customer = Inwarddata['Customer']
                CreatedBy = Inwarddata['CreatedBy']
                IBInwardDate = Inwarddata['IBInwardDate']

# ==========================Get Max GRN Number=====================================================
                a = GetMaxNumber.GetIBInwardNumber(Customer,IBInwardDate)
                Inwarddata['IBInwardNumber'] = a
                b = GetPrifix.GetIBInwardPrifix(Customer)
                
                Inwarddata['FullIBInwardNumber'] = str(b)+""+str(a)
#================================================================================================== 
                item = ""
                query = T_InterBranchInward.objects.filter(Customer_id=Inwarddata['Customer']).values('id')
                O_BatchWiseLiveStockList=list()
                O_LiveBatchesList=list()
                for a in Inwarddata['InterBranchInwardItems']:
                    
                    query1 = TC_InterBranchInwardItems.objects.filter(Item_id=a['Item'], SystemBatchDate=date.today(), IBInward_id__in=query).values('id')
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

                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], Inwarddata['Customer'], b)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,1)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    Gst = GSTHsnCodeMaster(a['Item'], IBInwardDate).GetTodaysGstHsnCode()
                    GSTID = Gst[0]['Gstid']
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                    
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "Party": Customer,
                    "CreatedBy":CreatedBy,
                    
                    })
                    O_LiveBatchesList.append({
                    
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "MRP": a['MRP'],
                    "Rate": a['Rate'],
                    "GST": GSTID,
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "OriginalBatchBaseUnitQuantity" : BaseUnitQuantity,
                    "O_BatchWiseLiveStockList" :O_BatchWiseLiveStockList                   
                    
                    })

                Inwarddata.update({"O_LiveBatchesList":O_LiveBatchesList}) 
                # return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'InterBranch Inward Save Successfully', 'Data': Inwarddata})   
                Inward_serializer = T_InterBranchInwardSerializer(data=Inwarddata)
                if Inward_serializer.is_valid():
                    # return JsonResponse({'Data':Inward_serializer.data})
                    Inward_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'InterBranch Inward Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Inward_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        

class InterBranchInwardViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                O_BatchWiseLiveStockData = O_BatchWiseLiveStock.objects.filter(InterBranchInward_id=id).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
              
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'InterBranch Inward Used in another Transaction', 'Data': []})   
                
                Inward_Data = T_InterBranchInward.objects.get(id=id)
                Inward_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'InterBranch Inward  Deleted Successfully', 'Data': []})
        except T_InterBranchInward.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'InterBranch Inward used in another tbale', 'Data': []})