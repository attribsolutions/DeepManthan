from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from rest_framework.parsers import JSONParser
from ..Serializer.S_CentralServiceItemMaster import *
from ..models import *

class CentralServiceItemView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                ServiceItem_data = M_CentralServiceItems.objects.all()
                ServiceItem_Serializer = CentralServiceItemSerializer(ServiceItem_data,many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': ServiceItem_Serializer.data})
        except  M_CentralServiceItems.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Central service item save Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
   
    def post(self, request):
        try:
            with transaction.atomic():
                ServiceItem_data = JSONParser().parse(request)
                ServiceItem_Serializer = CentralServiceItemSerializer(data=ServiceItem_data)
                if ServiceItem_Serializer.is_valid():
                    ServiceItem_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Central service item save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  ServiceItem_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
class CentralServiceItemViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ServiceItem_data = M_CentralServiceItems.objects.get(id=id)
                ServiceItem_Serializer = CentralServiceItemSerializer(ServiceItem_data).data
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': ServiceItem_Serializer})
        except  M_CentralServiceItems.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Central Service Item Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                ServiceItem_data = JSONParser().parse(request)
                ServiceItem_SerializerByID = M_CentralServiceItems.objects.get(id=id)
                ServiceItem_serializer = CentralServiceItemSerializer(ServiceItem_SerializerByID, data=ServiceItem_data)
                if ServiceItem_serializer.is_valid():
                    ServiceItem_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Central Service Item Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ServiceItem_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = M_CentralServiceItems.objects.get(id=id)
                Cluster_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Central Service Item Data Deleted Successfully','Data':[]})
        except M_CentralServiceItems.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Central Service Item Data Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Central Service Item Data used in another table', 'Data': []})
                
                
class CentralServiceItemAssignFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ServiceItemdata = JSONParser().parse(request)
                PartyID=ServiceItemdata['PartyID'] 
                CompanyID=ServiceItemdata['ServiceItemdata']
                ServiceItemquery= M_CentralServiceItems.objects.raw('''SELECT distinct M_CentralServiceItems.id,M_CentralServiceItems.Name,ifnull(MC_CentralServiceItemAssign.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName 
FROM M_CentralServiceItems
LEFT JOIN MC_CentralServiceItemAssign ON MC_CentralServiceItemAssign.CentralServiceItem_id=M_CentralServiceItems.id AND MC_CentralServiceItemAssign.Party_id=97 
LEFT JOIN M_Parties ON M_Parties.id=MC_CentralServiceItemAssign.Party_id where M_CentralServiceItems.Company_id =%s''',([PartyID],[CompanyID]))
                
                if not ServiceItemquery:
                    
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Central Service Items Not available', 'Data': []})
                else:
                    ServiceItems_Serializer = MC_CentralServiceItemAssignSerializer(ServiceItemquery, many=True).data
                    ServiceItemList = list()
                    for a in ServiceItems_Serializer:
                        ServiceItemList.append({
                            "ServiceItem": a['id'],
                            "ServiceItemName": a['Name'],
                            "Party": a['Party_id'], 
                            "PartyName": a['PartyName'],
                        })
                   
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ServiceItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})  
        
        
class CentralServiceItemAssignForParty(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PartyItems_data = JSONParser().parse(request)
                PartyItems_serializer = MC_CentralServiceItemAssignSerializerSecond(data=PartyItems_data, many=True)
                if PartyItems_serializer.is_valid():
                    id = PartyItems_serializer.data[0]['Party']
                    ServiceItemParty_data = MC_CentralServiceItemAssign.objects.filter(Party=id)
                    ServiceItemParty_data.delete()
                    ServiceItem = PartyItems_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CentralServiceItemForParty Save Successfully', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        
        
                      