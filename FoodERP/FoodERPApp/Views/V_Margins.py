from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Margins import *

from ..Serializer.S_Parties import *

from ..models import *


class M_MarginsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 
                M_Marginsdata = JSONParser().parse(request)
                M_Margins_Serializer = M_MarginsSerializer(data=M_Marginsdata,many=True)
            if M_Margins_Serializer.is_valid():
                M_Margins_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Margins Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Margins_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})