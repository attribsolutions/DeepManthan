import json
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from django.contrib.sessions.backends.db import SessionStore
from ..Serializer.S_Parties import *
from ..Serializer.S_Settings import *
from ..models import *
from ..Serializer.S_Orders import *

class DivisionsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Divisiondata = M_PartyType.objects.filter(IsDivision=id)
                aa = M_Parties.objects.filter(PartyType__in=Divisiondata)
                if aa.exists():
                    Division_serializer = DivisionsSerializer(aa, many=True)

                    log_entry = create_transaction_log(request, {'DivisonID':id}, 0, 0, "Divisons",89,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Division_serializer.data})
                log_entry = create_transaction_log(request, {'DivisonID':id}, 0, 0, "Data Not available",7,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Division Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request, {'DivisonID':id}, 0, 0, Exception(e),33,0)
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
        print('bbbbbbbbbbbbbbbbb', session.get('UserName'))
        try:
            with transaction.atomic():

                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']
                RoleID = Logindata['RoleID']
                CompanyID = Logindata['CompanyID']
                PartyID = Logindata['PartyID']
                # IsSCMCompany = Logindata['IsSCMCompany']
                CompanyGroupID = Logindata['CompanyGroup']
                IsSCMCompany = Logindata['IsSCMCompany']
                IsRetailer = Logindata['IsRetailer']

                if (RoleID == 1):  # SuperAdmin

                    q1 = M_PartyType.objects.filter(Company=CompanyID)
                    query = M_Parties.objects.filter(PartyType__in=q1)

                elif(IsSCMCompany == 0):  # Admin

                    q1 = M_PartyType.objects.filter(
                        Company=CompanyID, IsRetailer=0)
                    query = M_Parties.objects.filter(
                        Company=CompanyID, PartyType__IsRetailer=0).select_related("PartyType")

                elif(RoleID == 2 and IsSCMCompany == 1):  # SCM Company Admin

                    q0 = C_Companies.objects.filter(
                        CompanyGroup=CompanyGroupID)

                    q1 = M_PartyType.objects.filter(
                        Company__in=q0, IsRetailer=0, IsSCM=1)
                    query = M_Parties.objects.filter(PartyType__in=q1)

                else:

                    q = M_Roles.objects.filter(id=RoleID).values("isSCMRole")

                    if q[0]['isSCMRole'] == 1:
                        
                        if IsRetailer == 1:
                            q0 = MC_PartySubParty.objects.filter(Party=PartyID).values("SubParty")
                            query = M_Parties.objects.filter(id__in=q0, PartyType__IsRetailer=1).select_related("PartyType")
                        else:
                            q0 = MC_PartySubParty.objects.filter(Party=PartyID).values("SubParty")
                            query = M_Parties.objects.filter(id__in=q0, PartyType__IsRetailer=0).select_related("PartyType")    

                    else:
                        q0 = MC_PartySubParty.objects.filter(Party=PartyID)
                        query = M_Parties.objects.filter(id__in=q0)
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
                    log_entry = create_transaction_log(request, Logindata, 0, PartyID, "Data Not available",7,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:

                    M_Parties_serializer = M_PartiesSerializerSecond(
                        query, many=True).data
                    log_entry = create_transaction_log(request, Logindata, 0, PartyID, "Parties Filter List",90,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Parties_serializer})
        except Exception as e:
            log_entry = create_transaction_log(request, Logindata, 0, PartyID, Exception(e),33,0)
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
                    log_entry = create_transaction_log(request, 0, 0, 0, "Data Not available",33,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(
                        query, many=True).data
                    log_entry = create_transaction_log(request, {'PartyDetails':M_Parties_serializer}, 0, 0, "All Parties List",91,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Parties_serializer})
        except Exception as e:
            log_entry = create_transaction_log(request, {'PartyDetails':M_Parties_serializer}, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_Parties_Serializer = M_PartiesSerializer(data=M_Partiesdata)
            if M_Parties_Serializer.is_valid():
                Parties = M_Parties_Serializer.save()
                LastInsertID = Parties.id
                log_entry = create_transaction_log(request, M_Partiesdata, 0, 0, "Party Save Successfully",92,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Save Successfully', 'Data': []})
            else:
                log_entry = create_transaction_log(request, M_Partiesdata, 0, 0, M_Parties_Serializer.errors,34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request, M_Partiesdata, 0, 0, Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_PartiesViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Parties_data = M_Parties.objects.filter(id=id)
                # print(str( M_Parties_data.query))
                if not M_Parties_data:
                    log_entry = create_transaction_log(request, {'PartyID':id}, 0, 0, "Data Not available",7,0)
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
                    # # M_Parties_serializer.update({"PartySubParty":list2})
                    # M_Parties_serializer.extend(list2)
                    log_entry = create_transaction_log(request,{'PartyID':id}, 0, a['Party']['id'], "Party",93,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': list2[0]})
        except Exception as e:
            log_entry = create_transaction_log(request, {'PartyID':id}, 0, a['Party']['id'], Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_PartiesdataByID = M_Parties.objects.get(id=id)
                M_Parties_Serializer = UpdateM_PartiesSerializer(
                    M_PartiesdataByID, data=M_Partiesdata)
                if M_Parties_Serializer.is_valid():
                    M_Parties_Serializer.save()
                    log_entry = create_transaction_log(request,M_Partiesdata, 0, 0, "Party Updated Successfully",94,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_log(request,M_Partiesdata, 0, 0, M_Parties_Serializer.errors,34,id)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request,M_Partiesdata, 0, 0, Exception(e),33,id)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(id=id)
                M_Partiesdata.delete()
                log_entry = create_transaction_log(request,{'PartyID':id}, 0, 0, "Party Deleted Successfully",95,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully', 'Data': []})
        except M_Parties.DoesNotExist:
            log_entry = create_transaction_log(request,{'PartyID':id}, 0, 0, "Data Not available",7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_log(request,{'PartyID':id}, 0, 0, "Party used in another table",8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party used in another table', 'Data': []})


class BulkRetailerDataView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Retailerdata = JSONParser().parse(request)
                for aa in Retailerdata['BulkData']:
                    Retailer_serializer = M_PartiesSerializer(data=aa)
                    if Retailer_serializer.is_valid():
                        Retailer = Retailer_serializer.save()
                        LastInsertID = Retailer.id
                    else:
                        log_entry = create_transaction_log(request,Retailerdata, 0, 0, Retailer_serializer.errors,34,LastInsertID)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Retailer_serializer.errors, 'Data': []})
                log_entry = create_transaction_log(request,Retailerdata, 0, 0, "Retailer Bulk Data Import Successfully",96,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Retailer Bulk Data Import Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request,Retailerdata, 0, 0, Exception(e),33,LastInsertID)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})


class PartyAddressView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                PartiesAddress = MC_PartyAddress.objects.get(id=id)
                PartiesAddress.delete()
                log_entry = create_transaction_log(request,{'PartyID':id}, 0, 0, "Party Address Deleted Successfully",97,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Address Deleted Successfully', 'Data': []})
        except M_Parties.DoesNotExist:
            log_entry = create_transaction_log(request,{'PartyID':id}, 0, 0, 'Data Not available',7,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Address Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_log(request,{'PartyID':id}, 0, 0, 'Party Address used in transaction',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Address used in transaction', 'Data': []})


class PartiesSettingsDetailsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
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
    b.Value CompanyValue,
    c.Value PartyValue,
    (CASE WHEN a.IsPartyRelatedSetting = 1 THEN 
    (CASE WHEN c.Value is Null THEN a.DefaultValue ELSE c.Value END)
	ELSE 
    (CASE WHEN b.Value is Null THEN a.DefaultValue ELSE b.Value END)
	END) Value
FROM
    (SELECT 
        M_Settings.id AS Setting,
            M_Settings.SystemSetting AS SystemSetting,
            M_Settings.Description AS Description,
            M_Settings.DefaultValue AS DefaultValue,
            M_Settings.IsPartyRelatedSetting AS IsPartyRelatedSetting
    FROM
        M_Settings
    WHERE
        M_Settings.IsActive = 1) a
      
      
      LEFT  JOIN 
      (SELECT SettingID_id SettingID,MC_SettingsDetails.Value FROM MC_SettingsDetails WHERE MC_SettingsDetails.Company_id=%s)b
      ON a.Setting = b.SettingID
            
      LEFT JOIN
    (SELECT Setting_id SettingID, M_PartySettingsDetails.Value FROM M_PartySettingsDetails WHERE
        M_PartySettingsDetails.Party_id =%s) c ON a.Setting = c.SettingID ''', ([CompanyID], [PartyID]))
                
                a = PartiesSettingsDetailsListSerializer(
                    query, many=True).data

                log_entry = create_transaction_log(request,0, 0, PartyID, 'PartiesSettingsDetails List',98,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': a})
        except Exception as e:
            log_entry = create_transaction_log(request,0, 0, PartyID, Exception(e),7,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Retailerdata = JSONParser().parse(request)
                Party = Retailerdata['BulkData'][0]['Party']
                query = M_PartySettingsDetails.objects.filter(
                    Party=Party).all()
                query.delete()
                for aa in Retailerdata['BulkData']:
                    Partysettings_serializer = PartiesSettingSerializer(
                        data=aa)
                    if Partysettings_serializer.is_valid():
                        PartySettings = Partysettings_serializer.save()
                        LastInsertID = PartySettings.id
                    else:
                        log_entry = create_transaction_log(request,Retailerdata, 0, Party,Partysettings_serializer.errors,34,LastInsertID)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Partysettings_serializer.errors, 'Data': []})
                log_entry = create_transaction_log(request,Retailerdata, 0, Party, "Party Settings data Save Successfully",99,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Party Settings data Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_log(request,Retailerdata, 0, Party, Exception(e),33,LastInsertID)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})
