from asyncio.windows_events import NULL
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser


from ..Serializer.S_PartyTypes import PartyTypeSerializer

from ..Serializer.S_Parties import M_PartiesSerializer

from ..Serializer.S_PageAccess import H_PageAccessSerializer

from ..Serializer.S_Modules import H_ModulesSerializer

from ..Serializer.S_RoleAccess import M_RoleAccessSerializer

from ..Serializer.S_Pages import M_PagesSerializer1

from ..Serializer.S_States import DistrictsSerializer, StateSerializer

from ..Serializer.S_Companies import  C_CompanySerializer

from ..Serializer.S_CompanyGroup import C_CompanyGroupSerializer

from ..Serializer.S_Designations import M_DesignationsSerializer

from ..Serializer.S_Login import UserRegistrationSerializer

from ..Serializer.S_Employees import M_EmployeesSerializer

from ..Serializer.S_GeneralMaster import GeneralMasterserializer

from ..Serializer.S_SuperAdmin import *


class SuperAdminView(CreateAPIView):
    permission_classes = ()
    authentication_class = ()

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():


                # aaa=M_Users.objects.filter(LoginName__exact='S')
#===========================------EmployeeType------========================================================================= 
                EmployeeTypeJSON = [{
                    "Name": "SuperAdmin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "SuperAdmin",
                    "Company":1, 
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                },
                {
                    "Name": "Admin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "Admin", 
                    "Company":1, 
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }
                ]
                EmployeeType_Serializer = EmployeeTypeSerializer(
                    data=EmployeeTypeJSON ,many=True)
                if EmployeeType_Serializer.is_valid():
                    EmployeeType_Serializer.save()
                    print('EmployeeType')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  EmployeeType_Serializer.errors, 'Data': []})

#=============================------Role-------=========================================================================== 

                RoleJSON =[ {
                    "Name": "SuperAdmin",
                    "Description": "SuperAdmin",
                    "isActive":  1,
                    "isSCMRole": 0,
                    "IsPartyConnection":0,
                    "Company":1,
                    "Dashboard": "SuperAdminDashboard",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                },
                {
                    "Name": "Admin",
                    "Description": "Admin",
                    "isActive":  1,
                    "isSCMRole": 0,
                    "IsPartyConnection":0,
                    "Company":1,
                    "Dashboard": "AdminDashboard",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                }
                ]
                Role_Serializer = RoleSerializer(data=RoleJSON,many=True)
                if Role_Serializer.is_valid():
                    Role_Serializer.save()
                    print('Role')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Role_Serializer.errors, 'Data': []})

#============================-----PartyType------========================================================================= 

                PartyTypeJSON = [{
                    "Name": "Company Division",
                    "IsSCM":0,
                    "IsDivision":1,
                    "IsRetailer":0,
                    "IsVendor":0,
                    "Company":1,  
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }
                ]
                Partytypedata_Serializer = PartyTypeSerializer(
                    data=PartyTypeJSON,many=True)
                if Partytypedata_Serializer.is_valid():
                    Partytypedata_Serializer.save()
                    print('PartyType')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Partytypedata_Serializer.errors, 'Data': []})

#============================-----CompanyGroup-----=========================================================================
                CompanyGroupJSON = {
                    "Name": "Attrib Solutions",
                    "IsSCM": 0,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                }

                CompaniesGroup_Serializer = C_CompanyGroupSerializer(
                    data=CompanyGroupJSON)

                if CompaniesGroup_Serializer.is_valid():

                    CompaniesGroup_Serializer.save()
                    print('companygroup')
                else:

                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CompaniesGroup_Serializer.errors, 'Data': []})

#================================----Company----================================================================================ 

                CompanyJSON = {
                    "CompanyGroup": 1,
                    "Name": "Attrib Solutions",
                    "Address": "Pune",
                    "GSTIN": "27AAAFC5288N1ZZ",
                    "PhoneNo": "12365478952",
                    "CompanyAbbreviation": "Attrib",
                    "EmailID": "Attribsolutions@gmail.com",
                    "IsSCM": 0,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,

                }

                Companies_Serializer = C_CompanySerializer(data=CompanyJSON)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    print('Company')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Companies_Serializer.errors, 'Data': []})
                
                
#================================----General Master----================================================================================      
                
                GeneralMasterJSON =[
                    {
                    "Name": "Brand Name",
                    "IsActive": 1,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": 1,
                    "TypeID":0
                    },
                    {
                    "Name": "Party Master Bulk Update",
                    "IsActive": 1,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": 1,
                    "TypeID":0
                    },
                    {
                    "Name": "Receipt Mode",
                    "IsActive": 1,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": 1,
                    "TypeID":0
                    }
                ]

                Generalmaster_Serializer = GeneralMasterserializer(data=GeneralMasterJSON,many=True)
                if Generalmaster_Serializer.is_valid():
                    Generalmaster_Serializer.save()
                    print('General Master')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Generalmaster_Serializer.errors, 'Data': []})

#================================----state----================================================================================ 


                statesJSON = [
                    {
                        "Name": "Andaman and Nicobar Islands",
                        "StateCode": "AN",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Andhra Pradesh",
                        "StateCode": "AP",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Andhra Pradesh (New)",
                        "StateCode": "AD",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Arunachal Pradesh",
                        "StateCode": "AR",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Assam",
                        "StateCode": "AS",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Bihar",
                        "StateCode": "BH",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Chandigarh",
                        "StateCode": "CH",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Chattisgarh",
                        "StateCode": "CT",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Dadra and Nagar Haveli",
                        "StateCode": "DN",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Daman and Diu",
                        "StateCode": "DD",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Delhi",
                        "StateCode": "DL",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Goa",
                        "StateCode": "GA",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Gujarat",
                        "StateCode": "GJ",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Haryana",
                        "StateCode": "HR",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Himachal Pradesh",
                        "StateCode": "HP",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Jammu and Kashmir",
                        "StateCode": "JK",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Jharkhand",
                        "StateCode": "JH",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Karnataka",
                        "StateCode": "KA",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Kerala",
                        "StateCode": "KL",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Lakshadweep Islands",
                        "StateCode": "LD",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Madhya Pradesh",
                        "StateCode": "MP",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Maharashtra",
                        "StateCode": "MH",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Manipur",
                        "StateCode": "MN",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Meghalaya",
                        "StateCode": "ME",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Mizoram",
                        "StateCode": "MI",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Nagaland",
                        "StateCode": "NL",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Odisha",
                        "StateCode": "OR",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Pondicherry",
                        "StateCode": "PY",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Punjab",
                        "StateCode": "PB",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Rajasthan",
                        "StateCode": "RJ",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Sikkim",
                        "StateCode": "SK",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Tamil Nadu",
                        "StateCode": "TN",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Telangana",
                        "StateCode": "TS",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Tripura",
                        "StateCode": "TR",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Uttar Pradesh",
                        "StateCode": "UP",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Uttarakhand",
                        "StateCode": "UT",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "West Bengal",
                        "StateCode": "WB",
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    }]

                states_Serializer = StateSerializer(data=statesJSON, many=True)

                if states_Serializer.is_valid():
                    states_Serializer.save()
                    print('state')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': states_Serializer.errors, 'Data': []})

#================================----District----================================================================================ 

                DistrictJSON = [
                    {
                        "Name": "Ahmednagar",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Akola",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Amravati",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Aurangabad",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Beed",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Bhandara",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Buldhana",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Chandrapur",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Dhule",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Gadchiroli",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Gondia",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Hingoli",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Jalgaon",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Jalna",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Kolhapur",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Latur",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Mumbai City",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Mumbai Suburban",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Nagpur",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Nanded",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Nandurbar",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Nashik",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Osmanabad",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Palghar",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Parbhani",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Pune",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Raigad",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Ratnagiri",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Sangli",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Satara",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Sindhudurg",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Solapur",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Thane",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Wardha",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Washim",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    },
                    {
                        "Name": "Yavatmal",
                        "State": 22,
                        "CreatedBy": 1,
                        "UpdatedBy": 1
                    }
                ]

                District_Serializer = DistrictsSerializer(
                    data=DistrictJSON, many=True)
                if District_Serializer.is_valid():
                    District_Serializer.save()
                    print('District')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': District_Serializer.errors, 'Data': []})

#================================----Employee----================================================================================ 

    
                EmployeeJSON = {

                    "Name": "Super Admin",
                    "Address": "Pune",
                    "Mobile": "9860191393",
                    "email": "a.kiranmali@gmail.com",
                    "DOB": "1985-10-08",
                    "PAN": "qwer147852",
                    "AadharNo": "123456789",
                    "working_hours": "9.00",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": 1,
                    "Designation": 1,
                    "EmployeeType": 1,
                    "State": 1,
                    "District": 1,
                    "EmployeeParties": [
                        {"Party":  ""}
                        ]

                }

                Employee_Serializer = M_EmployeesSerializer(data=EmployeeJSON)
                if Employee_Serializer.is_valid():
                    Employee_Serializer.save()
                    print('Employee')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Employee_Serializer.errors, 'Data': []})

#================================----User----================================================================================ 

                UserJSON = {
                    "LoginName": "SuperAdmin",
                    "password": "1234",
                    "Employee": "1",
                    "isActive": "1",
                    "AdminPassword": "1234",
                    "isSendOTP": "0",
                    "isLoginUsingMobile": "0",
                    "isLoginUsingEmail": "0",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "UserRole": [
                                {
                                    "Party": "",
                                    "Role": 1
                                }
                    ]
                }

                Employee_Serializer = UserRegistrationSerializer(data=UserJSON)
                if Employee_Serializer.is_valid():
                    Employee_Serializer.save()
                    print('User')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Employee_Serializer.errors, 'Data': []})

#================================----Modules----================================================================================ 

                Modulesdata = [{

                    "Name": "Administration",
                    "DisplayIndex": 1,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    
                },
                {

                    "Name": "Purchase",
                    "DisplayIndex": 2,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    
                },
                {

                    "Name": "Sales",
                    "DisplayIndex": 3,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    
                },
                {

                    "Name": "Inventory",
                    "DisplayIndex": 4,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,   
                },
                {

                    "Name": "Master",
                    "DisplayIndex": 5,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,   
                },
                {

                    "Name": "Accounting",
                    "DisplayIndex": 6,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,   
                },
                {

                    "Name": "Reports",
                    "DisplayIndex": 7,
                    "isActive": 1,
                    "Icon": "home",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,   
                }
                ]
                Modules_Serializer = H_ModulesSerializer(data=Modulesdata, many=True)
                if Modules_Serializer.is_valid():
                    Modules_Serializer.save()
                    print('Module')

                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Modules_Serializer.errors, 'Data': []})

#================================----Pageaccess----================================================================================ 

                Pageaccess = [
                    {
                        "id": 1,
                        "Name": "IsShowOnMenu",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 1
                    },
                    {
                        "id": 2,
                        "Name": "IsSave",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 2
                    },
                    {
                        "id": 3,
                        "Name": "IsView",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 3
                    },
                    {
                        "id": 4,
                        "Name": "IsEdit",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 4
                    },
                    {
                        "id": 5,
                        "Name": "IsDelete",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 5
                    },
                    {
                        "id": 6,
                        "Name": "IsEditSelf",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 6
                    },
                    {
                        "id": 7,
                        "Name": "IsDeleteSelf",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 7
                    },
                    {
                        "id": 8,
                        "Name": "IsPrint",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 8
                    },
                    {
                        "id": 9,
                        "Name": "IsTopOfTheDivision",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 9
                    },
                    {
                        "id": 10,
                        "Name": "Pdfdownload",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 10
                    },
                    {
                        "id": 11,
                        "Name": "Exceldownload",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 11
                    },
                    {
                        "id": 12,
                        "Name": "IsCopy",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 12
                    },
                    {
                        "id": 13,
                        "Name": "IsMultipleInvoicePrint",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "Sequence": 13
                    }
                ]

                HPagesserializea_data = H_PageAccessSerializer(
                    data=Pageaccess, many=True)
                if HPagesserializea_data.is_valid():

                    HPagesserializea_data.save()
                    print('pagesaessee')
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  HPagesserializea_data.errors, 'Data': []})


#================================----RoleAccessdata----================================================================================ 
                
                RoleAccessdata = [
                    {
                        "Role": 1,
                        "Company":1, 
                        "Division": "",
                        "Modules": 1,
                        "Pages": 1,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 2,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 3,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 4,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 5,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 6,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 7,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company":1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 8,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 9,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 10,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company":1,
                        "Division": "",
                        "Modules": 2,
                        "Pages": 11,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 2,
                        "Pages": 12,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company": 1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 13,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company":1,
                        "Division": "",
                        "Modules": 1,
                        "Pages": 14,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company":1,
                        "Division": "",
                        "Modules": 2,
                        "Pages": 119,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    },
                    {
                        "Role": 1,
                        "Company":1,
                        "Division": "",
                        "Modules": 2,
                        "Pages": 120,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "RolePageAccess": [
                            {
                                "PageAccess": 1
                            },
                            {
                                "PageAccess": 2
                            },
                            {
                                "PageAccess": 3
                            },
                            {
                                "PageAccess": 4
                            },
                            {
                                "PageAccess": 5
                            }
                        ]
                    }

                ]
                RoleAccessSerialize_data = M_RoleAccessSerializer(data=RoleAccessdata, many=True)
                if RoleAccessSerialize_data.is_valid():
                    # RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                    #     Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                    # RoleAccessdata.delete()
                    RoleAccessSerialize_data.save()
                    print('RoleAccess')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  RoleAccessSerialize_data.errors, 'Data': []})

#========================================================================================================================== 

            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'SuperAdmin Created.....!', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})
