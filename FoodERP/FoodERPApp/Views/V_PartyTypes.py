from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyTypes import *
from ..models import *


class PartyTypeListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
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
                    
                    if(IsSCM == 0):
                       
                        query = M_PartyType.objects.filter(Company=CompanyID)
                        p=0
                    else:
                       
                        query = M_PartyType.objects.filter(IsSCM=IsSCM,Company=CompanyID)
                        print(str(query.query))
                        p=0
                else:    
                    
                    query = M_PartyType.objects.filter(id=id)
                    p=1
                
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Party Type Not available', 'Data':[]})
                else:    
                    PartyTypes_Serializer = PartyTypeSerializer(query, many=True).data
                    if p==0:
                        data=PartyTypes_Serializer
                    else:
                        data=PartyTypes_Serializer[0]    
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': data})   
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class PartyTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartyTypedata = JSONParser().parse(request)
                PartyTypedata_Serializer = PartyTypeSerializer(data=PartyTypedata)
                if PartyTypedata_Serializer.is_valid():
                    PartyTypedata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PartyTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            
        
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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PartyTypedata = M_PartyType.objects.get(id=id)
                PartyTypedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Deleted Successfully', 'Data':[]})
        except M_PartyType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Type Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Type used in another table', 'Data': []})   


    
  
                
        