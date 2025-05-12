from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyTypes import *
from ..models import *
from django.db.models import Q
from .V_CommFunction import *

class PartyTypeListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartyType_Data = JSONParser().parse(request)
             
                UserID = PartyType_Data['UserID']   
                RoleID=  PartyType_Data['RoleID']  
                CompanyID = PartyType_Data['CompanyID']  
                IsSCM=PartyType_Data['IsSCMCompany'] 
                id=PartyType_Data['id']                 
                
                if (id == 0):
                    
                    if(CompanyID == 0):
                        query = M_PartyType.objects.all()
                        p=0
                    else:    
                        if(IsSCM == 0):
                        
                            q= C_Companies.objects.filter(id=CompanyID).values("CompanyGroup")                            
                            q0=C_Companies.objects.filter(IsSCM=1,CompanyGroup=q[0]['CompanyGroup']).values('id')                           
                            if q0:
                                query = M_PartyType.objects.filter(Q(Company=CompanyID  ) | Q(Company=q0[0]['id'])) 
                            else:
                                query = M_PartyType.objects.filter(Q(Company=CompanyID  ))
                            p=0
                        else:                        
                            query = M_PartyType.objects.filter(IsSCM=IsSCM,Company=CompanyID)                        
                            p=0
                else:    
                    
                    
                    query = M_PartyType.objects.filter(id=id)
                    p=1
                
                if not query:
                    log_entry = create_transaction_logNew(request,PartyType_Data,0,'PartyType Not available',185,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Party Type Not available', 'Data':[]})
                else:    
                    PartyTypes_Serializer = PartTypeSerializerSecond(query, many=True).data
                    if p==0:
                        data=PartyTypes_Serializer
                    else:
                        data=PartyTypes_Serializer[0]    
                    log_entry = create_transaction_logNew(request,PartyType_Data,PartyType_Data['PartyID'],'',185,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': data})   
        except Exception as e:
                log_entry = create_transaction_logNew(request,0,0,'PartyTypeList:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class PartyTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartyTypedata = JSONParser().parse(request)
                PartyTypedata_Serializer = PartyTypeSerializer(data=PartyTypedata)
                if PartyTypedata_Serializer.is_valid():
                    PartyType = PartyTypedata_Serializer.save()
                    LastInsertID = PartyType.id
                    log_entry = create_transaction_logNew(request,PartyTypedata,0,'TransactionID:'+str(LastInsertID),186,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Save Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,PartyTypedata,0,'PartyTypeSave:'+str(PartyTypedata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PartyTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0,0,'PartyTypeSave:'+str(Exception(e)),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
            
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                PartyTypedata = JSONParser().parse(request)
                PartyTypedataByID = M_PartyType.objects.get(id=id)
                PartyTypedata_Serializer = PartyTypeSerializer(
                    PartyTypedataByID, data=PartyTypedata)
                if PartyTypedata_Serializer.is_valid():
                    PartyTypedata_Serializer.save()
                    log_entry = create_transaction_logNew(request,PartyTypedata,0,'Company:'+str(PartyTypedata['Company']),187,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,PartyTypedata,0,'PartyTypeEdit:'+str(PartyTypedata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
                log_entry = create_transaction_logNew(request,0,0,Exception(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PartyTypedata = M_PartyType.objects.get(id=id)
                PartyTypedata.delete()
                log_entry = create_transaction_logNew(request,{'PartyTypeID':id},0,'PartyTypeID:'+str(id),188,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Deleted Successfully', 'Data':[]})
        except M_PartyType.DoesNotExist:
            log_entry = create_transaction_logNew(request,{'PartyTypeID':id},0,'PartyTypeDelete:'+'Party Type Not available',188,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Type Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request,0,0,'PartyTypeDelete:'+'Party Type used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Type used in another table', 'Data': []})   


    
  
                
        