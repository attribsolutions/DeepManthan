from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Employees import *
from ..Serializer.S_Parties import *
from ..models import *
from django.db.models import F, Q
from ..Views.V_CommFunction import *

class M_EmployeesFilterView(CreateAPIView):

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
                
                if (RoleID == 1):
                    query = M_Employees.objects.raw(f'''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
                    M_Employees.PAN,M_Employees.AadharNo,M_Employees.CreatedBy,M_Employees.CreatedOn,
                    M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,
                    M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Employees.Company_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id,M_Employees.City_id,M_Employees.PIN, 
                    M_Employees.Designation AS DesignationID , M_GeneralMaster.Name AS Designation
                    FROM M_Employees
                    JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
                    JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
                    JOIN M_States ON M_States.id=M_Employees.State_id
                    JOIN M_Districts ON M_Districts.id=M_Employees.District_id
                    left JOIN M_Cities ON M_Cities.id=M_Employees.City_id
                    LEFT JOIN M_GeneralMaster ON M_GeneralMaster.id = M_Employees.Designation                
                    ''')                
                else:                   
                    SettingQuery=M_Settings.objects.filter(id=47).values("DefaultValue")
                    RoleID_List=str(SettingQuery[0]['DefaultValue'])                    
                    RoleID_list = [int(x) for x in RoleID_List.split(",")]
                   
                    if RoleID in RoleID_list:                        
                        Clause= f"And M_Employees.CreatedBy={UserID}"
                    else:
                        role_ids_str = ','.join(map(str, RoleID_list ))
                        Clause= f""" AND M_Employees.id not in (SELECT  M_Employees.id FROM M_Employees JOIN MC_RolesEmployeeTypes ON MC_RolesEmployeeTypes.EmployeeType_id = M_Employees.EmployeeType_id 
                        join M_Roles on   MC_RolesEmployeeTypes.Role_id=M_Roles.id and M_Roles.IdentifyKey != 0  
                        WHERE MC_RolesEmployeeTypes.Role_id in({role_ids_str})group by M_Employees.id)"""
                
                    query = M_Employees.objects.raw(f'''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Employees.Company_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id,M_Employees.City_id,M_Employees.PIN, M_Employees.Designation AS DesignationID, M_GeneralMaster.Name AS Designation
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id
left JOIN M_Cities ON M_Cities.id=M_Employees.City_id
LEFT JOIN M_GeneralMaster ON M_GeneralMaster.id = M_Employees.Designation 
where M_Employees.Company_id=%s {Clause}''', [CompanyID])  
                print(query)  
                if not query:
                    log_entry = create_transaction_logNew(request,Logindata,0,'List Not available',199,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employees Not available', 'Data': []})
                else:
                    M_Employees_Serializer = M_EmployeesSerializer02(
                        query, many=True).data
                    EmployeesData = list()
                    for a in M_Employees_Serializer:
                        ID = a['id']
                        query2 = MC_EmployeeParties.objects.raw(
                            '''SELECT Party_id as id, M_Parties.Name FROM MC_EmployeeParties join M_Parties on M_Parties.id = MC_EmployeeParties.Party_id where Employee_id=%s''', [ID])
                        EmployeepartiesData_Serializer = EmployeepartiesDataSerializer(
                            query2, many=True).data
                        EmployeeParties = list()
                        for b in EmployeepartiesData_Serializer:
                            EmployeeParties.append({
                                'PartyID': b['id'],
                                'Name': b['Name']
                            })
                        EmployeesData.append({
                            'id':  a['id'],
                            'Name': a['Name'],
                            'Address': a['Address'],
                            'Mobile': a['Mobile'],
                            'email': a['email'],
                            'DOB': a['DOB'],
                            'PAN': a['PAN'],
                            'AadharNo': a['AadharNo'],
                            'CreatedBy': a['CreatedBy'],
                            'CreatedOn':  a['CreatedOn'],
                            'UpdatedBy': a['UpdatedBy'],
                            'UpdatedOn': a['UpdatedOn'],
                            'CompanyName': a['CompanyName'],
                            'EmployeeTypeName': a['EmployeeTypeName'],
                            'StateName':  a['StateName'],
                            'DistrictName':  a['DistrictName'],
                            'CityName':  a['CityName'],
                            'Company_id':  a['Company_id'],
                            'EmployeeType_id':  a['EmployeeType_id'],
                            'State_id': a['State_id'],
                            'District_id':  a['District_id'],
                            'City_id':  a['City_id'],
                            'PIN':  a['PIN'],
                            'DesignationID':  a['DesignationID'],
                            'Designation':  a['Designation'],
                            'EmployeeParties': EmployeeParties
                        })
                    log_entry = create_transaction_logNew(request,Logindata,Logindata['PartyID'],'',199,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': EmployeesData})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Logindata,0,'EmployeeList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class M_EmployeesView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_Employees_Serializer = M_EmployeesSerializer(
                    data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    Employee = M_Employees_Serializer.save()
                    LastInsertID = Employee.id
                    #for log
                    if M_Employeesdata['EmployeeParties'][0]['Party'] == '':
                        x = 0
                    else:
                        x = M_Employeesdata['EmployeeParties'][0]['Party']

                    log_entry = create_transaction_logNew(request,M_Employeesdata,x,'TransactionID:'+str(LastInsertID),200,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Data Save Successfully','TransactionID':LastInsertID, 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,M_Employeesdata,0,'EmplyoeeSave:'+str(M_Employees_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Employees_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'EmplyoeeSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class M_EmployeesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Employees.Company_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id,M_Employees.City_id,M_Employees.PIN,
M_Employees.Designation AS DesignationID , M_GeneralMaster.Name AS Designation
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id 
JOIN M_Cities ON M_Cities.id=M_Employees.City_id
LEFT JOIN M_GeneralMaster ON M_GeneralMaster.id = M_Employees.Designation 
where M_Employees.id= %s''', [id])
                if not query:
                    log_entry = create_transaction_logNew(request,0,0,'Details Not available',201,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employee Not available', 'Data': []})
                else:
                    M_Employees_Serializer = M_EmployeesSerializer02(query, many=True).data

                    GetAllData = list()

                    Employeeparties = MC_EmployeeParties.objects.raw(
                        # '''SELECT Party_id as id, M_Parties.Name FROM MC_EmployeeParties join M_Parties on M_Parties.id = MC_EmployeeParties.Party_id where Employee_id=%s''', ([id]))
                        f'''SELECT  b.Role_id Role,M_Roles.Name AS RoleName,M_Parties.id  ,M_Parties.Name  from 
                        (SELECT MC_EmployeeParties.id,MC_EmployeeParties.Party_id,'0' RoleID,Employee_id FROM MC_EmployeeParties where Employee_id={id})a 
                        left join (select MC_UserRoles.Party_id,MC_UserRoles.Role_id,Employee_id FROM MC_UserRoles 
                        join M_Users on M_Users.id=MC_UserRoles.User_id WHERE M_Users.Employee_id={id})b on a.Party_id=b.Party_id 
                        left join M_Parties on M_Parties.id=a.Party_id 
                        Left join M_Roles on M_Roles.id=b.Role_id''')                    
                    
                    # EmployeepartiesData_Serializer = EmployeepartiesDataSerializer03(
                    #     Employeeparties, many=True).data

                    # EmployeeParties = list()
                   
                    # for a in EmployeepartiesData_Serializer:
                        
                    #     EmployeeParties.append({
                    #         'id': a['id'] if a['id'] is not None else '',
                    #         'Name': a['Name']if a['Name'] is not None else '',
                    #         'RoleName':a['RoleName']if a['RoleName'] is not None else ''
                    #     })     
                    # CustomPrint(Employeeparties)       
                    if not Employeeparties:
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                    else:
                        UserSerializer = EmployeepartiesDataSerializer03(Employeeparties, many=True).data   
                        # CustomPrint(UserSerializer)                                            
                        User_List = []
                        party_roles = {}  
                        for a in UserSerializer:
                            party_id = a["id"]                       
                        
                            if party_id not in party_roles:
                                party_roles[party_id] = {                               
                                    "id":a["id"],


                                    "Name": a["Name"],  
                                    "RoleName":a["RoleName"]                                                               


                                }                             
                        User_List = list(party_roles.values())   
                         
                    GetAllData.append({
                        'id':  M_Employees_Serializer[0]['id'],
                        'Name':  M_Employees_Serializer[0]['Name'],
                        'Address':  M_Employees_Serializer[0]['Address'],
                        'Mobile': M_Employees_Serializer[0]['Mobile'],
                        'email': M_Employees_Serializer[0]['email'],
                        'DOB': M_Employees_Serializer[0]['DOB'],
                        'PAN': M_Employees_Serializer[0]['PAN'],
                        'AadharNo': M_Employees_Serializer[0]['AadharNo'],
                        'CreatedBy': M_Employees_Serializer[0]['CreatedBy'],
                        'CreatedOn':  M_Employees_Serializer[0]['CreatedOn'],
                        'UpdatedBy': M_Employees_Serializer[0]['UpdatedBy'],
                        'UpdatedOn': M_Employees_Serializer[0]['UpdatedOn'],
                        'CompanyName': M_Employees_Serializer[0]['CompanyName'],
                        'EmployeeTypeName': M_Employees_Serializer[0]['EmployeeTypeName'],
                        'StateName':  M_Employees_Serializer[0]['StateName'],
                        'DistrictName':  M_Employees_Serializer[0]['DistrictName'],
                        'CityName':  M_Employees_Serializer[0]['CityName'],
                        'Company_id':  M_Employees_Serializer[0]['Company_id'],
                        'EmployeeType_id':  M_Employees_Serializer[0]['EmployeeType_id'],
                        'State_id': M_Employees_Serializer[0]['State_id'],
                        'District_id':  M_Employees_Serializer[0]['District_id'],
                        'City_id':  M_Employees_Serializer[0]['City_id'],
                        'PIN':  M_Employees_Serializer[0]['PIN'],
                        'DesignationID':  M_Employees_Serializer[0]['DesignationID'],
                        'Designation':  M_Employees_Serializer[0]['Designation'],
                        'EmployeeParties': User_List
                    })
                    log_entry = create_transaction_logNew(request,M_Employees_Serializer,0,'',201,id)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": " ", "Data": GetAllData[0]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'SingleGETEmplyoees:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        M_Employeesdata = JSONParser().parse(request)        
        try:
            with transaction.atomic():
                M_EmployeesdataByID = M_Employees.objects.get(id=id)
                # CustomPrint(M_EmployeesdataByID)
                M_Employees_Serializer = M_EmployeesSerializer(
                    M_EmployeesdataByID, data=M_Employeesdata)
                if M_Employees_Serializer.is_valid():
                    Employee = M_Employees_Serializer.save()
                    LastInsertID = Employee.id
                    log_entry = create_transaction_logNew(request,M_Employeesdata,M_Employeesdata['EmployeeParties'][0]['Party'],'TransactionID:'+str(LastInsertID),202,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,M_Employeesdata,0,'EmplyoeeEdit:'+str(M_Employees_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Employees_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,M_Employeesdata,0,'EmplyoeeEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = M_Employees.objects.get(id=id)
                M_Employeesdata.delete()
                log_entry = create_transaction_logNew(request,{'EmployeeID':id},0,'',203,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Employee data Deleted Successfully', 'Data': []})
        except M_Employees.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Employee Not available',203,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request,0,0,'EmployeeDelete:'+'Employee used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employee used in another table', 'Data': []})


class ManagementEmployeeViewList(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ManagementEmployeedata = JSONParser().parse(request)
                Company = ManagementEmployeedata['Company']
                query = M_EmployeeTypes.objects.filter(Company=Company, IsSalesTeamMember=1)
                if query.exists():
                    query2 = M_Employees.objects.filter(Company=Company, EmployeeType__in=query)
                    Employee_Serializer = M_EmployeesSerializer(
                        query2, many=True)
                    log_entry = create_transaction_logNew(request,ManagementEmployeedata,0,'Company:'+str(Company),204,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Employee_Serializer.data})
                log_entry = create_transaction_logNew(request,ManagementEmployeedata,0,'Employee Not Available',204,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Employee Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'ManagementEmployeeList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ManagementEmployeePartiesFilterView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 

                
                ManagementEmpParties_data = JSONParser().parse(request)
                EmployeeID = ManagementEmpParties_data['Employee']
                CompanyID = ManagementEmpParties_data['Company']
                query = M_Parties.objects.raw('''SELECT  a.party id,a.PartyName,a.PartyTypeName,a.StateName,a.DistrictName,b.PartyID, a.ClusterName,
                                              a.SubClusterName
                                              from (SELECT M_Parties.id AS Party,M_Parties.Name PartyName,M_PartyType.Name PartyTypeName,
                                              M_States.Name StateName,M_Districts.Name DistrictName,M_Cluster.Name as ClusterName, M_SubCluster.Name as SubClusterName 
                From M_Parties
                JOIN M_PartyType ON M_PartyType.id=M_Parties.PartyType_id 
                JOIN M_States ON M_States.id=M_Parties.State_id
                JOIN M_Districts ON M_Districts.id=M_Parties.District_id
                Left JOIN M_PartyDetails  ON M_Parties.id = M_PartyDetails.Party_id and M_PartyDetails.Group_id is null
				Left JOIN M_Cluster  ON M_PartyDetails.Cluster_id = M_Cluster.id
				Left JOIN M_SubCluster ON M_PartyDetails.SubCluster_id = M_SubCluster.id
                Where  M_PartyType.Company_id=%s AND (M_PartyType.IsRetailer=0 OR (M_PartyType.IsRetailer!=1 and M_PartyType.IsFranchises =1)) )a
                left join 
                (select Party_id PartyID from MC_ManagementParties where MC_ManagementParties.Employee_id=%s)b
                ON  a.Party = b.PartyID''', ([CompanyID], [EmployeeID]))
                
                Parties_serializer2 = M_PartiesSerializerFourth(query, many=True).data
                GetAllData = list()
                for a in Parties_serializer2:
                    GetAllData.append({
                        'id':  a['id'],
                        'Name':  a['PartyName'],
                        'PartyType': a['PartyTypeName'],
                        'State': a['StateName'],
                        'District': a['DistrictName'],
                        'Party': a['PartyID'],
                        'ClusterName' : a['ClusterName'],
                        'SubClusterName' : a['SubClusterName']
                    })
                    
                # q1=M_PartyType.objects.filter(Company=CompanyID,IsRetailer=0,IsSCM=1)
                # q0 = MC_ManagementParties.objects.filter(Employee=EmployeeID).select_related('Party')
                # CustomPrint(str(q0.query))
                # # q2=M_Parties.objects.filter(PartyType__in=q1).filter(Q(ManagementEmpparty__isnull=True)| Q(id__in=[MC_ManagementParties.Party_id for MC_ManagementParties in q0 ])).distinct().values('id','Name','PartyType','ManagementEmpparty__Party_id')
                # q2=q2=M_Parties.objects.filter(PartyType__in=q1).all()
                # CustomPrint(str(q2.query))
                # Parties_serializer = M_PartiesSerializerThird(q2,many=True).data
                # GetAllData = list()
                # for a in Parties_serializer:
                #     q3 =M_Parties.objects.filter(id=int(a['id'])).select_related('PartyType','District','State')
                #     Parties_serializer2 = M_PartiesSerializerFourth(q3,many=True).data
                #     GetAllData.append({
                #         'id':  a['id'],
                #         'Name':  a['Name'],
                #         'Party': a['ManagementEmpparty__Party_id'],
                #         'PartyType': Parties_serializer2[0]['PartyType']['Name'],
                #         'State': Parties_serializer2[0]['State']['Name'],
                #         'District': Parties_serializer2[0]['District']['Name'],
                #         })
                log_entry = create_transaction_logNew(request,ManagementEmpParties_data,0,'Company:'+str(CompanyID),380,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GetAllData})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'ManagementEmployeePartiesList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})


class ManagementEmployeePartiesSaveView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ManagementEmployeePartiesdata = JSONParser().parse(request)
                ManagementEmployeesParties_Serializer = ManagementEmployeeParties(
                    data=ManagementEmployeePartiesdata, many=True)
                if ManagementEmployeesParties_Serializer.is_valid():
                    Emploeepartiesdata = MC_ManagementParties.objects.filter(
                        Employee=ManagementEmployeesParties_Serializer.data[0]['Employee'])
                    Emploeepartiesdata.delete()
                    ManagementEmployeesParties_Serializer.save()
                    log_entry = create_transaction_logNew(request,ManagementEmployeePartiesdata,ManagementEmployeePartiesdata[0]['Party'],'',205,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Management Employee Parties Data Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,ManagementEmployeePartiesdata,ManagementEmployeePartiesdata['Party'],'ManagementEmpPartiesSave:'+str(ManagementEmployeesParties_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ManagementEmployeesParties_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'ManagementEmpPartiesSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_ManagementParties.objects.filter(Employee=id).values('Party')
                if query:
                    # q2 = M_Parties.objects.filter(id__in=query)
                    # Parties_serializer = DivisionsSerializerSecond(
                    #     q2, many=True).data
                    query =  ( M_Parties.objects.filter(id__in=query,PartyAddress__IsDefault=1)
                            .annotate(Address=F('PartyAddress__Address'),
                               PartyTypeName=F('PartyType_id__Name'),).values('id', 'Name','SAPPartyCode','Latitude','Longitude','MobileNo',  'Address',
                                   'PartyType_id','PartyTypeName'))
                    CustomPrint(query.query)
                    Partylist = list()
                    for a in query:
                        
                        Partylist.append({
                            'id':  a['id'],
                            'Name':  a['Name'],
                            'SAPPartyCode':a['SAPPartyCode'],
                            'Latitude': a['Latitude'],
                            'Longitude' : a['Longitude'],
                            'MobileNo' :a['MobileNo'],
                            'Address' :a['Address'],
                            'PartyTypeID': a['PartyType_id'],
                            'PartyType' :a['PartyTypeName']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Partylist})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Parties Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        


class PartiesEmpAllDetailsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request,id=0):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT 1 as id, M_Employees.Name EmpName, M_Employees.Address EmpAddress, Mobile EmpMobile, M_Employees.email EmpEmail, DOB, M_Employees.PAN EmpPAN, AadharNo, M_Employees.PIN EmpPIN, C1.Name EmpCity, D1.Name EmpDistrict, S1.Name EmpState, 
                                                        M_EmployeeTypes.Name EmpType, M_Parties.id PartyID,
                                                        M_Parties.Name PartyName, M_PartyType.Name PartyType, MC_PartyAddress.Address PartyAddress, FSSAINo, FSSAIExipry, MC_PartyAddress.PIN PartyPIN, M_Parties.email PartyEmail, MobileNo, AlternateContactNo, SAPPartyCode, GSTIN, M_Parties.PAN PartyPAN, 
                                                        C2.Name PartyCity, D2.Name PartyDistrict, S2.Name PartyState, M_Parties.IsDivision, MkUpMkDn, M_Parties.isActive IsPartyActive, Latitude, Longitude,
                                                        M_Users.LoginName
                                                        FROM M_Employees 
                                                        JOIN M_EmployeeTypes on EmployeeType_id = M_EmployeeTypes.id
                                                        LEFT JOIN MC_EmployeeParties ON Employee_id = M_Employees.id
                                                        LEFT JOIN M_Parties ON Party_id = M_Parties.id
                                                        JOIN M_PartyType ON PartyType_id = M_PartyType.id
                                                        LEFT JOIN MC_PartyAddress ON MC_PartyAddress.Party_id = M_Parties.id AND MC_PartyAddress.IsDefault = 1
                                                        LEFT JOIN M_Cities C1 ON M_Employees.City_id = C1.id
                                                        LEFT JOIN M_Cities C2 ON M_Parties.City_id = C2.id
                                                        JOIN M_Districts D1 ON M_Parties.District_id = D1.id
                                                        JOIN M_Districts D2 ON M_Employees.District_id = D2.id
                                                        JOIN M_States S1 ON M_Parties.State_id = S1.id
                                                        JOIN M_States S2 ON M_Employees.State_id = S2.id
                                                        LEFT JOIN M_Users ON M_Users.Employee_id = M_Employees.id
                                                        WHERE M_Parties.id IN (SELECT Party_id FROM MC_ManagementParties WHERE Employee_id = %s)''',[id])  
                
                if query:
                    PartyEmpDetails_Serializer = PartyEmpDetailsSerializer(query, many=True).data
                    PartyEmpList = list()
                    for a in PartyEmpDetails_Serializer:
                        PartyEmpList.append({
                            "EmpName" : a['EmpName'],
                            "EmpAddress":a['EmpAddress'],
                            "EmpMobile":a['EmpMobile'],
                            "EmpEmail":a['EmpEmail'],
                            "DOB":a['DOB'],
                            "EmpPAN":a['EmpPAN'],
                            "AadharNo":a['AadharNo'],
                            "EmpPIN":a['EmpPIN'],
                            "EmpDistrict":a['EmpDistrict'],
                            "EmpState" : a['EmpState'],
                            "EmpType":a['EmpType'],
                            "PartyID" :a['PartyID'],
                            "PartyName":a['PartyName'],
                            "PartyType":a['PartyType'],
                            "PartyAddress" :a['PartyAddress'],
                            "FSSAINo" :a['FSSAINo'],
                            "FSSAIExpiry" :a['FSSAIExipry'],
                            "PartyPIN" :a['PartyPIN'],
                            "PartyEmail":a['PartyEmail'],
                            "MobileNo":a['MobileNo'],
                            "AlternateContactNo":a['AlternateContactNo'],
                            "SAPPartyCode":a['SAPPartyCode'],
                            "GSTIN":a['GSTIN'],
                            "PartyPAN":a['PartyPAN'],
                            "PartyCity" : a['PartyCity'],
                            "PartyDistrict":a['PartyDistrict'],
                            "PartyState":a['PartyState'],
                            "IsDivision":a['IsDivision'],
                            "MkUpMkDn":a['MkUpMkDn'],
                            "IsPartyActive":a['IsPartyActive'],
                            "Latitude":a['Latitude'],
                            "Longitude":a['Longitude'],
                            "LoginName" : a['LoginName']
                        })
                    log_entry = create_transaction_logNew(request,PartyEmpDetails_Serializer,0,f'Party Details of EmployeeID: {id}',366,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyEmpList})
                else:
                    log_entry = create_transaction_logNew(request,PartyEmpDetails_Serializer,0,'Employee not found',366,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employee not found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'PartyEmpDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
        
          
class EmployeeSubEmployeeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)   

    @transaction.atomic()
    def get(self, request,EmployeeID=0):
        try:
            with transaction.atomic():
                
                
                
                # isSaleTeamMembrt_result = M_Employees.objects.filter(id=EmployeeID,Designation__in=['ASM','GM','MT','NH','RH','SO', 'SE','SR']).values('Designation')
                isSaleTeamMembrt_result = M_Employees.objects.raw(f'''select 1 as id,  M_Employees.Designation,M_GeneralMaster.Name from M_Employees 
left  join M_GeneralMaster on M_GeneralMaster.id=M_Employees.Designation and M_GeneralMaster.TypeID=161
where M_Employees.id={EmployeeID} and M_GeneralMaster.Name in('ASM','GM','MT','NH','RH','SO', 'SE','SR')''')
                Q =""
                if isSaleTeamMembrt_result :
                    # designation=isSaleTeamMembrt_result[0]['Designation']
                    for row in isSaleTeamMembrt_result:
                        designation=row.Name
                    Q =""
                    whereCondition= f'''where {designation}={EmployeeID}'''
                else:    
                    designation ="GM"
                    whereCondition= ""
                    Q += f'''SELECT distinct GM EmpID,'GM' Desig FROM FoodERP.M_PartyDetails union'''
                
                
                if designation == 'GM':
                    Q += f''' SELECT distinct NH EmpID,'NH' Desig FROM FoodERP.M_PartyDetails {whereCondition} union'''
                if designation == 'GM' or designation == 'NH':
                    Q += f''' SELECT distinct RH EmpID,'RH' Desig FROM FoodERP.M_PartyDetails {whereCondition} union'''    
                if designation == 'GM' or designation == 'NH' or designation == 'RH':
                    Q += f''' SELECT distinct ASM EmpID,'ASM' Desig FROM FoodERP.M_PartyDetails {whereCondition} union'''
                if designation == 'GM' or designation == 'NH' or designation == 'RH' or designation == 'ASM' :
                    Q += f''' SELECT distinct SO EmpID,'SO' Desig  FROM FoodERP.M_PartyDetails {whereCondition} union'''
                if designation == 'GM' or designation == 'NH' or designation == 'RH' or designation == 'ASM' or designation == 'SO' :
                    Q += f''' SELECT distinct SE EmpID,'SE' Desig  FROM FoodERP.M_PartyDetails {whereCondition} union'''
                if designation == 'GM' or designation == 'NH' or designation == 'RH' or designation == 'ASM' or designation == 'SO'or designation == 'SE' :
                    Q += f''' SELECT distinct SR EmpID,'SR' Desig  FROM FoodERP.M_PartyDetails {whereCondition} union'''
                if designation == 'GM' or designation == 'NH' or designation == 'RH' or designation == 'ASM' or designation == 'SO'or designation == 'SE' or designation == 'SR' :
                    Q += f''' SELECT distinct MT EmpID,'MT' Desig  FROM FoodERP.M_PartyDetails {whereCondition} '''    

                EmployeeSubEmployeeQuery=M_PartyDetails.objects.raw(f'''select EmpID id, concat(M_Employees.Name,'(', Desig,')') Employee from 
                                                            ({Q})a
                                                            join M_Employees on M_Employees.id=EmpID
                                                            where EmpID >0''')
                EMPList=list()
                for a in EmployeeSubEmployeeQuery:
                    
                    EMPList.append({
                    "id": a.id,
                    "ItemGroup": a.Employee,    
                    })
                
                    
            
            
            # log_entry = create_transaction_logNew(request,ManagementEmployeePartiesdata,ManagementEmployeePartiesdata[0]['Party'],'',205,0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': EMPList})
                
        except Exception as e:
            # log_entry = create_transaction_logNew(request,0,0,'ManagementEmpPartiesSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
