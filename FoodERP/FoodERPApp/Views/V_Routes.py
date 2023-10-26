from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Routes import *
from ..Serializer.S_PartySubParty import *
from ..models import *
from ..Serializer.S_Orders import *

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
                    log_entry = create_transaction_logNew(request, Routesdata,Party,'',228,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Routesdata})
                log_entry = create_transaction_logNew(request, Routesdata,Party,'Routes Not available',228,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Routes Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'RouteList:'+str(Exception(e)),33,0)
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
                    Routes = Routes_Serializer.save()
                    LastInsertID = Routes.id
                    log_entry = create_transaction_logNew(request,Routes_data,Routes_data['Party'],'TransactionID:'+str(LastInsertID),16,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Route Save Successfully','TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Routes_data,0,'RoutesSave:'+str( Routes_Serializer.errors),16,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Routes_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'RoutesSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Routequery = M_Routes.objects.filter(id=id)
                if Routequery.exists():
                    Routesdata = RoutesSerializer(Routequery, many=True).data
                    log_entry = create_transaction_logNew(request, Routesdata,Routesdata[0]['Party'],'TransactionID:'+str(id),229,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Routesdata[0]})
                log_entry = create_transaction_logNew(request, Routesdata,0,'Details Not available',229,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Routes Not available ', 'Data': []})
        except M_Routes.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Routes Not available',229,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Routes Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'Single Route'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Routesdata = JSONParser().parse(request)
                RoutesdataByID = M_Routes.objects.get(id=id)
                Routesdata_Serializer = RoutesSerializer(RoutesdataByID, data=Routesdata)
                if Routesdata_Serializer.is_valid():
                    Routes = Routesdata_Serializer.save()
                    LastInsertID = Routes.id
                    log_entry = create_transaction_logNew(request,Routesdata,Routesdata['Party'],'TransactionID:'+str(LastInsertID),17,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Routes Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Routesdata,0,'Route Edit:'+str(Routesdata_Serializer.errors),17,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Routesdata_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'Route Edit:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Routesdata = M_Routes.objects.get(id=id)
                Routesdata.delete()
                log_entry = create_transaction_logNew(request,{'RouteID':id},0,'RouteID:'+str(id),18,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Routes Deleted Successfully', 'Data':[]})
        except M_Routes.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Routes Not available',18,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Routes Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request, 0,0,'Routes used in another table',8,0)
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message':'Routes used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'RouteDelete:'+str(Exception(e)),33,0)
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
                
                q1 = M_Parties.objects.filter(id__in=q0).values("id")
                    
                query = MC_PartySubParty.objects.filter(SubParty__in=q1,Party=Party) 
                
                if query.exists():
                    SubPartydata = RoutesUpdateListSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartydata})
                    SubPartyListData = list()
                    for a in SubPartydata:
                        SubPartyListData.append({
                            "id": a['id'],
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "SubParty": a['SubParty']['id'],
                            "SubPartyName": a['SubParty']['Name'],
                            "Route":a['Route']['id'],
                            "RouteName":a['Route']['Name']
                        })
                    log_entry = create_transaction_logNew(request, PartySubpartydata,Party,'',230,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyListData})
                log_entry = create_transaction_logNew(request, PartySubpartydata,Party,'PartyRoute  Not available',230,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Route  Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'RouteUpdateList:'+str(Exception(e)),33,0)
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
                        log_entry = create_transaction_logNew(request, PartySubPartydata,a['Party'],'Route Not Updated',231,0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Route Not Updated', 'Data': []})     
                log_entry = create_transaction_logNew(request, PartySubPartydata,a['Party'],'',231,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Route Updated Successfully', 'Data': []})  
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'PartyRouteUpdate:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})             



