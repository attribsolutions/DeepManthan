import datetime
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_GRNs import *
from ..Serializer.S_Orders import *
from ..models import *
from django.db.models import *

# GRN List API

class GRNListFilterView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GRNdata = JSONParser().parse(request)
                FromDate = GRNdata['FromDate']
                ToDate = GRNdata['ToDate']
                Customer = GRNdata['Party']
                Supplier = GRNdata['Supplier']
                if(Supplier == ''):
                    query = T_GRNs.objects.filter(
                        GRNDate__range=[FromDate, ToDate], Customer_id=Customer)
                else:
                    query = T_GRNs.objects.filter(
                        GRNDate__range=[FromDate, ToDate], Customer_id=Customer, Party_id=Supplier)
                # return JsonResponse({'Data':str(query.query)})
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    GRN_serializer = T_GRNSerializerForGET(
                        query, many=True).data
                    GRNListData = list()
                    for a in GRN_serializer:
                        GRNListData.append({
                            "id": a['id'],
                            "GRNDate": a['GRNDate'],
                            "Customer": a['Customer']['id'],
                            "CustomerName": a['Customer']['Name'],
                            "GRNNumber": a['GRNNumber'],
                            "FullGRNNumber": a['FullGRNNumber'],
                            "InvoiceNumber": a['InvoiceNumber'],
                            "GrandTotal": a['GrandTotal'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "CreatedOn" : a['CreatedOn'],
                           

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

# GRN Save  API

class T_GRNView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GRNdata = JSONParser().parse(request)
                Customer = GRNdata['Customer']
                CreatedBy = GRNdata['CreatedBy']
                GRNDate = GRNdata['GRNDate']
                # print(GRNdata['GRNReferences'])

                # if R in GRNdata['GRNReferences']:
                #     Query =T_Orders.objects.filter(id=OrderID[0]).update(Inward=GRNReference_data['Inward'])
# ==========================Get Max GRN Number=====================================================
                a = GetMaxNumber.GetGrnNumber(Customer,GRNDate)
                GRNdata['GRNNumber'] = a
                b = GetPrifix.GetGrnPrifix(Customer)
                
                GRNdata['FullGRNNumber'] = b+""+str(a)
#================================================================================================== 
                item = ""
                query = T_GRNs.objects.filter(Customer_id=GRNdata['Customer']).values('id')
                O_BatchWiseLiveStockList=list()
                for a in GRNdata['GRNItems']:
                    
                    query1 = TC_GRNItems.objects.filter(Item_id=a['Item'], SystemBatchDate=date.today(), GRN_id__in=query).values('id')
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

                    BatchCode = SystemBatchCodeGeneration.GetGrnBatchCode(a['Item'], GRNdata['Customer'], b)
                    UnitwiseQuantityConversionobject=UnitwiseQuantityConversion(a['Item'],a['Quantity'],a['Unit'],0,0,0)
                    BaseUnitQuantity=UnitwiseQuantityConversionobject.GetBaseUnitQuantity()
                    
                    a['SystemBatchCode'] = BatchCode
                    a['SystemBatchDate'] = date.today()
                    a['BaseUnitQuantity'] = BaseUnitQuantity
                    O_BatchWiseLiveStockList.append({
                    "Item": a['Item'],
                    "Quantity": a['Quantity'],
                    "ItemExpiryDate":date.today()+ datetime.timedelta(days = query2[0]['Days']),
                    "Unit": a['Unit'],
                    "BaseUnitQuantity": BaseUnitQuantity,
                    "OriginalBaseUnitQuantity": BaseUnitQuantity,
                    "MRP": a['MRP'],
                    "Rate": a['Rate'],
                    "GST": a['GST'],
                    "Party": Customer,
                    "SystemBatchDate": a['SystemBatchDate'],
                    "SystemBatchCode": a['SystemBatchCode'],
                    "BatchDate": a['BatchDate'],
                    "BatchCode": a['BatchCode'],
                    "CreatedBy":CreatedBy,
                    
                    })

                # print(GRNdata)
                GRNdata.update({"O_BatchWiseLiveStockItems":O_BatchWiseLiveStockList}) 
                # print(GRNdata)   
                GRN_serializer = T_GRNSerializer(data=GRNdata)
                if GRN_serializer.is_valid():
                    # return JsonResponse({'Data':GRN_serializer.data})
                    GRN_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'GRN Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 400, 'Status': True,  'Message': GRN_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

#GRN Single Get API

class T_GRNViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                GRNdata = T_GRNs.objects.get(id=id)
                GRN_serializer = T_GRNSerializerForGET(GRNdata).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRN_serializer})
                GRNItemListData = list()
                for a in GRN_serializer['GRNItems']:
                    GRNItemListData.append({
                        "Item": a['Item']['id'],
                        "ItemName": a['Item']['Name'],
                        "Quantity": a['Quantity'],
                        "Unit": a['Unit']['id'],
                        "UnitName": a['Unit']['UnitID'],
                        "BaseUnitQuantity": a['BaseUnitQuantity'],
                        "MRP": a['MRP'],
                        "ReferenceRate": a['ReferenceRate'],
                        "Rate": a['Rate'],
                        "BasicAmount": a['BasicAmount'],
                        "TaxType": a['TaxType'],
                        "GST": a['GST']['id'],
                        "GSTPercentage": a['GST']['GSTPercentage'],
                        "HSNCode": a['GST']['HSNCode'],
                        "GSTAmount": a['GSTAmount'],
                        "Amount": a['Amount'],
                        "DiscountType": a['DiscountType'],
                        "Discount": a['Discount'],
                        "DiscountAmount": a['DiscountAmount'],
                        "CGST": a['CGST'],
                        "SGST": a['SGST'],
                        "IGST": a['IGST'],
                        "CGSTPercentage": a['CGSTPercentage'],
                        "SGSTPercentage": a['SGSTPercentage'],
                        "IGSTPercentage": a['IGSTPercentage'],
                        "BatchDate": a['BatchDate'],
                        "BatchCode": a['BatchCode'],
                        "SystemBatchDate": a['SystemBatchDate'],
                        "SystemBatchCode": a['SystemBatchCode'],
                    })

                GRNReferencesData = list()
                for r in GRN_serializer['GRNReferences']:
                    GRNReferencesData.append({
                        "Invoice": r['Invoice'],
                        "Order": r['Order'],
                        "ChallanNo": r['ChallanNo'],
                    })
                GRNListData = list()
                a = GRN_serializer
                GRNListData.append({
                    "id": a['id'],
                    "GRNDate": a['GRNDate'],
                    "Customer": a['Customer']['id'],
                    "CustomerName": a['Customer']['Name'],
                    "GRNNumber": a['GRNNumber'],
                    "FullGRNNumber": a['FullGRNNumber'],
                    "InvoiceNumber": a['InvoiceNumber'],
                    "GrandTotal": a['GrandTotal'],
                    "Party": a['Party']['id'],
                    "PartyName": a['Party']['Name'],
                    "CreatedBy": a['CreatedBy'],
                    "UpdatedBy": a['UpdatedBy'],
                    "GRNReferences": GRNReferencesData,
                    "GRNItems": GRNItemListData
                })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GRNListData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
 
# GRN DELETE API 
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                O_BatchWiseLiveStockData = O_BatchWiseLiveStock.objects.filter(GRN_id=id).values('OriginalBaseUnitQuantity','BaseUnitQuantity')
              
                for a in O_BatchWiseLiveStockData:
                    if (a['OriginalBaseUnitQuantity'] != a['BaseUnitQuantity']) :
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN Used in another Transaction', 'Data': []})   
                
                GRN_Data = T_GRNs.objects.get(id=id)
                GRN_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GRN Deleted Successfully', 'Data': []})
        except T_GRNs.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'T_GRN used in another tbale', 'Data': []})

# Get PO Details For Make GRN POST API 

class GetOrderDetailsForGrnView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                POOrderIDs = request.data['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderData = list()
                OrderItemDetails = list()
                
                OrderQuery=T_Orders.objects.raw("SELECT t_orders.Supplier_id id,m_parties.Name SupplierName,sum(t_orders.OrderAmount) OrderAmount ,t_orders.Customer_id CustomerID FROM t_orders join m_parties on m_parties.id=t_orders.Supplier_id where t_orders.id IN %s group by t_orders.Supplier_id;",[Order_list])
                OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                
                OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemSerializedata})
                for b in OrderItemSerializedata:
                        Item= b['Item']['id']
                        query = MC_ItemUnits.objects.filter(Item_id=Item,IsDeleted=0)
                        # print(query.query)
                        if query.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                            UnitDetails = list()
                            for c in Unitdata:
                                baseunitconcat=ShowBaseUnitQtyOnUnitDropDown(Item,c['id'],c['BaseUnitQuantity']).ShowDetails()
                                UnitDetails.append({
                                "Unit": c['id'],
                                "UnitName": c['UnitID']['Name'] + baseunitconcat,
                            })
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data':Unitdata})
                        OrderItemDetails.append({
                            "id": b['id'],
                            "Item": b['Item']['id'],
                            "ItemName": b['Item']['Name'],
                            "Quantity": b['Quantity'],
                            "MRP": b['MRP']['id'],
                            "MRPValue": b['MRP']['MRP'],
                            "Rate": b['Rate'],
                            "Unit": b['Unit']['id'],
                            "UnitName": b['Unit']['UnitID']['Name'],
                            "BaseUnitQuantity": b['BaseUnitQuantity'],
                            "GST": b['GST']['id'],
                            "HSNCode": b['GST']['HSNCode'],
                            "GSTPercentage": b['GST']['GSTPercentage'],
                            "Margin": b['Margin']['id'],
                            "MarginValue": b['Margin']['Margin'],
                            "BasicAmount": b['BasicAmount'],
                            "GSTAmount": b['GSTAmount'],
                            "CGST": b['CGST'],
                            "SGST": b['SGST'],
                            "IGST": b['IGST'],
                            "CGSTPercentage": b['CGSTPercentage'],
                            "SGSTPercentage": b['SGSTPercentage'],
                            "IGSTPercentage": b['IGSTPercentage'],
                            "Amount": b['Amount'],
                            "UnitDetails":UnitDetails
                        })     
                OrderData.append({
                "Supplier": OrderSerializedata[0]['id'],
                "SupplierName": OrderSerializedata[0]['SupplierName'],
                "OrderAmount": OrderSerializedata[0]['OrderAmount'],
                "Customer": OrderSerializedata[0]['CustomerID'],
                "OrderItem": OrderItemDetails,
            })
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    
