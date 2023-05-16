from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_GRNs import *
from ..Serializer.S_Challan import *
from ..Serializer.S_Bom import * 
from ..Serializer.S_Invoices import * 
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..models import  *

class ChallanItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request, id=0 ):
        try:
            with transaction.atomic():
                ChallanitemsData = JSONParser().parse(request)
                Company=ChallanitemsData['Company']
                Query = MC_BillOfMaterialItems.objects.filter(BOM__IsVDCItem=1,BOM__Company=Company).select_related('BOM','Item').values('Item').distinct()
                ItemList = list()
                for a in Query:
                    ItemList.append(a['Item'])
                y=tuple(ItemList)
                Itemsquery = M_Items.objects.filter(id__in=y,isActive=1)
                Itemsdata = M_ItemsSerializer01(Itemsquery,many=True).data    
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data':Itemsdata})      
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
class ChallanItemStockView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request, id=0 ):
        try:
            with transaction.atomic():
                ChallanItemData = JSONParser().parse(request)
                Item = ChallanItemData['Item']
                Party = ChallanItemData['Party']
                        
                obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0)
              
                if obatchwisestockquery == "":
                    StockQtySerialize_data =[]
                else: 
                    StockQtySerialize_data = StockQtyserializerForInvoice(obatchwisestockquery, many=True).data
                    stockDatalist = list()
                    for d in StockQtySerialize_data:
                        
                        stockDatalist.append({
                            "id": d['id'],
                            "Item":d['Item']['id'],
                            "BatchDate":d['LiveBatche']['BatchDate'],
                            "BatchCode":d['LiveBatche']['BatchCode'],
                            "SystemBatchDate":d['LiveBatche']['SystemBatchDate'],
                            "SystemBatchCode":d['LiveBatche']['SystemBatchCode'],
                            "LiveBatche" : d['LiveBatche']['id'],
                            "LiveBatcheMRPID" : d['LiveBatche']['MRP']['id'],
                            "LiveBatcheGSTID" : d['LiveBatche']['GST']['id'],
                            "Rate":d['LiveBatche']['Rate'],
                            "MRP" : d['LiveBatche']['MRP']['id'],
                            "MRPValue": d['LiveBatche']['MRP']['MRP'],
                            "GSTPercentage" : d['LiveBatche']['GST']['GSTPercentage'],
                            "GST": d['LiveBatche']['GST']['id'],
                            "HSNCode": d['LiveBatche']['GST']['HSNCode'],
                            "GSTPercentage": d['LiveBatche']['GST']['GSTPercentage'],
                            "UnitName":d['Unit']['UnitID'], 
                            "Unit":d['Unit']['BaseUnitConversion'], 
                            "BaseUnitQuantity":d['BaseUnitQuantity'], 
                            }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': stockDatalist})           
        except Exception as e:
            
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
class ChallanView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Challandata = JSONParser().parse(request)
                GRN = Challandata['GRN']
                if GRN == "":
                    ChallanDate = Challandata['ChallanDate']
                    Party = Challandata['Party']
                    a = GetMaxNumber.GetChallanNumber(Party,ChallanDate)
                    Challandata['ChallanNumber'] = a
                    b = GetPrifix.GetChallanPrifix(Party)
                    Challandata['FullChallanNumber'] = str(b)+""+str(a)
                    ChallanItems = Challandata['ChallanItems']
        
                    BatchWiseLiveStockList=list()
                    for ChallanItem in ChallanItems:
                        BatchWiseLiveStockList.append({
                            "Item" : ChallanItem['Item'],
                            "Quantity" : ChallanItem['Quantity'],
                            "BaseUnitQuantity" : ChallanItem['BaseUnitQuantity'],
                            "LiveBatche" : ChallanItem['BatchID'],
                            "Item" : ChallanItem['Item'],
                            "Party" : ChallanItem['Party'],
                        })
                        
                    Challandata.update({"BatchWiseLiveStockGRNID":BatchWiseLiveStockList}) 
                    Challan_serializer = ChallanSerializer(data=Challandata)
                    if Challan_serializer.is_valid():
                        # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.data, 'Data':[]})
                        Challan_serializer.save()
                        return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Challan Save Successfully', 'Data':[]})
                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.errors, 'Data':[]})
                else:
   
                    GRNdata = T_GRNs.objects.get(id=GRN)
                    GRN_serializer = T_GRNSerializerForGETSecond(GRNdata).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                    GRNItemListData = list()
                    for b in GRN_serializer['GRNItems']:
                        GRNItemListData.append({
                            "Item": b['Item']['id'],
                            "ItemName": b['Item']['Name'],
                            "Quantity": b['Quantity'],
                            "Unit": b['Unit']['id'],
                            "UnitName": b['Unit']['BaseUnitConversion'],
                            "BaseUnitQuantity": b['BaseUnitQuantity'],
                            "MRP": b['MRP'],
                            "ReferenceRate": b['ReferenceRate'],
                            "Rate": b['Rate'],
                            "BasicAmount": b['BasicAmount'],
                            "TaxType": b['TaxType'],
                            "GST": b['GST']['id'],
                            "GSTPercentage": b['GST']['GSTPercentage'],
                            "HSNCode": b['GST']['HSNCode'],
                            "GSTAmount": b['GSTAmount'],
                            "Amount": b['Amount'],
                            "DiscountType": b['DiscountType'],
                            "Discount": b['Discount'],
                            "DiscountAmount": b['DiscountAmount'],
                            "CGST": b['CGST'],
                            "SGST": b['SGST'],
                            "IGST": b['IGST'],
                            "CGSTPercentage": b['CGSTPercentage'],
                            "SGSTPercentage": b['SGSTPercentage'],
                            "IGSTPercentage": b['IGSTPercentage'],
                            "BatchDate": b['BatchDate'],
                            "BatchCode": b['BatchCode'],
                            "SystemBatchDate": b['SystemBatchDate'],
                            "SystemBatchCode": b['SystemBatchCode'],                            
                        })
                    GRNListData = list()
                    a = GRN_serializer
                    GRNListData.append({
                        "GRN": a['id'],
                        "ChallanDate": a['GRNDate'],
                        "Party": a['Customer']['id'],
                        "PartyName": a['Customer']['Name'],
                        "GrandTotal": a['GrandTotal'],
                        "Customer": a['Party']['id'],
                        "CustomerName": a['Party']['Name'],
                        "CreatedBy": a['CreatedBy'],
                        "UpdatedBy": a['UpdatedBy'],
                        "RoundOffAmount":"",
                        "ChallanItems": GRNItemListData,
                        "BatchWiseLiveStockGRNID":a['BatchWiseLiveStockGRNID']
                    })
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]})
                    Party = GRNListData[0]['Party']
                    ChallanDate = GRNListData[0]['ChallanDate']
                    # ==========================Get Max Invoice Number=====================================================
                    a = GetMaxNumber.GetChallanNumber(Party,ChallanDate)
                    GRNListData[0]['ChallanNumber'] = a
                    b = GetPrifix.GetChallanPrifix(Party)
                    GRNListData[0]['FullChallanNumber'] = str(b)+""+str(a)
                    #==================================================================================================
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData[0]}) 
                    Challan_serializer = ChallanSerializer(data=GRNListData[0])
                    if Challan_serializer.is_valid():
                        # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.data, 'Data':[]})
                        Challan_serializer.save()
                        return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Challan Save Successfully', 'Data':[]})
                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Challan_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e.__dict__, 'Data': []})
 
 
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata=T_Challan.objects.all().filter(id=id)
                Invoicedataserializer=ChallanSerializerForDelete(Invoicedata,many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Delete Successfully', 'Data':Invoicedataserializer})
                
                for a in Invoicedataserializer[0]['ChallanItems']:
                    BaseUnitQuantity11=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0,0).GetBaseUnitQuantity()
                    # return JsonResponse({'StatusCode': 200, 'Data':BaseUnitQuantity11})
                    selectQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).values('BaseUnitQuantity')
                    # return JsonResponse({'StatusCode': 200,'Data1':a['LiveBatch'],'Data2':BaseUnitQuantity11, 'Data3':selectQuery[0]['BaseUnitQuantity']})
                    UpdateQuery=O_BatchWiseLiveStock.objects.filter(LiveBatche=a['LiveBatch']).update(BaseUnitQuantity = float(selectQuery[0]['BaseUnitQuantity'])+float(BaseUnitQuantity11))
                Invoicedata = T_Challan.objects.get(id=id)
                Invoicedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Challan Delete Successfully', 'Data':[]})
        except T_Challan.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Challan Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Challan used in another table', 'Data': []})


class ChallanListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Challandata = JSONParser().parse(request)
                FromDate = Challandata['FromDate']
                ToDate = Challandata['ToDate']
                Customer = Challandata['Customer']
                Party = Challandata['Party']
                if(Customer == ''):
                    query = T_Challan.objects.filter(ChallanDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_Challan.objects.filter(ChallanDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party) 
                    
                if query:
                    Challan_serializer = ChallanSerializerList(query, many=True).data
                    ChallanListData = list()
                    for a in Challan_serializer:
                        ChallanListData.append({
                            "id": a['id'],
                            "ChallanDate": a['ChallanDate'],
                            "FullChallanNumber": a['FullChallanNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "CreatedOn": a['CreatedOn'],
                            "POType":3
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ChallanListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        