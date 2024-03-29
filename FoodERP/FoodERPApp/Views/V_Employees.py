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
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']
                RoleID = Logindata['RoleID']
                CompanyID = Logindata['CompanyID']

                if (RoleID == 1):
                    query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Employees.Company_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id,M_Employees.City_id,M_Employees.PIN
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id
JOIN M_Cities ON M_Cities.id=M_Employees.City_id
''')
                else:
                    query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Employees.Company_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id,M_Employees.City_id,M_Employees.PIN
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id

JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id
JOIN M_Cities ON M_Cities.id=M_Employees.City_id
where M_Employees.CreatedBy=%s
''', [UserID])
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
                            'EmployeeParties': EmployeeParties
                        })
                    log_entry = create_transaction_logNew(request,Logindata,Logindata['PartyID'],'',199,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': EmployeesData})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'EmployeeList:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


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
            log_entry = create_transaction_logNew(request,0,0,'EmplyoeeSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class M_EmployeesViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name,M_Employees.Address,M_Employees.Mobile,M_Employees.email,M_Employees.DOB,
M_Employees.PAN,M_Employees.AadharNo,M_Employees.CreatedBy,M_Employees.CreatedOn,
M_Employees.UpdatedBy,M_Employees.UpdatedOn,C_Companies.Name CompanyName,
M_EmployeeTypes.Name EmployeeTypeName,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Employees.Company_id,M_Employees.EmployeeType_id,M_Employees.State_id,M_Employees.District_id,M_Employees.City_id,M_Employees.PIN 
FROM M_Employees
JOIN C_Companies ON C_Companies.id=M_Employees.Company_id
JOIN M_EmployeeTypes ON M_EmployeeTypes.id=M_Employees.EmployeeType_id
JOIN M_States ON M_States.id=M_Employees.State_id
JOIN M_Districts ON M_Districts.id=M_Employees.District_id 
JOIN M_Cities ON M_Cities.id=M_Employees.City_id

where M_Employees.id= %s''', [id])
                if not query:
                    log_entry = create_transaction_logNew(request,0,0,'Details Not available',201,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employee Not available', 'Data': []})
                else:
                    M_Employees_Serializer = M_EmployeesSerializer02(query, many=True).data

                    GetAllData = list()

                    Employeeparties = MC_EmployeeParties.objects.raw(
                        '''SELECT Party_id as id, M_Parties.Name FROM MC_EmployeeParties join M_Parties on M_Parties.id = MC_EmployeeParties.Party_id where Employee_id=%s''', ([id]))
                    EmployeepartiesData_Serializer = EmployeepartiesDataSerializer(
                        Employeeparties, many=True).data

                    EmployeeParties = list()
                    for a in EmployeepartiesData_Serializer:
                        EmployeeParties.append({
                            'id': a['id'],
                            'Name': a['Name']
                        })

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
                        'EmployeeParties': EmployeeParties
                    })
                    log_entry = create_transaction_logNew(request,M_Employees_Serializer,0,'',201,id)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": " ", "Data": GetAllData[0]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'SingleGETEmplyoees:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Employeesdata = JSONParser().parse(request)
                M_EmployeesdataByID = M_Employees.objects.get(id=id)

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
            log_entry = create_transaction_logNew(request,0,0,'EmplyoeeEdit:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

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
                query = M_EmployeeTypes.objects.filter(
                    Company=Company, IsSalesTeamMember=1)
                if query.exists():
                    query2 = M_Employees.objects.filter(
                        Company=Company, EmployeeType__in=query)
                    Employee_Serializer = M_EmployeesSerializer(
                        query2, many=True)
                    log_entry = create_transaction_logNew(request,ManagementEmployeedata,0,'Company:'+str(Company),204,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Employee_Serializer.data})
                log_entry = create_transaction_logNew(request,ManagementEmployeedata,0,'Employee Not Available',204,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Employee Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'ManagementEmployeeList:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


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
                query = M_Parties.objects.raw('''SELECT  a.party id,a.PartyName,a.PartyTypeName,a.StateName,a.DistrictName,b.PartyID from (SELECT M_Parties.id AS Party,M_Parties.Name PartyName,M_PartyType.Name PartyTypeName,M_States.Name StateName,M_Districts.Name DistrictName 
                From M_Parties
                JOIN M_PartyType ON M_PartyType.id=M_Parties.PartyType_id 
                JOIN M_States ON M_States.id=M_Parties.State_id
                JOIN M_Districts ON M_Districts.id=M_Parties.District_id
                Where  M_PartyType.Company_id=%s AND M_PartyType.IsRetailer=0 AND M_PartyType.IsSCM=1 OR M_PartyType.IsFranchises=1)a
                left join 
                (select Party_id PartyID from MC_ManagementParties where MC_ManagementParties.Employee_id=%s)b
                ON  a.Party = b.PartyID''', ([CompanyID], [EmployeeID]))
                Parties_serializer2 = M_PartiesSerializerFourth(
                    query, many=True).data
                GetAllData = list()
                for a in Parties_serializer2:
                    GetAllData.append({
                        'id':  a['id'],
                        'Name':  a['PartyName'],
                        'PartyType': a['PartyTypeName'],
                        'State': a['StateName'],
                        'District': a['DistrictName'],
                        'Party': a['PartyID']
                    })
                    
                # q1=M_PartyType.objects.filter(Company=CompanyID,IsRetailer=0,IsSCM=1)
                # q0 = MC_ManagementParties.objects.filter(Employee=EmployeeID).select_related('Party')
                # print(str(q0.query))
                # # q2=M_Parties.objects.filter(PartyType__in=q1).filter(Q(ManagementEmpparty__isnull=True)| Q(id__in=[MC_ManagementParties.Party_id for MC_ManagementParties in q0 ])).distinct().values('id','Name','PartyType','ManagementEmpparty__Party_id')
                # q2=q2=M_Parties.objects.filter(PartyType__in=q1).all()
                # print(str(q2.query))
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
                log_entry = create_transaction_logNew(request,ManagementEmpParties_data,0,'Company:'+str(CompanyID),204,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GetAllData})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'ManagementEmployeePartiesFilter:'+str(e),33,0)
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
            log_entry = create_transaction_logNew(request,0,0,'ManagementEmpPartiesSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_ManagementParties.objects.filter(
                    Employee=id).values('Party')
                if query.exists():
                    q2 = M_Parties.objects.filter(id__in=query)
                    Parties_serializer = DivisionsSerializerSecond(
                        q2, many=True).data
                    Partylist = list()
                    for a in Parties_serializer:
                        Partylist.append({
                            'id':  a['id'],
                            'Name':  a['Name'],
                            'SAPPartyCode':a['SAPPartyCode'],
                            'Latitude': a['Latitude'],
                            'Longitude' : a['Longitude'],
                            'MobileNo' :a['MobileNo'],
                            'Address' :a['Address']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Partylist})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Parties Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
