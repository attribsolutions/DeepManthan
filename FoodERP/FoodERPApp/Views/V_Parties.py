from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Parties import *



from ..models import *

class M_PartyTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_PartyType_data = M_PartyType.objects.all()
                if M_PartyType_data.exists():
                    M_PartyType_serializer = M_PartyTypeSerializer(M_PartyType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_PartyType_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Types Not Available', 'Data': []})
        except Exception as e:
           return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            
class GetPartyTypeByDivisionTypeID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_PartyType_data = M_PartyType.objects.filter(DivisionTypeID=id)
                if M_PartyType_data.exists():
                    M_PartyType_serializer = M_PartyTypeSerializer(M_PartyType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_PartyType_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Types Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})            
            
class M_DivisionTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_DivisionType_data = M_DivisionType.objects.all()
                if M_DivisionType_data.exists():
                    M_DivisionType_serializer = M_DivisionTypeSerializer(M_DivisionType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data':M_DivisionType_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Division Not available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})            

class M_PartiesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_Parties_data=M_Parties.objects.raw('''SELECT p.ID,p.Name,p.PartyTypeID,p.DividionTypeID,p.companyID,p.CustomerDivision,p.Email,p.Address,p.PIN,p.State,p.District,p.GSTN,p.FSSAINo,p.FSSAIExipry,p.IsActive
,m_partytype.Name PartyType,m_divisiontype.Name DivisionType,c_companies.Name CompanyName,M_States.Name StateName
FROM m_parties p
left join M_PartyType on m_partytype.id=p.PartyTypeID
left join M_DivisionType on m_divisiontype.id=p.DividionTypeID
left join C_Companies on c_companies.ID =p.companyID
left join M_States on M_states.id=p.state''')
                if not M_Parties_data:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_Partiesserializer1(M_Parties_data, many=True)    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Parties_serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

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
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class M_PartiesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Parties_data=M_Parties.objects.raw('''SELECT p.ID,p.Name,p.PartyTypeID,p.DividionTypeID,p.companyID,p.CustomerDivision,p.Email,p.Address,p.PIN,p.State,p.District,p.GSTN,p.FSSAINo,p.FSSAIExipry,p.IsActive
,m_partytype.Name PartyType,m_divisiontype.Name DivisionType,c_companies.Name CompanyName,M_States.Name StateName
FROM m_parties p
left join M_PartyType on m_partytype.id=p.PartyTypeID
left join M_DivisionType on m_divisiontype.id=p.DividionTypeID
left join C_Companies on c_companies.ID =p.companyID
left join M_States on M_states.id=p.state where p.ID = %s''',[id])
               
                M_Parties_serializer = M_Partiesserializer1(M_Parties_data, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_Parties_serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_PartiesdataByID = M_Parties.objects.get(ID=id)
                M_Parties_Serializer = M_PartiesSerializer(
                    M_PartiesdataByID, data=M_Partiesdata)
                if M_Parties_Serializer.is_valid():
                    M_Parties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(ID=id)
                M_Partiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully', 'Data':[]})
        except M_Parties.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Not available', 'Data': []})    
            