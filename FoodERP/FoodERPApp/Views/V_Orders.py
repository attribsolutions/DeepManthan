from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Orders import *

from ..models import  *
class TermsAndCondtions(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication  

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                Order_serializer = M_TermsAndConditionsSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'TermsAndCondtions Save Successfully' , 'Data':[] })
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors , 'Data':[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':'Exception Found','Data': []})   

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Modulesdata = M_TermsAndConditions.objects.all()
                if Modulesdata.exists():
                    Modules_Serializer = M_TermsAndConditionsSerializer(
                    Modulesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Modules_Serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'TermsAndConditions Not available', 'Data': []})    
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

class T_OrdersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Orderdata = T_Orders.objects.all().order_by('-id')
                # return JsonResponse({'query': str(Orderdata.query)})
                if Orderdata:
                    Order_serializer = T_OrderSerializerSecond(Orderdata, many=True).data
                    OrderListData = list()
                    for a in Order_serializer:   
                        OrderListData.append({
                        "id": a['id'],
                        "OrderDate": a['OrderDate'],
                        "Customer": a['Customer']['Name'],
                        "Supplier": a['Supplier']['Name'],
                        "OrderAmount": a['OrderAmount'],
                        "Description": a['Description'],
                        "CreatedBy" : a['CreatedBy'],
                        "CreatedOn" : a['CreatedOn']
                        
                        }) 
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': OrderListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':'Exception Found','Data': []})
             
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                Order_serializer = T_OrderSerializer(data=Orderdata)
                if Order_serializer.is_valid():
                    Order_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Order Save Successfully' , 'Data':[] })
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Order_serializer.errors , 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class T_OrdersViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Orderupdatedata = JSONParser().parse(request)
                OrderupdateByID = T_Orders.objects.get(id=id)
                
                Orderupdate_Serializer = T_OrderSerializer(OrderupdateByID, data=Orderupdatedata)
                if Orderupdate_Serializer.is_valid():
                    Orderupdate_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Updated Successfully','Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Orderupdate_Serializer.errors ,'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':'Exception Found','Data': []})  
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Order_Data = T_Orders.objects.get(id=id)
                Order_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully','Data':[]})
        except T_Orders.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'T_Orders used in another tbale', 'Data': []}) 

                