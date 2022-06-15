from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Orders import T_OrderSerializer



from ..models import  *

      


class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Orderdata = T_Orders.objects.all()
                Order_serializer = T_OrderSerializer(
                    Orderdata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Order_serializer.data})
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
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': Order_serializer.errors})
        except Exception as e:
            raise Exception(e)

class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Orderdata = T_Orders.objects.filter(id=id)
                Order_serializer = T_OrderSerializer(
                    Orderdata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': Order_serializer.data})
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