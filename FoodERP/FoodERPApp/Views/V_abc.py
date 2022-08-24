from genericpath import exists
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from  ..Serializer.S_abc import *
from ..models import *

 
class AbcView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                Abcdata = Abc.objects.all()
                if Abcdata.exists():
                    Abc_Serializer = AbcSerializer(Abcdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': Abc_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Data Not available', 'Data': []})        
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data':[]})
            
    
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Rolesdata = JSONParser().parse(request)
                M_Roles_Serializer = AbcSerializer(data=M_Rolesdata)
            if M_Roles_Serializer.is_valid():
                M_Roles_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Roles_Serializer.errors, 'Data' : []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})

    
