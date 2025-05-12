from django.db.models import Q, F
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
from .V_CommFunction import *

class PartySubPartyListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.raw('''SELECT MC_PartySubParty.id,MC_PartySubParty.Party_id,M_Parties.Name PartyName,count(MC_PartySubParty.SubParty_id)Subparty FROM MC_PartySubParty join M_Parties ON M_Parties.id=MC_PartySubParty.Party_id group by Party_id''')
                if not query:
                    log_entry = create_transaction_logNew(request, 0,0,'Party SubParty List Not Found',175,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = PartySubPartySerializerGETList(query, many=True).data
                    log_entry = create_transaction_logNew(request, M_Items_Serializer,0,'',175,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'PartySubPartyList:'+str(Exception(e)),33,0)
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
                    PartySubpartiesdata2 = MC_PartySubParty.objects.filter(SubParty=PartySubpartiesdata[0]['PartyID'],Party__PartyType__IsVendor=1).select_related('Party')
                  
                    PartySubpartiesdata2.delete()
                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'Data':str(PartySubpartiesdata.query)})
                   
                    SubParty = PartySubparties_Serializer.save()
                    LastInsertID = SubParty[0].id
                    log_entry = create_transaction_logNew(request, PartySubpartiesdata,PartySubpartiesdata[0]['Party'],'TransactionID:'+str(LastInsertID),176,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party SubParty Save Successfully', 'TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, PartySubpartiesdata,0,'PartySubPartySave:'+str(PartySubparties_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartySubparties_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'PartySubPartySave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class PartySubPartyViewSecond(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
       
    @transaction.atomic()         
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query= MC_PartySubParty.objects.filter(Party=id)
                # CustomPrint(query.query)
                SubPartySerializer = PartySubpartySerializerSecond(query, many=True).data
                # CustomPrint(SubPartySerializer)
                query1= MC_PartySubParty.objects.filter(SubParty=id).values('Party_id')
                # CustomPrint(query1.query)
                query2 = M_Parties.objects.filter(id__in=query1,PartyType__IsVendor=1).select_related('PartyType')
                # CustomPrint(query2.query)
                query3 =  MC_PartySubParty.objects.filter(Party__in=query2,SubParty=id)
                # CustomPrint(query3.query)
                PartySerializer = PartySubpartySerializerSecond(query3, many=True).data
                # CustomPrint(PartySerializer)
                
                SubPartyList = list()
                for a in PartySerializer:
                    SubPartyList.append({
                        "Party": a['SubParty']['id'],
                        "PartyName": a['SubParty']['Name'],
                        "SubParty": a['Party']['id'],
                        "SubPartyName": a['Party']['Name'],
                        "PartyType": a['Party']['PartyType']['id'],
                        "IsVendor": a['Party']['PartyType']['IsVendor'],
                        "Route": a['Route']['id'],
                        "Creditlimit": a['Creditlimit'],
                        "PartyTypeName" : a['Party']['PartyType']['Name']
                    }) 

                for a in SubPartySerializer:
                    SubPartyList.append({
                        "Party": a['Party']['id'],
                        "PartyName": a['Party']['Name'],
                        "SubParty": a['SubParty']['id'],
                        "SubPartyName": a['SubParty']['Name'],
                        "PartyType": a['SubParty']['PartyType']['id'],
                        "IsVendor": a['SubParty']['PartyType']['IsVendor'],
                        "Route": a['Route']['id'],
                        "Creditlimit": a['Creditlimit'],
                        "PartyTypeName" : a['Party']['PartyType']['Name']                        
                    })
                
                log_entry = create_transaction_logNew(request, PartySerializer,0,'',175,0)               
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SubPartyList})
        except  MC_PartySubParty.DoesNotExist:
            log_entry = create_transaction_logNew(request, PartySerializer,0,'PartySubPartyList Not Available',175,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Party SubParty Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'PartySubPartyList:'+str(Exception(e)),33,0)
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
                Route = Partydata['Route']
                
                if(Type==1): #Vendor
                    
                    Query = MC_PartySubParty.objects.filter(
                                    SubParty=id,
                                    Party__PartyType__IsVendor=1,
                                    Party__PartyAddress__IsDefault=1
                                    ).select_related('Party', 'Party__PartyType','Party__PartyAddress').annotate(
                                    PartyId=F('Party__id'),
                                    PartyName=F('Party__Name'),
                                    GSTIN = F('Party__GSTIN'),
                                    PAN= F('Party__PAN'),
                                    PartyTypeID=F('Party__PartyType'),
                                    SkyggeID=F('Party__SkyggeID'),
                                    FSSAINo=F('Party__PartyAddress__FSSAINo'),
                                    FSSAIExipry=F('Party__PartyAddress__FSSAIExipry'),
                                ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')
                    CustomPrint(Query.query)
                elif(Type==2): #Supplier
                    Query = MC_PartySubParty.objects.filter(
                                    SubParty=id,
                                    
                                    Party__PartyAddress__IsDefault=1
                                    ).select_related('Party', 'Party__PartyType','Party__PartyAddress').annotate(
        PartyId=F('Party__id'),
        PartyName=F('Party__Name'),
        GSTIN = F('Party__GSTIN'),
        PAN= F('Party__PAN'),
        PartyTypeID=F('SubParty__PartyType'),
        SkyggeID=F('Party__SkyggeID'),
        FSSAINo=F('Party__PartyAddress__FSSAINo'),
        FSSAIExipry=F('Party__PartyAddress__FSSAIExipry'),
    ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')
                    
                elif(Type==3):  #Customer
                    
                    if (Route==""):
                        D = Q()
                    else:
                        D = Q(Route=Route)
                    Query = MC_PartySubParty.objects.filter(D).filter(
                                    Party=id,SubParty__PartyAddress__IsDefault=1,SubParty__PartyType__IsDivision=0).select_related('SubParty', 'SubParty__PartyType','SubParty__PartyAddress').annotate(
        PartyId=F('SubParty__id'),
        PartyName=F('SubParty__Name'),
        GSTIN = F('SubParty__GSTIN'),
        PAN= F('SubParty__PAN'),
        PartyTypeID=F('SubParty__PartyType'),
        SkyggeID=F('SubParty__SkyggeID'),
        FSSAINo=F('SubParty__PartyAddress__FSSAINo'),
        FSSAIExipry=F('SubParty__PartyAddress__FSSAIExipry'),
    ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')
                    
                elif (Type==4):
                    Query = MC_PartySubParty.objects.filter(~Q(id=id)).filter(
                                    Party=id,SubParty__PartyType__IsDivision=1,
                                    SubParty__PartyAddress__IsDefault=1).select_related('SubParty', 'SubParty__PartyType','SubParty__PartyAddress').annotate(
        PartyId=F('SubParty__id'),
        PartyName=F('SubParty__Name'),
        GSTIN = F('SubParty__GSTIN'),
        PAN= F('SubParty__PAN'),
        PartyTypeID=F('SubParty__PartyType'),
        SkyggeID=F('SubParty__SkyggeID'),
        FSSAINo=F('SubParty__PartyAddress__FSSAINo'),
        FSSAIExipry=F('SubParty__PartyAddress__FSSAIExipry'),
    ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')
                        
                elif(Type==5):  #Customer without retailer
                    if (Route==""):
                        D = Q()
                    else:
                        D = Q(Route=Route)
                    Query = MC_PartySubParty.objects.filter(D).filter(
                                    Party=id,SubParty__PartyType__IsRetailer=0,
                                    SubParty__PartyAddress__IsDefault=1).select_related('SubParty', 'SubParty__PartyType','SubParty__PartyAddress').annotate(
        PartyId=F('SubParty__id'),
        PartyName=F('SubParty__Name'),
        GSTIN = F('SubParty__GSTIN'),
        PAN= F('SubParty__PAN'),
        PartyTypeID=F('SubParty__PartyType'),
        SkyggeID=F('SubParty__SkyggeID'),
        FSSAINo=F('SubParty__PartyAddress__FSSAINo'),
        FSSAIExipry=F('SubParty__PartyAddress__FSSAIExipry'),
    ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')
                elif(Type==6): #Vendor & Division
                    
                    Query1 = MC_PartySubParty.objects.filter(
                                    SubParty=id,
                                    Party__PartyType__IsVendor=1,                                    
                                    Party__PartyAddress__IsDefault=1                                   
                                    ).select_related('Party', 'Party__PartyType','Party__PartyAddress').annotate(
                                    PartyId=F('Party__id'),
                                    PartyName=F('Party__Name'),
                                    GSTIN = F('Party__GSTIN'),
                                    PAN= F('Party__PAN'),
                                    PartyTypeID=F('Party__PartyType'),
                                    SkyggeID=F('Party__SkyggeID'),
                                    FSSAINo=F('Party__PartyAddress__FSSAINo'),
                                    FSSAIExipry=F('Party__PartyAddress__FSSAIExipry'),
                                ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')    
                    Query2 = MC_PartySubParty.objects.filter(
                                    Party=id,
                                    SubParty__PartyType__IsDivision=1,                                    
                                    SubParty__PartyAddress__IsDefault=1                                   
                                    ).select_related('SubParty', 'SubParty__PartyType','SubParty__PartyAddress').annotate(
                                    PartyId=F('SubParty__id'),
                                    PartyName=F('SubParty__Name'),
                                    GSTIN = F('SubParty__GSTIN'),
                                    PAN= F('SubParty__PAN'),
                                    PartyTypeID=F('SubParty__PartyType'),
                                    SkyggeID=F('SubParty__SkyggeID'),
                                    FSSAINo=F('SubParty__PartyAddress__FSSAINo'),
                                    FSSAIExipry=F('SubParty__PartyAddress__FSSAIExipry'),
                                ).values('PartyId','PartyName','GSTIN','PAN','PartyTypeID','IsTCSParty','SkyggeID','FSSAINo','FSSAIExipry')
                    Query=Query1.union(Query2)
                   
                
                if Query:
                    ListData = list()
                    for a in Query: 
                        # CustomPrint(a)
                        ListData.append({
                            "id": a['PartyId'],
                            "Name": a['PartyName'],
                            "GSTIN": a['GSTIN'],
                            "PAN":a['PAN'],
                            "FSSAINo" : a['FSSAINo'],
                            "FSSAIExipry" : a['FSSAIExipry'],
                            "IsTCSParty":a['IsTCSParty'],
                            "SkyggeID": a['SkyggeID']
                            })
                        
                        
                    log_entry = create_transaction_logNew(request, Partydata,id,'',177,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': ListData})
                log_entry = create_transaction_logNew(request, Partydata,id,'GetVendorSupplierCustomer Not Available',177,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request, 0,0,'GetVendorSupplierCustomer:'+str(Exception(e)),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
                
        
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
                
                q2 = []
                
                if Type == 1: ##All Retailer under given Party and Company
                    if CompanyID == 4: ##ForCSS show all Customers under given Party
                        setting = M_Settings.objects.filter(id=68, IsActive=True, DefaultValue__isnull=False).values("DefaultValue").first()
                        if setting:
                            PartytypeID = int(setting['DefaultValue'])  
                            q1 = MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                            q2 = M_Parties.objects.filter(PartyType=PartytypeID, id__in=q1)
                    else:
                        q0 = M_PartyType.objects.filter(Company=CompanyID, IsRetailer=1, IsSCM=1)
                        q1 = MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                        q2 = M_Parties.objects.filter(PartyType__in=q0, id__in=q1)

                  
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
                     
                        a1=C_Companies.objects.filter(CompanyGroup=a[0]['CompanyGroup'])
                       
                        q0=M_PartyType.objects.filter(Company__in=a1,IsRetailer=0,IsSCM=1,IsDivision=0)
                       
                        q2=M_Parties.objects.filter(PartyType__in=q0)
                       
                
                elif Type==4:  #All Subparties under given Party and Company
                    q1=MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                    q2=M_Parties.objects.filter(id__in=q1)    
                
                PartySerializer_data=PartySerializer(q2,many=True).data
            log_entry = create_transaction_logNew(request, PartySubPartydata,PartyID,'',178,0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartySerializer_data})  
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'RetailerandSSDD:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})        


class CxDDDiffPartiesView(CreateAPIView):        

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():
                query = M_Parties.objects.raw('''SELECT  MC_PartySubParty.id, B.id SupplierID, B.NAME AS SupplierName
                                    FROM MC_PartySubParty 
                                    JOIN M_Parties A ON A.id = MC_PartySubParty.SubParty_id
                                    JOIN M_Parties B ON B.id = MC_PartySubParty.Party_id
                                    JOIN M_PartyType ON M_PartyType.id = A.PartyType_id
                                    WHERE M_PartyType.id = 15 GROUP BY SupplierID''')
                if query:
                    CxDDDiffParties_Serializer = CxDDDiffPartiesSerializer(query, many=True).data
                    CxDDDiffPartiesList=list()
                    for a in CxDDDiffParties_Serializer:
                        CxDDDiffPartiesList.append({
                            "SupplierID":a['SupplierID'],
                            "SupplierName":a['SupplierName']
                        })
                    log_entry = create_transaction_logNew(request, CxDDDiffParties_Serializer,0,'',273,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :CxDDDiffPartiesList})
                log_entry = create_transaction_logNew(request, CxDDDiffParties_Serializer,0,'CxParty not available',273,0)                    
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'CxParty not available', 'Data' : []})
        except Exception as e:
                log_entry = create_transaction_logNew(request, 0,0,'GETCxParty:'+str(Exception(e)),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})