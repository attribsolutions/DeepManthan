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
                Type = Party_data['Type']
                query = MC_PartySubParty.objects.filter(Party=Party, Route=Route)
                if query.exists:
                    PartyID_serializer = PartyWiseSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyID_serializer})
                    SubPartyListData = list()
                    # aa = list()
                    for a in PartyID_serializer:

                        if (Type == 'District' or Type == 'State' or Type == 'PriceList' or Type == 'PartyType' or Type == 'Company'):
                            aa = a['SubParty'][Type]['Name'],
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                Type: aa[0],
                            })
                            
                        elif (Type == 'FSSAINo'):
                            query1 = MC_PartyAddress.objects.filter(Party=a['SubParty']['id'])
                            FSSAI_Serializer = FSSAINoSerializer(query1, many=True).data
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                "FSSAINo": FSSAI_Serializer[0]['FSSAINo'],
                                "FSSAIExipry":  FSSAI_Serializer[0]['FSSAIExipry']
                                })
                            
                        elif (Type == 'Creditlimit'):
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                Type: a[Type],
                            })
                     
                        else:                           
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                Type: a['SubParty'][Type],
                                })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  PartyID_serializer.error, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

