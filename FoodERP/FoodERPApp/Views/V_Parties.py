from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from django.contrib.sessions.backends.db import SessionStore


from ..Serializer.S_Parties import *

from ..models import *


class DivisionsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Divisiondata =  M_PartyType.objects.filter(IsDivision=id)
                aa=M_Parties.objects.filter(PartyType__in=Divisiondata)
                
                if aa.exists():
                    Division_serializer = DivisionsSerializer(aa, many=True)
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Division_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Division Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 

# def get_session(request):
#     # Create a new session object using the same session key
#     session = SessionStore(session_key=request.session.session_key)
    
#     # Get the session variable
#     my_var = session.get('my_var', None)
#     print(my_var)
#     return render(request, 'index.html', {'my_var': my_var})  

class M_PartiesFilterView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def post(self, request):
        
        session = SessionStore(session_key=request.session.session_key)
        print('bbbbbbbbbbbbbbbbb',session.get('UserName'))
        try:
            with transaction.atomic():
                
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 
                # IsSCMCompany = Logindata['IsSCMCompany']
                CompanyGroupID =Logindata['CompanyGroup'] 
                IsSCMCompany = Logindata['IsSCMCompany'] 
               
                if (RoleID == 1): # SuperAdmin
                   
                    q1=M_PartyType.objects.filter(Company=CompanyID)
                    query=M_Parties.objects.filter(PartyType__in = q1)

                elif(RoleID == 2 and IsSCMCompany == 0): # Admin
                  
                    q1=M_PartyType.objects.filter(Company=CompanyID,IsRetailer = 0)
                    query=M_Parties.objects.filter(Company=CompanyID,PartyType__IsRetailer=0).select_related("PartyType")

                elif(RoleID == 2 and IsSCMCompany == 1): # SCM Company Admin
                    
                    q0=C_Companies.objects.filter(CompanyGroup = CompanyGroupID)
                    
                    q1=M_PartyType.objects.filter(Company__in=q0,IsRetailer = 0,IsSCM = 1)
                    query=M_Parties.objects.filter(PartyType__in = q1)
                    

                else:
                   
                    
                    q=M_Roles.objects.filter(id=RoleID).values("isSCMRole")
                   
                    if q[0]['isSCMRole'] == 1:
                        
                      
                        q0 = MC_PartySubParty.objects.filter(Party = PartyID).values("SubParty")
                       
                        query = M_Parties.objects.filter(id__in = q0,PartyType__IsRetailer=1).select_related("PartyType")  
                       
                    else:
                        q0 = MC_PartySubParty.objects.filter(Party = PartyID)
                        query = M_Parties.objects.filter(id__in = q0)
                # if PartyID == 0:

                #     if(RoleID == 1 ):
                #         q1=M_PartyType.objects.filter(Company=CompanyID)
                #         query=M_Parties.objects.filter(PartyType__in = q1)
                #     else:
                #         query=M_Parties.objects.filter(Company=CompanyID)
                # else:
                #     query=MC_PartySubParty.objects.filter(Party=PartyID)
                
                # print((query.query))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:

                    M_Parties_serializer = M_PartiesSerializerSecond(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Data':M_Parties_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_PartiesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query=M_Parties.objects.all() 
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Data':M_Parties_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 
                M_Partiesdata = JSONParser().parse(request)
                M_Parties_Serializer = M_PartiesSerializer(data=M_Partiesdata)
            if M_Parties_Serializer.is_valid():
                M_Parties_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class M_PartiesViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Parties_data=M_Parties.objects.filter(id=id)
                # print(str( M_Parties_data.query))
                if not M_Parties_data:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(M_Parties_data, many=True).data
                    query = MC_PartySubParty.objects.filter(SubParty=id)
                    PartySubParty_Serializer= PartySubPartySerializer2(query,many=True).data
                    PartySubPartyList = list()
                    for a in PartySubParty_Serializer:
                        PartySubPartyList.append({
                            "Party":a['Party']['id'],
                            "PartyName":a['Party']['Name']
                        })
                    list2 = list()
                    list2.append({"Data":M_Parties_serializer[0],
                                  "PartySubParty":PartySubPartyList})    
                    # # M_Parties_serializer.update({"PartySubParty":list2})
                    # M_Parties_serializer.extend(list2)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data':list2[0]})
                    
                    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_PartiesdataByID = M_Parties.objects.get(id=id)
                M_Parties_Serializer = M_PartiesSerializer(
                    M_PartiesdataByID, data=M_Partiesdata)
                if M_Parties_Serializer.is_valid():
                    M_Parties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' : []})
        except Exception as e :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e),'Data' : []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(id=id)
                M_Partiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully', 'Data':[]})
        except M_Parties.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party used in another table', 'Data': []})


                