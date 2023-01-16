from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Invoices import *
from ..Serializer.S_Orders import *

from ..models import  *


class OrderDetailsForInvoice(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
               
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                Party = Orderdata['Party']
                Customer = Orderdata['Customer']
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderItemDetails = list()
               
                if POOrderIDs != '':
                    OrderQuery=T_Orders.objects.raw("SELECT t_orders.Supplier_id id,m_parties.Name SupplierName,sum(t_orders.OrderAmount) OrderAmount ,t_orders.Customer_id CustomerID FROM t_orders join m_parties on m_parties.id=t_orders.Supplier_id where t_orders.id IN %s group by t_orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                else:
                    query = T_Orders.objects.filter(OrderDate=FromDate,Supplier=Party,Customer=Customer)
                    Serializedata = OrderserializerforInvoice(query,many=True).data
                    Order_list = list()
                    for x in Serializedata:
                        Order_list.append(x['id'])
                   
                    OrderQuery=T_Orders.objects.raw("SELECT t_orders.Supplier_id id,m_parties.Name SupplierName,sum(t_orders.OrderAmount) OrderAmount ,t_orders.Customer_id CustomerID FROM t_orders join m_parties on m_parties.id=t_orders.Supplier_id where t_orders.id IN %s group by t_orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True)
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                       
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemSerializedata})
                for b in OrderItemSerializedata:
                    
                    Item= b['Item']['id']
                    obatchwisestockquery= O_BatchWiseLiveStock.objects.filter(Item_id=Item,Party_id=Party,BaseUnitQuantity__gt=0)
           
                   
                    if obatchwisestockquery == "":
                        StockQtySerialize_data =[]
                    else:
                        StockQtySerialize_data = StockQtyserializerForInvoice(obatchwisestockquery, many=True).data
                        stockDatalist = list()
                        for d in StockQtySerialize_data:
                            stockDatalist.append({
                                "id": d['id'],
                                "Item":d['Item'],
                                "BatchDate":d['LiveBatche']['BatchDate'],
                                "BatchCode":d['LiveBatche']['BatchCode'],
                                "SystemBatchDate":d['LiveBatche']['SystemBatchDate'],
                                "SystemBatchCode":d['LiveBatche']['SystemBatchCode'],
                                "BaseUnitQuantity":d['BaseUnitQuantity']   
                                })
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
                            "ConversionUnit": c['BaseUnitQuantity'],
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
                        "UnitDetails":UnitDetails,
                        "StockDetails":stockDatalist
                    })     
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': OrderItemDetails})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

class InvoiceListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                FromDate = Invoicedata['FromDate']
                ToDate = Invoicedata['ToDate']
                Customer = Invoicedata['Customer']
                Party = Invoicedata['Party']
               
                if(Customer == ''):
                    query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Party=Party)
                else:
                    query = T_Invoices.objects.filter(InvoiceDate__range=[FromDate, ToDate], Customer_id=Customer, Party=Party)
                   
                # return JsonResponse({'query': str(Orderdata.query)})
                if query:
                    Invoice_serializer = InvoiceSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer})
                    InvoiceListData = list()
                    for a in Invoice_serializer:
                        InvoiceListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount']  
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})








class InvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                Party = Invoicedata['Party']
                InvoiceDate = Invoicedata['InvoiceDate']
                # ==========================Get Max Invoice Number=====================================================
                a = GetMaxNumber.GetInvoiceNumber(Party,InvoiceDate)
                Invoicedata['InvoiceNumber'] = a
                b = GetPrifix.GetInvoicePrifix(Party)
                Invoicedata['FullInvoiceNumber'] = b+""+str(a)
                #================================================================================================== 
                InvoiceItems = Invoicedata['InvoiceItems']
                
                O_BatchWiseLiveStockList=list()
                for InvoiceItem in InvoiceItems:
                    O_BatchWiseLiveStockList.append({
                        "Quantity" : InvoiceItem['BatchID'],
                        "Item" : InvoiceItem['Item'],
                        "BaseUnitQuantity" : InvoiceItem['Quantity']
                    })
                        
                Invoicedata.update({"obatchwiseStock":O_BatchWiseLiveStockList}) 
                
                Invoice_serializer = InvoiceSerializer(data=Invoicedata)
                if Invoice_serializer.is_valid():
                    Invoice_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'Invoice Save Successfully', 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': Invoice_serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
    