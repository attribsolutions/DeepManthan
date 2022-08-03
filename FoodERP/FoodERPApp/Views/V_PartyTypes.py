from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PartyTypes import *

from ..models import *



class PartyTypesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PartyTypesdata = M_PartyType.objects.all()
                if PartyTypesdata.exists():
                    PartyTypes_Serializer = PartyTypesSerializer(PartyTypesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': PartyTypes_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party Types Not Available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartyTypesdata = JSONParser().parse(request)
                PartyTypes_Serializer = PartyTypesSerializer(data=PartyTypesdata)
                if PartyTypes_Serializer.is_valid():
                    PartyTypes_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  PartyTypes_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
            

class PartyTypesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = M_PartyType.objects.raw('''SELECT m_partytype.id,m_partytype.Name,m_divisiontype.Name DivisionTypeName FROM m_partytype
JOIN m_divisiontype ON m_divisiontype.id=m_partytype.DivisionType_id
WHERE m_partytype.id = %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Party Type Not available', 'Data': []})
                else:    
                    PartyTypes_Serializer = PartyTypesSerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': PartyTypes_Serializer[0]})   
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
            

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                PartyTypedata = JSONParser().parse(request)
                PartyTypedataByID = M_PartyType.objects.get(id=id)
                PartyTypedata_Serializer = PartyTypesSerializer(
                    PartyTypedataByID, data=PartyTypedata)
                if PartyTypedata_Serializer.is_valid():
                    PartyTypedata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Type Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyTypedata_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

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

