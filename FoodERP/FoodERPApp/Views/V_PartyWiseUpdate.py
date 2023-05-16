from ..models import MC_PartySubParty
from ..Serializer.S_PartyWiseUpdate import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from django.db.models import Q


class PartyWiseUpdateView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
 
    @transaction.atomic() 
    def post(self, request):
        try:
            with transaction.atomic():
                Party_data = JSONParser().parse(request)
                Party = Party_data['PartyID']
                Route = Party_data['Route']
                FilterPartyID = Party_data['FilterPartyID']
                Type = Party_data['Type']
                
                if not (Route == 0):
                    a = Q(Route=Route)
                else:
                    a = ~Q(Route=Route)
                    
                if not (FilterPartyID == 0):
                    b = Q(SubParty=FilterPartyID)
                else:
                    b = ~Q(SubParty=FilterPartyID)
                    
                # query = MC_PartySubParty.objects.filter(Party=Party).filter(a).filter(b)
                
                q0 = MC_PartySubParty.objects.filter(Party = Party).values("SubParty")
                q1 = M_Parties.objects.filter(id__in = q0,PartyType__IsRetailer=1).select_related("PartyType") 
                query = MC_PartySubParty.objects.filter(SubParty__in=q1).filter(a).filter(b)
                
                
                
                
                if query.exists:
                    PartyID_serializer = PartyWiseSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyID_serializer})
                    SubPartyListData = list()
                    # aa = list()
                    for a in PartyID_serializer:
                        if ( Type == 'PriceList' or Type == 'PartyType' or Type == 'Company'):
                            aa = a['SubParty'][Type]['Name'],
                            ab = a['SubParty'][Type]['id'],
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                Type: aa[0],
                                "TypeID": ab[0]
                            })
                           
                        elif(Type == 'State'):
                            query1 = M_Parties.objects.filter(id=a['SubParty']['id'])
                            State_Serializer = SubPartySerializer(query1,many=True).data

                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                "StateID": State_Serializer[0]['State']['id'],
                                "State": State_Serializer[0]['State']['Name'],
                                "District":  State_Serializer[0]['District']['Name'],
                                "DistrictID": State_Serializer[0]['District']['id'],
                            })
                                                       
                        elif(Type == 'FSSAINo'):
                            query2 = MC_PartyAddress.objects.filter(Party=a['SubParty']['id'])
                            FSSAI_Serializer = FSSAINoSerializer(query2, many=True).data
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
        

class PartyWiseUpdateViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Partydata = JSONParser().parse(request)                
                Type = Partydata['Type']
                UpdatedData = Partydata['UpdateData']

                for a in UpdatedData:
                    if (Type == 'Creditlimit'):     
                        Party = Partydata['PartyID']             
                        query = MC_PartySubParty.objects.filter(Party=Party, SubParty=a['SubPartyID']).update(**{Type: a['Value1']})
                    elif (Type == 'FSSAINo'):
                        query = MC_PartyAddress.objects.filter(Party=a['SubPartyID'], IsDefault=1).update(FSSAINo=a['Value1'], FSSAIExipry=a['Value2'])
                    elif (Type == 'State'):

                        query = M_Parties.objects.filter(id=a['SubPartyID']).update(State=a['Value1'], District=a['Value2'])

                        # print(str(query.query))
                    else:    
                        query = M_Parties.objects.filter(id=a['SubPartyID']).update(**{Type: a['Value1']})
                   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Update Successfully', 'Data': []})
                
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})     

