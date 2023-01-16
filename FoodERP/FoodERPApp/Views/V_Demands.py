from typing import Concatenate
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_Demands import *
from ..Serializer.S_Items import *
from ..Serializer.S_PartyItems import *
from ..Serializer.S_Bom import *
from django.db.models import Sum
from ..models import *


class DemandView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Demanddata = JSONParser().parse(request)
                Division = Demanddata['Division']
                Customer = Demanddata['Customer']
                DemandDate = Demanddata['DemandDate']

                '''Get Max Demand Number'''
                a = GetMaxNumber.GetDemandNumber(Division, Customer, DemandDate)
                # return JsonResponse({'StatusCode': 200, 'Status': True,   'Data':[] })
                for aa in Demanddata['DemandItem']:
                    BaseUnitQuantity=UnitwiseQuantityConversion(aa['Item'],aa['Quantity'],aa['Unit'],0,0,0).GetBaseUnitQuantity()
                    Demanddata['BaseUnitQuantity'] =  BaseUnitQuantity 
                
                Demanddata['DemandNo'] = a
                '''Get Demand Prifix '''
                b = GetPrifix.GetDemandPrifix(Division)
                Demanddata['FullDemandNumber'] = b+""+str(a)
               
                Demand_serializer = DemandSerializer(data=Demanddata)
                if Demand_serializer.is_valid():
                    Demand_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Demand Save Successfully', 'Data': []})
                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Demand_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DemandViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Order_Data = T_Demands.objects.get(id=id)
                Order_Data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Order Deleted Successfully', 'Data': []})
        except T_Demands.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
