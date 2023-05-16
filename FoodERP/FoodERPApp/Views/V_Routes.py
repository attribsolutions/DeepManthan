from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Routes import *
from ..Serializer.S_PartySubParty import *
from ..models import *


class RouteListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                Routesdata = JSONParser().parse(request)
                Company = Routesdata['CompanyID']
                Party = Routesdata['PartyID']
                Routequery = M_Routes.objects.filter(Party=Party,Company=Company)
                if Routequery.exists():
                    Routesdata = RoutesSerializer(Routequery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Routesdata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Routes Not available ', 'Data': []})
        except M_Routes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Routes Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
     
class RoutesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Routes_data = JSONParser().parse(request)
                Routes_Serializer = RoutesSerializer(data=Routes_data)
                if Routes_Serializer.is_valid():
                    Routes_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Route Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Routes_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Routequery = M_Routes.objects.filter(id=id)
                if Routequery.exists():
                    Routesdata = RoutesSerializer(Routequery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Routesdata[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Routes Not available ', 'Data': []})
        except M_Routes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Routes Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Routesdata = JSONParser().parse(request)
                RoutesdataByID = M_Routes.objects.get(id=id)
                Routesdata_Serializer = RoutesSerializer(RoutesdataByID, data=Routesdata)
                if Routesdata_Serializer.is_valid():
                    Routesdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Routes Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Routesdata_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Routesdata = M_Routes.objects.get(id=id)
                Routesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Routes Deleted Successfully', 'Data':[]})
        except M_Routes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Routes Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Routes used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
  
class RoutesUpdateListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                PartySubpartydata = JSONParser().parse(request)
                Party = PartySubpartydata['PartyID']
                      
                
                q0 = MC_PartySubParty.objects.filter(Party = Party).values("SubParty")
              
                q1 = M_Parties.objects.filter(id__in = q0,PartyType__IsRetailer=1).select_related("PartyType") 
               
                query = MC_PartySubParty.objects.filter(SubParty__in=q1) 
                
                if query.exists():
                    SubPartydata = RoutesUpdateListSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartydata})
                    SubPartyListData = list()
                    for a in SubPartydata:
                        SubPartyListData.append({
                            "id": a['id'],
                            "Party": a['Party']['id'],
                            "SubParty": a['SubParty']['id'],
                            "SubPartyName": a['SubParty']['Name'],
                            "Route":a['Route']['id'],
                            "RouteName":a['Route']['Name']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Creditlimit  Not available ', 'Data': []})
        except MC_PartySubParty.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Creditlimit Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
          

class RoutesUpdateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                PartySubPartydata = JSONParser().parse(request)
                for a in PartySubPartydata['Data']:
                    if(a['Route']!= ""):
                        query = MC_PartySubParty.objects.filter(id=a['id'],Party=a['Party'],SubParty=a['SubParty']).update(Route=a['Route']) 
                    else:
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Route Not Updated', 'Data': []})     
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Route Updated Successfully', 'Data': []})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})             



