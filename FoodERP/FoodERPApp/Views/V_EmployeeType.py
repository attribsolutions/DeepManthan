from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_M_EmployeeType import  *

from ..models import *

class M_EmployeeTypeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                M_EmployeeTypedata = M_EmployeeType.objects.all()
                M_EmployeeType_serializer = M_EmployeeTypeSerializer(M_EmployeeTypedata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_EmployeeType_serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                M_EmployeeTypedata = JSONParser().parse(request)
                M_EmployeeType_serializer = M_EmployeeTypeSerializer(data=M_EmployeeTypedata)
                if M_EmployeeType_serializer.is_valid():
                    M_EmployeeType_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Designation Save Successfully'})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  M_EmployeeType_serializer.errors})
        except Exception as e:
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  Exception(e)})
            print(e)        
 