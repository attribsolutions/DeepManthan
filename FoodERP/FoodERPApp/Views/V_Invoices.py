from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Invoices import *
from ..Serializer.S_Orders import *

from ..models import  *


class GetOrderDetailsForInvoice(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request, id=0):
        try:
            with transaction.atomic():
               
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                Customer = Orderdata['Customer']
                POOrderIDs = Orderdata['OrderIDs']
                Order_list = POOrderIDs.split(",")
                OrderData = list()
                OrderItemDetails = list()
               
                if POOrderIDs != '':
                    OrderQuery=T_Orders.objects.raw("SELECT t_orders.Supplier_id id,m_parties.Name SupplierName,sum(t_orders.OrderAmount) OrderAmount ,t_orders.Customer_id CustomerID FROM t_orders join m_parties on m_parties.id=t_orders.Supplier_id where t_orders.id IN %s group by t_orders.Supplier_id;",[Order_list])
                    OrderSerializedata = OrderSerializerForGrn(OrderQuery,many=True).data
                    OrderItemQuery=TC_OrderItems.objects.filter(Order__in=Order_list,IsDeleted=0).order_by('Item')
                    OrderItemSerializedata=TC_OrderItemSerializer(OrderItemQuery,many=True).data
                else:
                    
                    query = T_Orders.objects.raw("SELECT t_orders.id FROM t_orders where t_orders.OrderDate= %s and t_orders.Customer_id = %s ",[FromDate,Customer])
                    Serializedata = OrderserializerforInvoice(query,many=True).data
                    Order_list = list()
                    for x in Serializedata:
                        Order_list.append(x['id'])
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
        




# class T_InvoiceView(CreateAPIView):
    
#     permission_classes = (IsAuthenticated,)
#     authentication__Class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def get(self, request,id=0):
#         try:
#             with transaction.atomic():
#                 query = T_Invoices.objects.raw('''SELECT t_invoices.id,t_invoices.InvoiceDate,t_invoices.InvoiceNumber, t_invoices.FullInvoiceNumber,
#  t_invoices.CustomerGSTTin,t_invoices.GrandTotal,t_invoices.RoundOffAmount,t_invoices.CreatedBy,
#  t_invoices.CreatedOn, t_invoices.UpdatedBy, t_invoices.UpdatedOn,t_invoices.Customer_id,A.Name CustomerName,t_invoices.Party_id,B.Name PartyName,t_invoices.Order_id FROM t_invoices
# join m_parties A ON A.ID=t_invoices.Customer_id
# join m_parties B ON B.ID=t_invoices.Party_id
# ''')
#                 if not query:
#                     return JsonResponse({'StatusCode': 200, 'Status': True,'Message':  'Records Not available', 'Data': []})
#                 else:
#                     Invoice_serializer = T_InvoiceSerializerGETList(query, many=True).data
#                     return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': Invoice_serializer})
#         except Exception :
#             return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Exception Found', 'Data': []})

#     @transaction.atomic()
#     def post(self, request):
#         try:
#             with transaction.atomic():
#                 Invoicedata = JSONParser().parse(request)
#                 Invoice_serializer = T_InvoiceSerializer(data=Invoicedata)
#                 if Invoice_serializer.is_valid():
#                     Invoice_serializer.save()
#                     return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'Invoice Save Successfully', 'Data':[]})
#                 return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': Invoice_serializer.errors, 'Data':[]})
#         except Exception:
#             return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Exceptio Found', 'Data': []})

# class T_InvoicesViewSecond(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     authentication__Class = JSONWebTokenAuthentication

#     @transaction.atomic()
#     def get(self, request,id=0):
#         try:
#             with transaction.atomic():
#                 Invoicedata = T_Invoices.objects.get(id=id)
#                 Invoice_serializer = T_InvoiceSerializer(Invoicedata)
#                 return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': Invoice_serializer.data})
#         except T_Invoices.DoesNotExist:
#             return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'T_Invoices Not available', 'Data': []})
   

#     @transaction.atomic()
#     def put(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Invoiceupdatedata = JSONParser().parse(request)
#                 InvoiceupdateByID = T_Invoices.objects.get(id=id)
#                 Invoiceupdate_Serializer = T_InvoiceSerializer(InvoiceupdateByID, data=Invoiceupdatedata)
#                 if Invoiceupdate_Serializer.is_valid():
#                     Invoiceupdate_Serializer.save()
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Updated Successfully','Data':{}})
#                 return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Invoiceupdate_Serializer.errors ,'Data':[]})
#         except Exception  :
#             return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Exception Found', 'Data': []})               
        
#     @transaction.atomic()
#     def delete(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 Invoice_Data = T_Invoices.objects.get(id=id)
#                 Invoice_Data.delete()
#                 return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Message': 'Invoice Deleted Successfully', 'Data':[]})
#         except T_Invoices.DoesNotExist:
#             return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
#         except IntegrityError:   
#             return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'T_Invoices used in another tbale', 'Data': []})    
