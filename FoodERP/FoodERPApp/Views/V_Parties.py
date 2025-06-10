import json
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from django.contrib.sessions.backends.db import SessionStore
from ..Serializer.S_Parties import *
from ..Serializer.S_Settings import *
from ..models import *
from ..Serializer.S_Orders import *
import base64
from io import BytesIO
from PIL import Image


class DivisionsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Divisiondata = M_PartyType.objects.filter(IsDivision=id, IsRetailer=0)
                # CustomPrint(Divisiondata.query)
                aa = M_Parties.objects.filter(PartyType__in=Divisiondata)
                if aa.exists():
                    Division_serializer = PartySerializer1(aa, many=True)

                    log_entry = create_transaction_logNew(request, {'DivisonID':id}, 0,'',89,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Division_serializer.data})
                log_entry = create_transaction_logNew(request, {'DivisonID':id}, 0, "Division Not available",89,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Division Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'DivisonDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

# def get_session(request):
#     # Create a new session object using the same session key
#     session = SessionStore(session_key=request.session.session_key)

#     # Get the session variable
#     my_var = session.get('my_var', None)
#     CustomPrint(my_var)
#     return render(request, 'index.html', {'my_var': my_var})


class M_PartiesFilterView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):

        session = SessionStore(session_key=request.session.session_key)
        # CustomPrint('bbbbbbbbbbbbbbbbb', session.get('UserName'))
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Logindata['UserID']
                RoleID = Logindata['RoleID']
                CompanyID = Logindata['CompanyID']
                PartyID = Logindata['PartyID']
                CompanyGroupID = Logindata['CompanyGroup']
                IsSCMCompany = Logindata['IsSCMCompany']
                IsRetailer = Logindata['IsRetailer']

                if (RoleID == 1):  # SuperAdmin
                    
                    q1 = M_PartyType.objects.filter(Company=CompanyID)
                    query = M_Parties.objects.filter(PartyType__in=q1,IsApprovedParty=0)


                elif(IsSCMCompany == 0):  # Admin
                                        
                        if(RoleID == 16 or RoleID == 35 or RoleID == 24):
                            
                            q0 = MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                       
                            q1 = M_Parties.objects.filter(id__in=q0,IsApprovedParty=0)

                            q2 = M_Parties.objects.filter(id=PartyID, IsApprovedParty=0)

                            query = q1.union(q2)
                            
                        else:
                            q1 = M_PartyType.objects.filter(
                            Company=CompanyID, IsRetailer=0)
                    
                            query = M_Parties.objects.filter(
                            Company=CompanyID, PartyType__IsRetailer=0,IsApprovedParty=0).select_related("PartyType")                   
                   

                elif(RoleID == 2 and IsSCMCompany == 1):  # SCM Company Admin
                   
                    q0 = C_Companies.objects.filter(
                        CompanyGroup=CompanyGroupID)
                    
                    q1 = M_PartyType.objects.filter(
                         Company__in=q0, IsRetailer=0, IsSCM=IsSCMCompany)
                    
                    query = M_Parties.objects.filter(PartyType__in=q1,IsApprovedParty=0)
                    

                else:
                   
                    q = M_Roles.objects.filter(id=RoleID).values("isSCMRole")
                    # CustomPrint(q.query)
                    if q[0]['isSCMRole'] == 1:
                        
                        if IsRetailer == 1:
                            q0 = MC_PartySubParty.objects.filter(Party=PartyID).values("SubParty")
                            query = M_Parties.objects.filter(id__in=q0, PartyType__IsRetailer=1,IsApprovedParty=0).select_related("PartyType")
                            
                        else:
                            q0 = MC_PartySubParty.objects.filter(Party=PartyID).values("SubParty")
                            query = M_Parties.objects.filter(id__in=q0, PartyType__IsRetailer=0,IsApprovedParty=0).select_related("PartyType")    
                           
                    else:
                        q0 = MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                       
                        query = M_Parties.objects.filter(id__in=q0,IsApprovedParty=0)
                        
                       
                # if PartyID == 0:

                #     if(RoleID == 1 ):
                #         q1=M_PartyType.objects.filter(Company=CompanyID)
                #         query=M_Parties.objects.filter(PartyType__in = q1)
                #     else:
                #         query=M_Parties.objects.filter(Company=CompanyID)
                # else:
                #     query=MC_PartySubParty.objects.filter(Party=PartyID)

                print((query.query))

                if not query:
                   
                    log_entry = create_transaction_logNew(request, Logindata, PartyID, "List Not available",90,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    
                    M_Parties_serializer = M_PartiesSerializerSecond(
                        query, many=True).data
                    log_entry = create_transaction_logNew(request, Logindata,PartyID ,'Company:'+str(CompanyID),90,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Parties_serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Logindata, 0, 'PartiesFilterList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
class M_PartiesFilterView2(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Logindata['UserID']
                RoleID = Logindata['RoleID']
                CompanyID = Logindata['CompanyID']
                PartyID = Logindata['PartyID']
                CompanyGroupID = Logindata['CompanyGroup']
                IsSCMCompany = Logindata['IsSCMCompany']
                IsRetailer = Logindata['IsRetailer']
                EmployeeID = Logindata['EmployeeID']

                if int(RoleID) == 1:
                     PartyQuery=M_Parties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name,M_PartyType.Name PartyTypeName,M_Parties.Company_id
                                                        FROM M_Parties
                                                        join C_Companies on C_Companies.id=M_Parties.Company_id
                                                        join M_PartyType on M_PartyType.id=M_Parties.PartyType_id
                                                        where M_PartyType.Company_id ={CompanyID}''')
                elif int(RoleID) ==2:
                    if IsSCMCompany == 0:
                            PartyQuery=M_Parties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name,M_PartyType.Name PartyTypeName,M_Parties.Company_id
                                                                FROM M_Parties
                                                                join C_Companies on C_Companies.id=M_Parties.Company_id
                                                                join M_PartyType on M_PartyType.id=M_Parties.PartyType_id
                                                                where M_Parties.Company_id in({CompanyID}) and M_PartyType.IsRetailer = 0 ''')
                    else:
                            PartyQuery=M_Parties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name,M_PartyType.Name PartyTypeName,M_Parties.Company_id
                                                                FROM M_Parties
                                                                join C_Companies on C_Companies.id=M_Parties.Company_id
                                                                join M_PartyType on M_PartyType.id=M_Parties.PartyType_id
                                                                where C_Companies.CompanyGroup_id={CompanyGroupID} and M_PartyType.IsSCM = {IsSCMCompany} and M_PartyType.IsRetailer = 0 ;''')
                else:
                    
                    EmployeeTypecheck = M_Employees.objects.raw(f'''select 1 as id, M_EmployeeTypes.IsSalesTeamMember SalesTeam from M_Employees join M_EmployeeTypes on M_EmployeeTypes.id=M_Employees.EmployeeType_id where M_Employees.id={EmployeeID}''')
                    print(EmployeeTypecheck[0].SalesTeam)
                    
                    if int(EmployeeTypecheck[0].SalesTeam) == 1:
                        
                        party_result = M_Employees.objects.raw(f'''SELECT 1 id ,EmployeeParties({EmployeeID}) Party''')
                        if party_result:
                            party_string = party_result[0].Party  # example: "32584,32585"
                            PartyList = [int(p.strip()) for p in party_string.split(',') if p.strip().isdigit()]
                            Party = ','.join(str(p) for p in PartyList)
                        
                            PartyQuery=M_Parties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name,M_PartyType.Name PartyTypeName,M_Parties.Company_id
                                                        FROM M_Parties
                                                        join C_Companies on C_Companies.id=M_Parties.Company_id
                                                        join M_PartyType on M_PartyType.id=M_Parties.PartyType_id
                                                        where M_Parties.id in( {Party})  ''')
                    else:
                        q = M_Roles.objects.filter(id=RoleID).values("isSCMRole")
                        
                        if q[0]['isSCMRole'] == 1:
                        
                            if IsRetailer == 1:
                                PartyQuery=M_Parties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name,M_PartyType.Name PartyTypeName,M_Parties.Company_id
                                                        FROM M_Parties
                                                        join C_Companies on C_Companies.id=M_Parties.Company_id
                                                        join M_PartyType on M_PartyType.id=M_Parties.PartyType_id 
                                                        join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id
                                                        where MC_PartySubParty.Party_id={PartyID} and M_PartyType.IsRetailer=1 and IsApprovedParty =0   ''')
                            else:
                                PartyQuery=M_Parties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name,M_PartyType.Name PartyTypeName,M_Parties.Company_id
                                                        FROM M_Parties
                                                        join C_Companies on C_Companies.id=M_Parties.Company_id
                                                        join M_PartyType on M_PartyType.id=M_Parties.PartyType_id 
                                                        join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id
                                                        where MC_PartySubParty.Party_id={PartyID} and M_PartyType.IsRetailer=0 and IsApprovedParty =0   ''')

                
                Partys=[]
                # print(PartyQuery)
                for PartyData in PartyQuery:
                    

                    Partys.append({
                        
                        
                        "PartyID": PartyData.id,
                        "PartyName": PartyData.Name,
                        "PartyType": PartyData.PartyTypeName,
                        "Company_id": PartyData.Company_id,
                        
                    })
                
                if not PartyQuery:
                   
                    log_entry = create_transaction_logNew(request, Logindata, PartyID, "List Not available",90,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    
                    
                    log_entry = create_transaction_logNew(request, Logindata,PartyID ,'Company:'+str(CompanyID),90,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Partys})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Logindata, 0, 'PartiesFilterList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        


class M_PartiesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = M_Parties.objects.all()
                if not query:
                    log_entry = create_transaction_logNew(request, 0, 0, "List Not available",91,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(query, many=True).data
                    log_entry = create_transaction_logNew(request,M_Parties_serializer, 0, "All Parties List",91,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Parties_serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'AllPartiesList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        M_Partiesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                M_Parties_Serializer = M_PartiesSerializer(data=M_Partiesdata)
            if M_Parties_Serializer.is_valid():
                Parties = M_Parties_Serializer.save()
                LastInsertID = Parties.id
                log_entry = create_transaction_logNew(request, M_Partiesdata,M_Partiesdata['PartySubParty'][0]['Party'],'',92,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Save Successfully', 'TransactionID':LastInsertID, 'Data': []})
            else:
                log_entry = create_transaction_logNew(request, M_Partiesdata, 0,'PartySave:'+str(M_Parties_Serializer.errors),34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, M_Partiesdata, 0,'PartySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class M_PartiesViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Parties_data = M_Parties.objects.filter(id=id)
                # CustomPrint(str( M_Parties_data.query))
                if not M_Parties_data:
                    log_entry = create_transaction_logNew(request, {'PartyID':id}, 0, "Party Not available",93,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(
                        M_Parties_data, many=True).data
                    query = MC_PartySubParty.objects.filter(SubParty=id)
                    PartySubParty_Serializer = PartySubPartySerializer2(
                        query, many=True).data
                    PartySubPartyList = list()
                    for a in PartySubParty_Serializer:
                        PartySubPartyList.append({
                            "Party": a['Party']['id'],
                            "PartyName": a['Party']['Name'],
                            "Subparty": a['SubParty'],
                            "Creditlimit": a['Creditlimit'],
                            "Route": a['Route']['id'],
                            "RouteName": a['Route']['Name'],
                            "Distance": a['Distance']
                        })
                    list2 = list()
                    list2.append({"Data": M_Parties_serializer[0],
                                  "PartySubParty": PartySubPartyList})
                    # M_Parties_serializer.update({"PartySubParty":list2})
                    # M_Parties_serializer.extend(list2)
                    log_entry = create_transaction_logNew(request,{'PartyID':id},0,'',93,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': list2[0]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'PartyGETMethod:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        M_Partiesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                M_PartiesdataByID = M_Parties.objects.get(id=id)
                M_Parties_Serializer = UpdateM_PartiesSerializer(M_PartiesdataByID, data=M_Partiesdata)
                
                if M_Parties_Serializer.is_valid():
                    UpdatedParty = M_Parties_Serializer.save()
                    LastInsertID = UpdatedParty.id
                    log_entry = create_transaction_logNew(request,M_Partiesdata,id,'',94,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully','TransactionID':LastInsertID, 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,M_Partiesdata, 0, 'PartyEditMethod:'+str(M_Parties_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,M_Partiesdata, 0,'PartyEditMethod:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(id=id)
                M_Partiesdata.delete()
                
                log_entry = create_transaction_logNew(request,{'PartyID':id}, 0, "Party Deleted Successfully",95,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully','TransactionID':id, 'Data': []})
        except M_Parties.DoesNotExist:
            log_entry = create_transaction_logNew(request,{'PartyID':id}, 0, "Party Not available",95,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,{'PartyID':id}, 0, "Party used in another table",8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party used in another table', 'Data': []})


class BulkRetailerDataView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Retailerdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                for aa in Retailerdata['BulkData']:
                    for address in aa.get('PartyAddress', []):
                        if address.get('FSSAIExipry', '') == '':
                            address['FSSAIExipry'] = None 
                            
                    Retailer_serializer = M_PartiesSerializer(data=aa)
                    if Retailer_serializer.is_valid():
                        Retailer = Retailer_serializer.save()
                        LastInsertID = Retailer.id
                    else:
                        log_entry = create_transaction_logNew(request,Retailerdata, 0, 'RetailerBulkDataImportMethod:'+str(Retailer_serializer.errors),34,0)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Retailer_serializer.errors, 'Data': []})
                log_entry = create_transaction_logNew(request,Retailerdata, 0, "Retailer Bulk Data Import Successfully",96,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Bulk Data Import Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Retailerdata, 0,'RetailerBulkDataImportMethod:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


class PartyAddressView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PartiesAddress = MC_PartyAddress.objects.get(id=id)
                PartiesAddress.delete()
                log_entry = create_transaction_logNew(request,{'PartyID':id}, 0,'',97,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Address Deleted Successfully', 'Data': []})
        except MC_PartyAddress.DoesNotExist:
            log_entry = create_transaction_logNew(request,{'PartyID':id}, 0, 'Party Address Not available',97,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Address Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,{'PartyID':id}, 0, 'Party Address used in transaction',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Address used in transaction', 'Data': []})


class PartiesSettingsDetailsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser,MultiPartParser,FormParser]
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, PartyID=0, CompanyID=0):

        try:
            with transaction.atomic():
                query = M_Settings.objects.raw('''SELECT 
    a.Setting id,
    a.SystemSetting,
    a.Description,
	a.IsPartyRelatedSetting,
    a.DefaultValue,
    a.IsActive,
    b.Value CompanyValue,
    c.Value PartyValue,
    (CASE WHEN a.IsPartyRelatedSetting = 1 THEN 
    (CASE WHEN c.Value is Null THEN a.DefaultValue ELSE c.Value END)
	ELSE 
    (CASE WHEN b.Value is Null THEN a.DefaultValue ELSE b.Value END)
	END) Value, 
    c.Image,
    c.ImageID
FROM
    (SELECT 
        M_Settings.id AS Setting,
            M_Settings.SystemSetting AS SystemSetting,
            M_Settings.Description AS Description,
            M_Settings.DefaultValue AS DefaultValue,
            M_Settings.IsPartyRelatedSetting AS IsPartyRelatedSetting,
            M_Settings.IsActive AS IsActive
    FROM
        M_Settings
    WHERE
        M_Settings.IsActive = 1) a
      
      LEFT  JOIN 
      (SELECT SettingID_id SettingID,MC_SettingsDetails.Value FROM MC_SettingsDetails WHERE MC_SettingsDetails.Company_id=%s and IsDeleted=0)b
      ON a.Setting = b.SettingID
            
      LEFT JOIN
    (SELECT Setting_id SettingID, M_PartySettingsDetails.Value,M_PartySettingsDetails.Image,M_PartySettingsDetails.id AS ImageID FROM M_PartySettingsDetails WHERE
        M_PartySettingsDetails.Party_id =%s) c ON a.Setting = c.SettingID ''', ([CompanyID], [PartyID]))
      
                a = PartiesSettingsDetailsListSerializer(query, many=True,context= {'request': request}).data
                log_entry = create_transaction_logNew(request,a, PartyID,'',98,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': a})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'PartiesSettingsDetailsList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def post(self, request,format=None):
        try:
            with transaction.atomic():
                
                Retailerdata = request.POST.get('BulkData')
                Retailerdatareferences = json.loads(Retailerdata) if Retailerdata else []
                Party= Retailerdatareferences[0]['Party']
                query = M_PartySettingsDetails.objects.filter(Party=Party).all()
                query.delete()
                for aa in Retailerdatareferences:
                    '''Image Upload Code End''' 
                    keyname='uploaded_images_'+str(aa['Setting'])
                    avatar = request.FILES.getlist(keyname)
                    for file in avatar:
                        aa['Image']=file
                    '''Image Upload Code End'''
                    Partysettings_serializer = PartiesSettingSerializer(
                        data=aa)
                    if Partysettings_serializer.is_valid():
                        PartySettings = Partysettings_serializer.save()
                        LastInsertID = PartySettings.id
                    else:
                        log_entry = create_transaction_logNew(request,Retailerdata, 0,'PartySettingsDataSave:'+str(Partysettings_serializer.errors),34,0)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Partysettings_serializer.errors, 'Data': []})
                log_entry = create_transaction_logNew(request,Retailerdata, Party,'',99,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Party Settings data Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'PartySettingsDataSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
        
        
        
class PartiesListForApprovalView(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Retailerdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyID = Retailerdata['PartyID']
                q0 = MC_PartySubParty.objects.filter(Party=PartyID).values('SubParty')
                query = M_Parties.objects.filter(id__in=q0,IsApprovedParty=1)
                if not query:
                    log_entry = create_transaction_logNew(request,Retailerdata, PartyID,'PartyList Not available',198,0)                   
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    M_Parties_serializer = PartiesSerializer(query, many=True).data
                    log_entry = create_transaction_logNew(request,Retailerdata, PartyID,'',198,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Parties_serializer})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Retailerdata, 0,'PartyListForApproval:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
           
        
