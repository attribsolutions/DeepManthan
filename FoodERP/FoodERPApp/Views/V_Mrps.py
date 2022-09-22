from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Mrps import *

from ..Serializer.S_Parties import *

from ..models import *


class M_MRPsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 
                M_Mrpsdata = JSONParser().parse(request)
                M_Mrps_Serializer = M_MRPsSerializer(data=M_Mrpsdata,many=True)
            if M_Mrps_Serializer.is_valid():
                M_Mrps_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'MRP Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Mrps_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})