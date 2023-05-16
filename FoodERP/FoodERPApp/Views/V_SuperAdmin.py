from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from django.db import transaction


from ..Serializer.S_PartyTypes import PartyTypeSerializer




from ..Serializer.S_RoleAccess import M_RoleAccessSerializer



from ..Serializer.S_Companies import  C_CompanySerializer

from ..Serializer.S_CompanyGroup import C_CompanyGroupSerializer


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
