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
                M_DivisionType_data = M_DivisionType.objects.all()
                if M_DivisionType_data.exists():
                    M_DivisionType_serializer = M_DivisionTypeSerializer(M_DivisionType_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data':M_DivisionType_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Division Not available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   



class DivisionTypeViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
        