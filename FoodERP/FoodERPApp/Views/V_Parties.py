from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PartyTypes import PartyTypesSerializer

from ..Serializer.S_Parties import *

from ..models import *
        
class GetPartyTypeByDivisionTypeID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_PartyType_data = M_PartyType.objects.filter(DivisionType=id)
                if M_PartyType_data.exists():
                    M_PartyType_serializer = PartyTypesSerializer(M_PartyType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_PartyType_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Types Not available ', 'Data': []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})            
            
         

class M_PartiesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_Parties_data=M_Parties.objects.raw('''SELECT p.id,p.Name,p.PartyType_id,p.DivisionType_id,p.Company_id,p.Email,p.Address,p.PIN,p.State_id,p.District_id ,p.GSTIN,p.PAN,p.FSSAINo,p.FSSAIExipry,p.isActive,p.MobileNo
,p.AlternateContactNo,M_PartyType.Name PartyTypeName,M_DivisionType.Name DivisionTypeName,C_Companies.Name CompanyName,M_States.Name StateName,M_Districts.Name DistrictName,p.CreatedBy,p.CreatedOn,p.UpdatedBy,p.UpdatedOn
FROM M_Parties p
left join M_PartyType on M_PartyType.id=p.PartyType_id
left join M_DivisionType on M_DivisionType.id=p.DivisionType_id
left join C_Companies on C_Companies.id =p.Company_id
left join M_States on M_States.id=p.State_id
left join M_Districts on M_Districts.id=p.District_id''')
                if not M_Parties_data:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_PartiesSerializer1(M_Parties_data, many=True)    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Parties_serializer.data})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 
                M_Partiesdata = JSONParser().parse(request)
                M_Parties_Serializer = M_PartiesSerializer(data=M_Partiesdata)
            if M_Parties_Serializer.is_valid():
                M_Parties_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' :[]})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})


class M_PartiesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Parties_data=M_Parties.objects.raw('''SELECT p.id,p.Name,p.PartyType_id,p.DivisionType_id,p.Company_id,p.Email,p.Address,p.PIN,p.State_id,p.District_id ,p.GSTIN,p.PAN,p.FSSAINo,p.FSSAIExipry,p.isActive,p.MobileNo
,M_PartyType.Name PartyTypeName,M_DivisionType.Name DivisionTypeName,C_Companies.Name CompanyName,M_States.Name StateName,M_Districts.Name DistrictName,p.CreatedBy,p.CreatedOn,p.UpdatedBy,p.UpdatedOn
FROM M_Parties p
left join M_PartyType on M_PartyType.id=p.PartyType_id
left join M_DivisionType on M_DivisionType.id=p.DivisionType_id
left join C_Companies on C_Companies.id =p.Company_id
left join M_States on M_States.id=p.State_id
left join M_Districts on M_Districts.id=p.District_id
 WHERE p.id  = %s''',[id])
                if not M_Parties_data:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_PartiesSerializer1(M_Parties_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_Parties_serializer.data[0]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_PartiesdataByID = M_Parties.objects.get(id=id)
                M_Parties_Serializer = M_PartiesSerializer(
                    M_PartiesdataByID, data=M_Partiesdata)
                if M_Parties_Serializer.is_valid():
                    M_Parties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' : []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Exception Found','Data' : []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(id=id)
                M_Partiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully', 'Data':[]})
        except M_Parties.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party used in another table', 'Data': []})    