from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_DivisionTypes import *
from ..models import *


class DivisionTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                DivisionTypesdata = M_DivisionType.objects.all()
                if DivisionTypesdata.exists():
                    DivisionTypesdata_serializer = DivisionTypeSerializer(DivisionTypesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': DivisionTypesdata_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Division Not available', 'Data': []})    
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception' , 'Data':[]})


    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                DivisionTypesdata = JSONParser().parse(request)
                DivisionTypes_Serializer = DivisionTypeSerializer(data=DivisionTypesdata)
                if DivisionTypes_Serializer.is_valid():
                    DivisionTypes_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Division Type Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  DivisionTypes_Serializer.errors, 'Data':[]})
        except Exception   :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception'  , 'Data':[]})
            


class DivisionTypeViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_DivisionType.objects.raw('''SELECT m_divisiontype.id,m_divisiontype.Name,m_divisiontype.IsSCM FROM m_divisiontype

WHERE m_divisiontype.id = %s''',[id])
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Division Type Not available', 'Data': []})
                else:    
                    PartyTypes_Serializer = DivisionTypeSerializer2(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': PartyTypes_Serializer[0]})   
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data': []})
            
        
    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                DivisionTypesdata = JSONParser().parse(request)
                DivisionTypesdataByID = M_DivisionType.objects.get(id=id)
                DivisionTypesdata_Serializer = DivisionTypeSerializer(
                    DivisionTypesdataByID, data=DivisionTypesdata)
                if DivisionTypesdata_Serializer.is_valid():
                    DivisionTypesdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Division Type Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': DivisionTypesdata_Serializer.errors, 'Data':[]})
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception', 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                DivisionTypedata = M_DivisionType.objects.get(id=id)
                DivisionTypedata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Division Type Deleted Successfully', 'Data':[]})
        except M_DivisionType.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Division Type Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Division Type used in another table', 'Data': []})   


        