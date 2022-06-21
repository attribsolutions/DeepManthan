from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Orders import *



from ..models import  *

      


class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                # Orderdata = T_Orders.objects.all()
                OrderListData=list()
                Orderdata = T_Orders.objects.raw('''SELECT t_orders.id,t_orders.OrderDate,t_orders.CustomerID,t_orders.PartyID,t_orders.OrderAmount,t_orders.Discreption,party.name partyName,customer.name customerName ,t_orders.CreatedBy,t_orders.CreatedOn 
                FROM t_orders
join m_parties party on party.ID=t_orders.PartyID
join m_parties customer on customer.ID=t_orders.CustomerID ''')
                # print(str(Orderdata.query))
                Order_serializer = T_OrderSerializerforGET(
                    Orderdata, many=True).data
                for a in Order_serializer:   
                    OrderListData.append({
                        
                        "ID": a['id'],
                        "OrderDate": a['OrderDate'],
                        "CustomerID": a['CustomerID'],
                        "CustomerName": a['customerName'],
                        "PartyID": a['PartyID'],
                        "PartyName": a['partyName'],
                        "OrderAmount": a['OrderAmount'],
                        "Discreption": a['Discreption'],
                        
                    }) 

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': OrderListData})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                Order_serializer = T_OrderSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully'})
                return JsonResponse({'StatusCode': 400, 'Status': True,  'Message': Order_serializer.errors})
        except Exception as e:
            raise Exception(e)

class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                
                OrderListData=list()
                Orderdata = T_Orders.objects.raw('''SELECT t_orders.id,t_orders.OrderDate,t_orders.CustomerID,t_orders.PartyID,t_orders.OrderAmount,t_orders.Discreption,party.name partyName,customer.name customerName ,t_orders.CreatedBy,t_orders.CreatedOn 
                FROM t_orders
join m_parties party on party.ID=t_orders.PartyID
join m_parties customer on customer.ID=t_orders.CustomerID where t_orders.id= %s''', [id])
                # print(str(Orderdata.query))
                Order_serializer = T_OrderSerializerforGET(Orderdata, many=True).data
                OrderItemsListData=list()
                bb=TC_OrderItems.objects.filter(OrderID=id)
#                 bb=TC_OrderItems.objects.raw('''SELECT m_items.name ItemName,tc_orderitems.ItemID_id ,tc_orderitems.Quantity,tc_orderitems.MRP,tc_orderitems.Rate,tc_orderitems.UnitID,tc_orderitems.BaseUnitQuantity,
#  tc_orderitems.GST FROM tc_orderitems
#  join m_items on m_items.ID=tc_orderitems.ItemID_id where tc_orderitems.OrderID_id=%s''', [id])
                OrderItems_data = TC_OrderItemsSerializer(bb, many=True).data












                for a in Order_serializer:
                    OrderListData.append({
                        
                        "ID": a['id'],
                        "OrderDate": a['OrderDate'],
                        "CustomerID": a['CustomerID'],
                        "CustomerName": a['customerName'],
                        "PartyID": a['PartyID'],
                        "PartyName": a['partyName'],
                        "OrderAmount": a['OrderAmount'],
                        "Discreption": a['Discreption'],
                        "OrderItem" : OrderItems_data
                    }) 

       
                    

                    
                    
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': OrderListData})
                
        except Exception as e:
            raise Exception(e)
            print(e)     

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Order_Data = T_Orders.objects.get(id=id)
                Order_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully'})
        except Exception as e:
            raise Exception(e)

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Orderupdatedata = JSONParser().parse(request)
                OrderupdateByID = T_Orders.objects.get(id=id)
                
                Orderupdate_Serializer = T_OrderSerializer(OrderupdateByID, data=Orderupdatedata)
                if Orderupdate_Serializer.is_valid():
                    Orderupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Updated Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Orderupdate_Serializer.errors})
        except Exception as e:
            raise Exception(e)
            print(e)                  