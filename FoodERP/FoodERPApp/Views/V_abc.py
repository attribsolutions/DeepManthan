from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser,MultiPartParser, FormParser

from ..Views.V_CommFunction import GetO_BatchWiseLiveStock

from ..Serializer.S_Orders import TC_OrderTermsAndConditionsSerializer

from ..Serializer.S_abc import *
from ..models import *


class AbcView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    parser_classes = (MultiPartParser, FormParser)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                file_serializer =  TC_OrderTermsAndConditionsSerializer(data=request.data)
                if file_serializer.is_valid():
                    file_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'File Uploaded Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': file_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                print('aaaaa')
                Modulesdata = TC_OrderTermsAndConditions.objects.filter(Order=201)
                print('bbbbb')
                if Modulesdata.exists():
                    print('ccccc')
                    Modules_Serializer = TC_OrderTermsAndConditionsSerializer(
                    Modulesdata, many=True)
                    Stock=GetO_BatchWiseLiveStock(44,4)
                    print(Stock)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': float(Stock),'Data': Modules_Serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Modules Not available', 'Data': []})    
        except Exception as e :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[e]})
         