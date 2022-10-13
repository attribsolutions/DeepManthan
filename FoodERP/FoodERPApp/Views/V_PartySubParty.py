from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PartySubParty import *
from ..Serializer.S_CompanyGroup import *

from ..models import *


class PartySubPartyView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                PartySubpartiesdata = MC_PartySubParty.objects.all()
                if PartySubpartiesdata.exists():
                    PartySubParty_Serializer = PartySubpartySerializer(PartySubpartiesdata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': PartySubParty_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Company Groups Not available', 'Data': []})        
        except Exception  :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data':[]})
            
