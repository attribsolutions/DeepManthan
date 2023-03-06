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

from ..Serializer.S_SuperAdmin import *


class SuperAdminView(CreateAPIView):
    permission_classes = ()
    authentication_class = ()

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():


                # aaa=M_Users.objects.filter(LoginName__exact='S')
#===========================------EmployeeTyep------========================================================================= 
                EmployeeTypeJSON = [{
                    "Name": "SuperAdmin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "SuperAdmin", 
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                },
                {
                    "Name": "Admin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "Admin", 
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
                    "Dashboard": "SuperAdminDashboard",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                },
                {
                    "Name": "Admin",
                    "Description": "Admin",
                    "isActive":  1,
                    "isSCMRole": 0,
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

#============================-----Designation------========================================================================= 

                DesignationJSON = [{
                    "Name": "SuperAdmin",
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                },
                {   "Name": "Admin",
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }
                ]
                Designationsdata_Serializer = M_DesignationsSerializer(
                    data=DesignationJSON,many=True)
                if Designationsdata_Serializer.is_valid():
                    Designationsdata_Serializer.save()
                    print('Designations')

                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Designationsdata_Serializer.errors, 'Data': []})

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

#================================----EMployee----================================================================================ 

    
                EmployeeJSON = {

                    "Name": "Super Admin",
                    "Address": "Baner Pune",
                    "Mobile": "9865321245",
                    "email": "superadmin@gmail.com",
                    "DOB": "1993-08-09",
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

                    "Name": "Master",
                    "DisplayIndex": 2,
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
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 1
                    },
                    {
                        "id": 2,
                        "Name": "IsSave",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 2
                    },
                    {
                        "id": 3,
                        "Name": "IsView",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 3
                    },
                    {
                        "id": 4,
                        "Name": "IsEdit",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 4
                    },
                    {
                        "id": 5,
                        "Name": "IsDelete",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 5
                    },
                    {
                        "id": 6,
                        "Name": "IsEditSelf",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 6
                    },
                    {
                        "id": 7,
                        "Name": "IsDeleteSelf",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 7
                    },
                    {
                        "id": 8,
                        "Name": "IsPrint",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 8
                    },
                    {
                        "id": 9,
                        "Name": "IsTopOfTheDivision",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 9
                    },
                    {
                        "id": 10,
                        "Name": "Pdfdownload",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 10
                    },
                    {
                        "id": 11,
                        "Name": "Exceldownload",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 11
                    },
                    {
                        "id": 12,
                        "Name": "IsCopy",
                        "CreatedBy": 1,
                        "CreatedOn": "2022-07-29T00:00:00",
                        "UpdatedBy": 1,
                        "UpdatedOn": "2022-07-29T00:00:00",
                        "Sequence": 12
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

#================================----HPages----================================================================================ 

               
                HPagesdata = [

                     {
                        "Name": "Company Master",
                        "PageHeading": "Company Master",
                        "PageDescription": "Page Description : Company Master",
                        "PageDescriptionDetails": "Page Description Details :Company Master",
                        "Module": 1,
                        "ModuleName": "Administration",
                        "isActive": 1,
                        "DisplayIndex": 3,
                        "Icon": "Company Master Icon",
                        "ActualPagePath": "CompanyMaster",
                        "PageType": 1,
                        "RelatedPageID": 0,
                        "RelatedPageName": NULL,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    
                    {
                        "Name": "Company List",
                        "PageHeading": "Company List",
                        "PageDescription": "Page Description : Company Master",
                        "PageDescriptionDetails": "Page Description Details : Company Master",
                        "Module": 1,
                        "ModuleName": "Administration",
                        "isActive": 1,
                        "DisplayIndex": 4,
                        "Icon": "Company List Icon",
                        "ActualPagePath": "CompanyList",
                        "PageType": 2,
                        "RelatedPageID": 1,
                        "RelatedPageName": "Company Master",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "PagePageAccess": [
                            {
                                "Access": 1,
                                "AccessName": "IsShowOnMenu"
                            },
                            {
                                "Access": 2,
                                "AccessName": "IsSave"
                            },
                            {
                                "Access": 3,
                                "AccessName": "IsView"
                            },
                            {
                                "Access": 4,
                                "AccessName": "IsEdit"
                            },
                            {
                                "Access": 5,
                                "AccessName": "IsDelete"
                            },
                            {
                                "Access": 6,
                                "AccessName": "IsEditSelf"
                            }
                        ],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "CompanyGroup Master",
                                "PageHeading": "CompanyGroup Master",
                                "PageDescription": "CompanyGroup Master",
                                "PageDescriptionDetails": "Page Description Details : CompanyGroup Master",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 1,
                                "Icon": "dfgdf",
                                "ActualPagePath": "CompanyGroupMaster",
                                "PageType": 1,
                                "RelatedPageID": 0,
                                "RelatedPageName": NULL,
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "CompanyGroup List",
                                "PageHeading": "CompanyGroup List",
                                "PageDescription": "CompanyGroup List",
                                "PageDescriptionDetails": "Page Description Details : CompanyGroup List",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 2,
                                "Icon": "erht",
                                "ActualPagePath": "CompanyGroupList",
                                "PageType": 2,
                                "RelatedPageID": 3,
                                "RelatedPageName": "CompanyGroupMaster",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [
                                    {
                                    "Access": 1,
                                    "AccessName": "IsShowOnMenu"
                                    },
                                    {
                                    "Access": 2,
                                    "AccessName": "IsSave"
                                    },
                                    {
                                    "Access": 3,
                                    "AccessName": "IsView"
                                    },
                                    {
                                    "Access": 6,
                                    "AccessName": "IsEditSelf"
                                    },
                                    {
                                    "Access": 4,
                                    "AccessName": "IsEdit"
                                    },
                                    {
                                    "Access": 5,
                                    "AccessName": "IsDelete"
                                    },
                                    {
                                    "Access": 8,
                                    "AccessName": "IsPrint"
                                    }
                                ],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "Module Master",
                                "PageHeading": "Module Master",
                                "PageDescription": "Module Master",
                                "PageDescriptionDetails": "Module Master",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 5,
                                "Icon": "dfasdf",
                                "ActualPagePath": "ModuleMaster",
                                "PageType": 1,
                                "RelatedPageID": 0,
                                "RelatedPageName": "Module List",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "Module List",
                                "PageHeading": "Module List",
                                "PageDescription": "Module List",
                                "PageDescriptionDetails": "Module List",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 6,
                                "Icon": "xfgd",
                                "ActualPagePath": "ModuleList",
                                "PageType": 2,
                                "RelatedPageID": 5,
                                "RelatedPageName": "Module Master",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [
                                    {
                                    "Access": 1,
                                    "AccessName": "IsShowOnMenu"
                                    },
                                    {
                                    "Access": 2,
                                    "AccessName": "IsSave"
                                    },
                                    {
                                    "Access": 3,
                                    "AccessName": "IsView"
                                    },
                                    {
                                    "Access": 6,
                                    "AccessName": "IsEditSelf"
                                    },
                                    {
                                    "Access": 4,
                                    "AccessName": "IsEdit"
                                    },
                                    {
                                    "Access": 5,
                                    "AccessName": "IsDelete"
                                    }
                                ],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "PageMaster",
                                "PageHeading": "PageMaster",
                                "PageDescription": "PageMaster",
                                "PageDescriptionDetails": "PageMaster",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 7,
                                "Icon": "fa-fa-paw",
                                "ActualPagePath": "PageMaster",
                                "PageType": 1,
                                "RelatedPageID": 0,
                                "RelatedPageName": "PageList",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "PageList",
                                "PageHeading": "PageList",
                                "PageDescription": "PageList",
                                "PageDescriptionDetails": "PageList",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 8,
                                "Icon": "fa-fa-paw",
                                "ActualPagePath": "PageList",
                                "PageType": 2,
                                "RelatedPageID": 7,
                                "RelatedPageName": "PageMaster",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [
                                    {
                                    "Access": 1,
                                    "AccessName": "IsShowOnMenu"
                                    },
                                    {
                                    "Access": 2,
                                    "AccessName": "IsSave"
                                    },
                                    {
                                    "Access": 5,
                                    "AccessName": "IsDelete"
                                    },
                                    {
                                    "Access": 3,
                                    "AccessName": "IsView"
                                    },
                                    {
                                    "Access": 6,
                                    "AccessName": "IsEditSelf"
                                    },
                                    {
                                    "Access": 4,
                                    "AccessName": "IsEdit"
                                    }
                                ],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "Role Access",
                                "PageHeading": "Role Access",
                                "PageDescription": "Role Access",
                                "PageDescriptionDetails": "Role Access",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 9,
                                "Icon": "a",
                                "ActualPagePath": "RoleAccess",
                                "PageType": 1,
                                "RelatedPageID": 0,
                                "RelatedPageName": NULL,
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "RoleAccess List",
                                "PageHeading": "RoleAccess List",
                                "PageDescription": "RoleAccess List",
                                "PageDescriptionDetails": "RoleAccess List",
                                "Module": 1,
                                "ModuleName": "Administration",
                                "isActive": 1,
                                "DisplayIndex": 10,
                                "Icon": "wsd",
                                "ActualPagePath": "RoleAccessList",
                                "PageType": 2,
                                "RelatedPageID": 9,
                                "RelatedPageName": "Role Access",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [
                                    {
                                    "Access": 1,
                                    "AccessName": "IsShowOnMenu"
                                    },
                                    {
                                    "Access": 2,
                                    "AccessName": "IsSave"
                                    },
                                    {
                                    "Access": 3,
                                    "AccessName": "IsView"
                                    },
                                    {
                                    "Access": 6,
                                    "AccessName": "IsEditSelf"
                                    },
                                    {
                                    "Access": 4,
                                    "AccessName": "IsEdit"
                                    },
                                    {
                                    "Access": 5,
                                    "AccessName": "IsDelete"
                                    }
                                ],
                        "PageFieldMaster": []
                    },
                    # {
                    #             "Name": "Role Master",
                    #             "PageHeading": "Role Master",
                    #             "PageDescription": "Role Master",
                    #             "PageDescriptionDetails": "Role Master",
                    #             "Module": 1,
                    #             "ModuleName": "Administration",
                    #             "isActive": 1,
                    #             "DisplayIndex": 12,
                    #             "Icon": "sfdgsdfgsg",
                    #             "ActualPagePath": "RoleMaster",
                    #             "PageType": 1,
                    #             "RelatedPageID": 0,
                    #             "RelatedPageName": NULL,
                    #             "PagePageAccess": []
                    # },
                    # {
                    #             "Name": "Role List",
                    #             "PageHeading": "Role List",
                    #             "PageDescription": "Role List",
                    #             "PageDescriptionDetails": "Role List",
                    #             "Module": 1,
                    #             "ModuleName": "Administration",
                    #             "isActive": 1,
                    #             "DisplayIndex": 13,
                    #             "Icon": "adfg",
                    #             "ActualPagePath": "RoleList",
                    #             "PageType": 2,
                    #             "RelatedPageID": 11,
                    #             "RelatedPageName": "Role Master",
                    #             "PagePageAccess": [
                    #                 {
                    #                 "AccessID": 1,
                    #                 "AccessName": "IsShowOnMenu"
                    #                 },
                    #                 {
                    #                 "AccessID": 2,
                    #                 "AccessName": "IsSave"
                    #                 },
                    #                 {
                    #                 "AccessID": 3,
                    #                 "AccessName": "IsView"
                    #                 },
                    #                 {
                    #                 "AccessID": 6,
                    #                 "AccessName": "IsEditSelf"
                    #                 },
                    #                 {
                    #                 "AccessID": 4,
                    #                 "AccessName": "IsEdit"
                    #                 },
                    #                 {
                    #                 "AccessID": 5,
                    #                 "AccessName": "IsDelete"
                    #                 }
                    #             ]
                    # },
                    {
                                "Name": "Employee Master",
                                "PageHeading": "Employee Master",
                                "PageDescription": "Employee Master",
                                "PageDescriptionDetails": "Employee Master",
                                "Module": 2,
                                "ModuleName": "Master",
                                "isActive": 1,
                                "DisplayIndex": 1,
                                "Icon": "sdfc",
                                "ActualPagePath": "EmployeeMaster",
                                "PageType": 1,
                                "RelatedPageID": 0,
                                "RelatedPageName": "Employee List",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    {
                                "Name": "Employee List",
                                "PageHeading": "Employee List",
                                "PageDescription": "Employee List",
                                "PageDescriptionDetails": "Employee List",
                                "Module": 2,
                                "ModuleName": "Master",
                                "isActive": 1,
                                "DisplayIndex": 2,
                                "Icon": "sf",
                                "ActualPagePath": "EmployeeList",
                                "PageType": 2,
                                "RelatedPageID": 11,
                                "RelatedPageName": "Employee Master",
                                "CreatedBy": 1,
                                "UpdatedBy": 1,
                                "PagePageAccess": [
                                    {
                                    "Access": 1,
                                    "AccessName": "IsShowOnMenu"
                                    },
                                    {
                                    "Access": 2,
                                    "AccessName": "IsSave"
                                    },
                                    {
                                    "Access": 3,
                                    "AccessName": "IsView"
                                    },
                                    {
                                    "Access": 6,
                                    "AccessName": "IsEditSelf"
                                    },
                                    {
                                    "Access": 4,
                                    "AccessName": "IsEdit"
                                    },
                                    {
                                    "Access": 5,
                                    "AccessName": "IsDelete"
                                    }
                                ],
                        "PageFieldMaster": []
                    },
                   
                    {
                        "Name": "User Master",
                        "PageHeading": "Registration",
                        "PageDescription": "Registration Page",
                        "PageDescriptionDetails": "New User Registration",
                        "Module": 1,
                        "ModuleName": "Administration",
                        "isActive": 1,
                        "DisplayIndex": 11,
                        "Icon": "fa-fa-paw",
                        "ActualPagePath": "UserMaster",
                        "PageType": 1,
                        "RelatedPageID": 0,
                        "RelatedPageName": NULL,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "PagePageAccess": [],
                        "PageFieldMaster": []
                    },
                    {
                        "Name": "User List",
                        "PageHeading": "User List",
                        "PageDescription": "All Users",
                        "PageDescriptionDetails": "User List",
                        "Module": 1,
                        "ModuleName": "Administration",
                        "isActive": 1,
                        "DisplayIndex": 12,
                        "Icon": "fa-fa-paw",
                        "ActualPagePath": "UserList",
                        "PageType": 2,
                        "RelatedPageID": 13,
                        "RelatedPageName": "User Master",
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "PagePageAccess": [
                            {
                                "Access": 1,
                                "AccessName": "IsShowOnMenu"
                            },
                            {
                                "Access": 2,
                                "AccessName": "IsSave"
                            },
                            {
                                "Access": 5,
                                "AccessName": "IsDelete"
                            },
                            {
                                "Access": 3,
                                "AccessName": "IsView"
                            },
                            {
                                "Access": 6,
                                "AccessName": "IsEditSelf"
                            },
                            {
                                "Access": 4,
                                "AccessName": "IsEdit"
                            }
                        ],
                        "PageFieldMaster": []
                    }
                ]


                # HPagesserialize_data = M_PagesSerializer1(
                #     data=HPagesdata, many=True)
                # if HPagesserialize_data.is_valid():
                #     HPagesserialize_data.save()
                #     print('pages')
                #     # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Page Save Successfully', 'Data': []})
                # else:
                #     transaction.set_rollback(True)
                #     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  HPagesserialize_data.errors, 'Data': []})

#================================----RoleAccessdata----================================================================================ 
                
                RoleAccessdata = [
                    {
                        "Role": 1,
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                        "Company": "",
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
                    }

                ]
                # RoleAccessSerialize_data = M_RoleAccessSerializer(data=RoleAccessdata, many=True)
                # if RoleAccessSerialize_data.is_valid():
                   
                #     RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                #         Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                #     RoleAccessdata.delete()
                #     RoleAccessSerialize_data.save()
                #     print('RoleAccess')
                # else:
                #     transaction.set_rollback(True)
                #     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  RoleAccessSerialize_data.errors, 'Data': []})

#========================================================================================================================== 

            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'SuperAdmin Created.....!', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})
