from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Routes import *
from ..Serializer.S_PartySubParty import *
from ..models import *

class RouteListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        try:
            with transaction.atomic():
                Routesdata = JSONParser().parse(request)
                Company = Routesdata['Company']
                Party = Routesdata['Party']
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
    authentication_class = JSONWebTokenAuthentication
    
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
        
  
class RoutesUpdateView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartySubpartiesdata = JSONParser().parse(request)
                PartySubparties_Serializer = PartySubPartySerializer(data=PartySubpartiesdata, many=True)
               
                if PartySubparties_Serializer.is_valid():
                    
                    PartySubpartiesdata1 = MC_PartySubParty.objects.filter(Party=PartySubpartiesdata[0]['PartyID'])
                    PartySubpartiesdata1.delete()
                    PartySubpartiesdata2 = MC_PartySubParty.objects.filter(SubParty=PartySubpartiesdata[0]['PartyID'],Party__PartyType=3).select_related('Party')
                    PartySubpartiesdata2.delete()
                    PartySubparties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartySubparties_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
          
           



