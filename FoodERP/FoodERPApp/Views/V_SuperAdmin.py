from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_States import DistrictsSerializer, StateSerializer

from ..Serializer.S_Companies import C_CompanyGroupsSerializer, C_CompanyGroupsSerializer1, C_CompanySerializer2

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
                EmployeeTypeJSON = {
                    "Name": "SuperAdmin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "SuperAdmin",
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }

                EmployeeType_Serializer = EmployeeTypeSerializer(
                    data=EmployeeTypeJSON)
                if EmployeeType_Serializer.is_valid():
                    EmployeeType_Serializer.save()
                    print('EmployeeType')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  EmployeeType_Serializer.errors, 'Data': []})

                RoleJSON = {
                    "Name": "SuperAdmin",
                    "Description": "SuperAdmin",
                    "isActive":  1,
                    "isSCMRole": 0,
                    "Dashboard": "SuperAdminDashboard",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                }

                Role_Serializer = RoleSerializer(data=RoleJSON)
                if Role_Serializer.is_valid():
                    Role_Serializer.save()
                    print('Role')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Role_Serializer.errors, 'Data': []})

                DesignationJSON = {
                    "Name": "SuperAdmin",
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }

                Designationsdata_Serializer = M_DesignationsSerializer(
                    data=DesignationJSON)
                if Designationsdata_Serializer.is_valid():
                    Designationsdata_Serializer.save()
                    print('Designations')
                   
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Designationsdata_Serializer.errors, 'Data': []})

                CompanyGroupJSON = {
                    "Name": "Attrib Solutions",
                    "IsSCM"  : 0,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                }
               
                CompaniesGroup_Serializer = C_CompanyGroupsSerializer1(
                    data=CompanyGroupJSON)
                
                if CompaniesGroup_Serializer.is_valid():
                    
                    CompaniesGroup_Serializer.save()
                    print('companygroup')
                else:
                    
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CompaniesGroup_Serializer.errors, 'Data':[]})
                
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
                
                Companies_Serializer = C_CompanySerializer2(data=CompanyJSON)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    print('Company')
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Companies_Serializer.errors, 'Data':[]})
                
                print('States0')


                
                statesJSON =[
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

                states_Serializer = StateSerializer(data=statesJSON , many=True)
                
                if states_Serializer.is_valid():
                   states_Serializer.save()
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': states_Serializer.errors, 'Data': []})
                
                

                DistrictJSON =   [
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

                   
                District_Serializer = DistrictsSerializer(data=DistrictJSON, many=True)
                if District_Serializer.is_valid():
                    District_Serializer.save()
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': District_Serializer.errors, 'Data': []})
                
                
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

            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'SuperAdmin Created.....!', 'Data': []})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data': []})
