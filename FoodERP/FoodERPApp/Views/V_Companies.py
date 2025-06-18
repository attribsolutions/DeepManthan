from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_EmployeeTypes import M_EmployeeTypeSerializer
from ..Serializer.S_Companies import *
from ..Serializer.S_Login import UserRegistrationSerializer
from ..Serializer.S_Employees import M_EmployeesSerializer
from ..models import C_Companies
from ..Views.V_CommFunction import *


class C_CompaniesViewFilter(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
                   
    @transaction.atomic()
    def post(self, request):
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 

                if(RoleID == 1 ):
                    Groupquery = C_Companies.objects.all()
                else:
                    Groupquery = C_Companies.objects.filter(id=CompanyID)
               
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = C_CompanySerializerSecond(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "IsSCM" : a['IsSCM'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    log_entry = create_transaction_logNew(request, Logindata,0,'',305,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList})
                log_entry = create_transaction_logNew(request, Logindata,0,'Company Not available',305,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Company Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Logindata, 0,'GETLogindata:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})                


class C_CompaniesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
                   
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.all()
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = C_CompanySerializerSecond(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "IsSCM" : a['IsSCM'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    log_entry = create_transaction_logNew(request, Companydata,0,'',306,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList})
                log_entry = create_transaction_logNew(request, Companydata,0,'Company Not available',306,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Company Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllCompanyDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})                

    @transaction.atomic()
    def post(self, request):
        Companiesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                AdminDivisionDatalist=list()
                
                AdminDivisionDatalist.append({
                        "Name": Companiesdata['Name']+' AdminDivision',
                        "PartyType": 1,
                        "Company": 1,
                        "PAN": "AAAAA1234A",
                        "Email": Companiesdata['EmailID'],
                        "MobileNo": Companiesdata['PhoneNo'],
                        "AlternateContactNo": "",
                        "State": 22,
                        "District": 26,
                        "Taluka": 0,
                        "City": "",
                        "GSTIN": Companiesdata['GSTIN'],
                        "MkUpMkDn": False,
                        "isActive": True,
                        "IsDivision": True,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "IsRetailer" : 0,
                        "PartyAddress":[{
                            "Address":"Pune",
                            "FSSAINo":"",
                            "FSSAIExipry":"2024-10-17",
                            "PIN":"411009",
                            "IsDefault":1,
                            "fssaidocument":"",
                            "Party_id":""
                        }]
                        
              })
                
                EmployeeJSON = {

                    "Name": Companiesdata['Name']+' Admin Employee',
                    "Address": "pune",
                    "Mobile": Companiesdata['PhoneNo'],
                    "email": Companiesdata['EmailID'],
                    "DOB": "1985-10-08",
                    "PAN": "AAAAA1234A",
                    "AadharNo": "123456789234",
                    "working_hours": "9.00",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": 1,
                    "EmployeeType": 2,
                    "State": 22,
                    "District": 26,
                    "City": "",
                    "EmployeeParties": [
                        {"Party":  ""}
                        ]

                }
                
                UserJSON = {
                    "LoginName": Companiesdata['Name']+' Admin',
                    "password": "1234",
                    "Employee": "1",
                    "isActive": "1",
                    "AdminPassword": "1234",
                    "isSendOTP": "0",
                    "isLoginUsingMobile": "0",
                    "isLoginUsingEmail": "0",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "last_activity" : '2023-04-01 00:00:00',
                    "POSRateType" : 0,
                    "UserRole": [
                                {
                                    "Party": "",
                                    "Role": 2
                                }
                    ]
                }
                
                Companies_Serializer = C_CompanySerializer(data=Companiesdata)
                
                AdminDivisionDatalist_Serializer=M_PartySerializer(data=AdminDivisionDatalist,many=True)
                
                Employee_Serializer = M_EmployeesSerializer(data=EmployeeJSON)
                
                UserRegistration_Serializer = UserRegistrationSerializer(data=UserJSON)
                
                
                if (Companies_Serializer.is_valid() and AdminDivisionDatalist_Serializer.is_valid() and Employee_Serializer.is_valid() and UserRegistration_Serializer.is_valid()):
                    Companies_Serializer.save()
                    # CustomPrint(Companies_Serializer)
                    CompanyID=Companies_Serializer.data['id']

                    AdminDivisionDatalist_Serializer.save()
                    # CustomPrint(AdminDivisionDatalist_Serializer)
                    partyID=AdminDivisionDatalist_Serializer.data[0]['id']
                    M_Parties.objects.filter(id=partyID).update(Company=CompanyID)

                    Employee_Serializer.save()
                    # CustomPrint(Employee_Serializer)
                    EmployeeID=Employee_Serializer.data['id']
                    M_Employees.objects.filter(id=EmployeeID).update(Company=CompanyID)
                    MC_EmployeeParties.objects.filter(Employee=EmployeeID).update(Party=partyID)

                    UserRegistration_Serializer.save()
                    # CustomPrint(UserRegistration_Serializer)
                    UserID=UserRegistration_Serializer.data['id']
                    M_Users.objects.filter(id=UserID).update(Employee=EmployeeID)
                    MC_UserRoles.objects.filter(User=UserID).update(Party=partyID)
                    # log_entry = create_transaction_logNew(request, Companiesdata,0,'',307,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Save Successfully', 'Data':[]})
                else:
                    # log_entry = create_transaction_logNew(request, Companiesdata,0,'CompanySave:'+str(Employee_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':str(Companies_Serializer.errors) +','+  str(Employee_Serializer.errors) +','+ str(AdminDivisionDatalist_Serializer.errors) +','+ str(UserRegistration_Serializer.errors), 'Data':[]})
        except IntegrityError:   
            # log_entry = create_transaction_logNew(request, 0,0,'Company used in another table',8,0)  
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company used in another table', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, Companiesdata, 0,'CompanySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            
     
class C_CompaniesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.filter(id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = C_CompanySerializerSecond(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "IsSCM" : a['IsSCM'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                        log_entry = create_transaction_logNew(request, Companydata,0,'',308,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList[0]})
                log_entry = create_transaction_logNew(request, Companydata,0,'Company Not available',308,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Company Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETSingleCompanyDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})



    @transaction.atomic()
    def put(self, request, id=0):
        Companiesdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                CompaniesdataByID = C_Companies.objects.get(id=id)
                Companies_Serializer = C_CompanySerializer(
                    CompaniesdataByID, data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    log_entry = create_transaction_logNew(request, Companiesdata,0,'CompanyID:'+str(id),309,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Companiesdata,0,'CompanyEdit:'+str(Companies_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Companiesdata,0,'CompanyEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})   
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(id=id)
                Companiesdata.delete()
                log_entry = create_transaction_logNew(request, 0,0,'CompanyID:'+str(id),310,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Deleted Successfully', 'Data':[]})
        except C_Companies.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Company Not available',310,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Not available', 'Data': []})
        except IntegrityError:  
            log_entry = create_transaction_logNew(request, 0,0,'Company used in another table',8,0)   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company used in another table', 'Data': []})   



''' Below class used on Party Master Company Dropdown Populate Here we Check Division is IsSCM Or not. If IsSCM Then We show IsSCM Company Else Other'''
class GetCompanyByDivisionType(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                PartyType = M_PartyType.objects.filter(id=id).values('id','Name','IsSCM','IsDivision')
                # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data':str(PartyType.query) })
                if PartyType.exists():
                    PartyTypedata_Serializer = PartyTypeserializer(PartyType, many=True).data
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data': PartyTypedata_Serializer[0]['IsSCM'] })
                    CompaniesData = C_Companies.objects.filter(IsSCM=PartyTypedata_Serializer[0]['IsSCM'])
                    if CompaniesData.exists():
                        C_Companiesdata_Serializer = C_CompanySerializer(CompaniesData, many=True).data
                        # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data': C_Companiesdata_Serializer })
                        log_entry = create_transaction_logNew(request, C_Companiesdata_Serializer,0,'',311,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': ' ' , 'Data':C_Companiesdata_Serializer })
                log_entry = create_transaction_logNew(request, 0,0,'Party Types Not available',311,0)   
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Types Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'PartyTypes:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})               

class GetCompanyByEmployeeType(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                EmployeeTypesdata = M_EmployeeTypes.objects.get(id=id)
                EmployeeTypesdata_Serializer = M_EmployeeTypeSerializer(EmployeeTypesdata).data
                
                Companiesdata = C_Companies.objects.filter(IsSCM=EmployeeTypesdata_Serializer['IsSCM'])
                Companiesdata_Serializer = C_CompanySerializer(Companiesdata, many=True)
                log_entry = create_transaction_logNew(request, Companiesdata_Serializer,0,'',312,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': Companiesdata_Serializer.data})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'Companiesdata:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})   