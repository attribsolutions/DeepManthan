from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyTypes import *
from ..models import *


class PartyTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PartyTypedata = M_PartyType.objects.all()
                if PartyTypedata.exists():
                    PartyTypedata_serializer = PartyTypeSerializer(PartyTypedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': PartyTypedata_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party Type available', 'Data': []})    
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception' , 'Data':[]})


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
        except Exception   :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception'  , 'Data':[]})
            


class PartyTypeViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_PartyType.objects.raw('''SELECT m_partytype.id,m_partytype.Name,m_partytype.IsSCM FROM m_partytype

WHERE m_partytype.id = %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Party Type Not available', 'Data': []})
                else:    
                    PartyTypes_Serializer = PartyTypeSerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': PartyTypes_Serializer[0]})   
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data': []})
            
        
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
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
        

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


        