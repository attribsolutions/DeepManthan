from django.db.models import Q
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Parties import DivisionsSerializer
from ..Serializer.S_PartySubParty import *
from ..Serializer.S_CompanyGroup import *
from ..models import *

class PartySubPartyListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.raw('''SELECT MC_PartySubParty.id,MC_PartySubParty.Party_id,M_Parties.Name PartyName,count(MC_PartySubParty.SubParty_id)Subparty FROM MC_PartySubParty join M_Parties ON M_Parties.id=MC_PartySubParty.Party_id group by Party_id''')
                if not query:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = PartySubPartySerializerGETList(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
class PartySubPartyView(CreateAPIView):     # PartySubParty Save
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartySubpartiesdata = JSONParser().parse(request)
         
                PartySubparties_Serializer = PartySubPartySerializer(data=PartySubpartiesdata, many=True)
               
                if PartySubparties_Serializer.is_valid():
                    PartySubpartiesdata1 = MC_PartySubParty.objects.filter(Party=PartySubpartiesdata[0]['PartyID'])
                 
                    PartySubpartiesdata1.delete()
                    PartySubpartiesdata2 = MC_PartySubParty.objects.filter(SubParty=PartySubpartiesdata[0]['PartyID'],Party__PartyType=3).select_related('Party')
                  
                    PartySubpartiesdata2.delete()
                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'Data':str(PartySubpartiesdata.query)})
                   
                    PartySubparties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartySubparties_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class PartySubPartyViewSecond(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
       
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query= MC_PartySubParty.objects.filter(Party=id)
                
                SubPartySerializer = PartySubpartySerializerSecond(query, many=True).data

                query1= MC_PartySubParty.objects.filter(SubParty=id)
               
                PartySerializer = PartySubpartySerializerSecond(query1, many=True).data
                SubPartyList = list()
                for a in PartySerializer:
                    SubPartyList.append({
                        "Party": a['SubParty']['id'],
                        "PartyName": a['SubParty']['Name'],
                        "SubParty": a['Party']['id'],
                        "SubPartyName": a['Party']['Name'],
                        "PartyType": a['Party']['PartyType'],
                        "Route": a['Route']['id'],
                        "Creditlimit": a['Creditlimit']
                    }) 
                for a in SubPartySerializer:
                    SubPartyList.append({
                        "Party": a['Party']['id'],
                        "PartyName": a['Party']['Name'],
                        "SubParty": a['SubParty']['id'],
                        "SubPartyName": a['SubParty']['Name'],
                        "PartyType": a['SubParty']['PartyType'],
                        "Route": a['Route']['id'],
                        "Creditlimit": a['Creditlimit']
                    })
                   
                
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyList})
                
        except  MC_PartySubParty.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party SubParty Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class GetVendorSupplierCustomerListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication 
            
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Partydata = JSONParser().parse(request)
                Type=Partydata['Type']
                id=Partydata['PartyID']
                Company=Partydata['Company']
                
                if(Type==1): #Vendor
                    q0=M_PartyType.objects.filter(Company=Company,IsVendor=1)
                    Query = MC_PartySubParty.objects.filter(SubParty=id,Party__PartyType__in=q0).select_related('Party')
                    
                elif(Type==2): #Supplier
                    q=C_Companies.objects.filter(id=Company).values("CompanyGroup")
                    q00=C_Companies.objects.filter(CompanyGroup=q[0]["CompanyGroup"])
                    q0=M_PartyType.objects.filter(Company__in=q00,IsVendor=0)
                    Query = MC_PartySubParty.objects.filter(SubParty=id,Party__PartyType__in=q0).select_related('Party')
                    
                elif(Type==3):  #Customer
                    q0=M_PartyType.objects.filter(Company=Company,IsVendor=0)
                    Query = MC_PartySubParty.objects.filter(Party=id,SubParty__PartyType__in=q0).select_related('Party')
                
                elif (Type==4):
                    Query = M_Parties.objects.filter(Company=Company,IsDivision=1).filter(~Q(id=id))
                
                if Query:
                    
                    if(Type==4):
                        Supplier_serializer = DivisionsSerializer(Query, many=True).data
                    else:    
                        Supplier_serializer = PartySubpartySerializerSecond(Query, many=True).data
                    
                    ListData = list()
                    for a in Supplier_serializer: 
                        if(Type==1): #Vendor
                            ListData.append({
                            "id": a['Party']['id'],
                            "Name": a['Party']['Name']
                            })   
                        elif(Type==2): #Supplier
                            ListData.append({
                            "id": a['Party']['id'],
                            "Name": a['Party']['Name']
                            }) 
                        elif(Type==3):  #Customer
                            ListData.append({
                            "id": a['SubParty']['id'],
                            "Name": a['SubParty']['Name']
                            })
                        else:
                            ListData.append({
                            "id": a['id'],
                            "Name": a['Name']
                            })

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': ListData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                
        
class RetailerandSSDDView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication 
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                PartySubPartydata = JSONParser().parse(request)
                CompanyID=PartySubPartydata['CompanyID']
                PartyID=PartySubPartydata['PartyID']
                Type=PartySubPartydata['Type']   
                
                if Type==1: ##All Retailer under given Party and Company
                    q0=M_PartyType.objects.filter(Company=CompanyID,IsRetailer=1,IsSCM=1)
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(PartyType__in=q0,id__in=q1)
                  
                elif Type==2:  ##All SS/DD under given Party and Company
                    
                    q0=M_PartyType.objects.filter(Company=CompanyID,IsRetailer=0,IsSCM=1)
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(PartyType__in=q0,id__in=q1)
                
                elif Type==3:  #All SS/DD under given Company
                   
                    q=C_Companies.objects.filter(id=CompanyID).values('IsSCM')
                 
                    if q[0]['IsSCM'] == 0:
                       
                        
                        q2=M_Parties.objects.filter(Company=CompanyID )
                        
                    else:
                        a=C_Companies.objects.filter(id=CompanyID).values('CompanyGroup')
                     
                        a1=C_Companies.objects.filter(CompanyGroup=a[0]['CompanyGroup'],IsSCM=0)
                       
                        q0=M_PartyType.objects.filter(Company__in=a1,IsRetailer=0,IsSCM=1)
                       
                        q2=M_Parties.objects.filter(PartyType__in=q0)
                       
                
                elif Type==4:  #All Subparties under given Party and Company
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(id__in=q1)    
                
                PartySerializer_data=PartySerializer(q2,many=True).data

            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartySerializer_data})  
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})        
        