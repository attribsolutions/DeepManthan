from ..models import MC_PartySubParty
from ..Serializer.S_PartyWiseUpdate import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from django.db.models import Q
from ..Serializer.S_Orders import *
import datetime

class PartyWiseUpdateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
 
    @transaction.atomic() 
    def post(self, request):
        Party_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                Party = Party_data['PartyID']
                Route = Party_data['Route']
                FilterPartyID = Party_data['FilterPartyID']
                Type = Party_data['Type']               
                
                if not (Route == 0):
                    a = Q(Route=Route)
                else:
                    a = Q()
                    
                if not (FilterPartyID == 0):
                    b = Q(SubParty=FilterPartyID)
                else:
                    b = Q()
                    
                
                
                # q0 = MC_PartySubParty.objects.filter(Party = Party).values("SubParty")
                
                # q1 = M_Parties.objects.filter(id__in = q0).select_related("PartyType")

                query = MC_PartySubParty.objects.filter(Party = Party).filter(a).filter(b)
                # CustomPrint(query.query)
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
                            
                        elif (Type == 'Creditlimit' or Type == 'IsTCSParty' ):
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                Type: a[Type],
                            })
                        
                        elif (Type == 'OpeningBalance'):
                            query = MC_PartySubPartyOpeningBalance.objects.filter(Party_id=a['Party']['id'],SubParty_id=a['SubParty']['id']).values('OpeningBalanceAmount','Date')
                           
                            if not query:
                                OpeningBalance = 0.00                              
                                OpeningBalanceDate= ""
                            else:
                                OpeningBalance = query[0]['OpeningBalanceAmount']
                                OpeningBalanceDate=query[0]["Date"]
                                                             
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                "Date":OpeningBalanceDate,
                                Type: OpeningBalance,
                                    
                                })
                            
                            
                        else:                           
                            SubPartyListData.append({
                                "id": a['id'],
                                "PartyID":a['Party']['id'],
                                "SubPartyID":a['SubParty']['id'],
                                "PartyName": a['SubParty']['Name'],
                                Type: a['SubParty'][Type],
                                })
                    log_entry = create_transaction_logNew(request, Party_data, Party, "PartyWise SubParty List",112,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyListData})
                log_entry = create_transaction_logNew(request, Party_data, 0,'PartyWiseUpdate:'+str(PartyID_serializer.error),34,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  PartyID_serializer.error, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Party_data, 0,'PartyWiseUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        

class PartyWiseUpdateViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Partydata = JSONParser().parse(request) 
        try:
            with transaction.atomic():               
                Type = Partydata['Type']
                UpdatedData = Partydata['UpdateData']

                for a in UpdatedData:
                    if (Type == 'Creditlimit' or Type == 'IsTCSParty' ):     
                        Party = Partydata['PartyID']             
                        query = MC_PartySubParty.objects.filter(Party=Party, SubParty=a['SubPartyID']).update(**{Type: a['Value1']})
                    elif (Type == 'FSSAINo'):
                        query = MC_PartyAddress.objects.filter(Party=a['SubPartyID'], IsDefault=1).update(FSSAINo=a['Value1'], FSSAIExipry=a['Value2'])
                    elif (Type == 'State'):
                        query = M_Parties.objects.filter(id=a['SubPartyID']).update(State=a['Value1'], District=a['Value2'])
                    elif (Type == 'OpeningBalance'):
                        
                        Party = Partydata['PartyID']
                        party_instance = M_Parties.objects.get(id=int(Party)) 
                        subparty_instance = M_Parties.objects.get(id=int(a['SubPartyID']))   
                        query = MC_PartySubPartyOpeningBalance.objects.filter(Party=Party,SubParty=a['SubPartyID'])
                        num_updated = query.update(OpeningBalanceAmount=a['Value1'],Date=a['Date'])                        
                        if num_updated == 0:
                            # If no records were updated, insert a new record
                            new_record = MC_PartySubPartyOpeningBalance(
                                Party=party_instance,
                                SubParty=subparty_instance,
                                OpeningBalanceAmount=a['Value1'],
                                Year='2324',
                                CreatedBy =Partydata['CreatedBy'],
                                UpdatedBy =Partydata['UpdatedBy'], 
                                Date=a['Date'] ,
                            )
                            new_record.save()
                            
                    else:    
                        query = M_Parties.objects.filter(id=a['SubPartyID']).update(**{Type: a['Value1']})  
                log_entry = create_transaction_logNew(request, Partydata,Partydata['PartyID'], "PartyWise Update Successfully",113,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Update Successfully','PartyID':Partydata['PartyID'], 'Data': []})  
        except Exception as e:
            log_entry = create_transaction_logNew(request, Partydata, 0,'PartyWiseSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})     

