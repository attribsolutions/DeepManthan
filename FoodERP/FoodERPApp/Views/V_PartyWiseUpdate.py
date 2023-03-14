from ..models import MC_PartySubParty
from ..Serializer.S_PartyWiseUpdate import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser


class PartyWiseUpdateView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Party_data = JSONParser().parse(request)
                Party = Party_data['PartyID']
                Route = Party_data['Route']
                query = MC_PartySubParty.objects.filter(Party=Party,Route=Route)
                
                if query:
                    PartyID_serializer = PartyWiseSerializer(query,many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyID_serializer})
                    SubPartyListData = list()
                    for a in PartyID_serializer:
                        SubPartyListData.append({
                            "id": a['id'],
                            "SubParty":a['SubParty']['MobileNo']
                    })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyListData})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party Not available', 'Data': []})    
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})    