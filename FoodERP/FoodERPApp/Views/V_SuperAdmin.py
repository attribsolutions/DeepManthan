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

from ..Serializer.S_Parties import *


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
                
                CompaniesGroup_Serializer = C_CompanyGroupSerializer(data=CompanyGroupJSON)
                
                if not CompaniesGroup_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CompaniesGroup_Serializer.errors, 'Data': []})
                company_group_instance = CompaniesGroup_Serializer.save()
                Company_GroupID = company_group_instance.id  # Store CompanyGroup ID
                print('CompanyGroup created')
                
#================================----Company----================================================================================ 

                CompanyJSON = {
                    "CompanyGroup": Company_GroupID,
                    "Name": "Attrib Solutions",
                    "Address": "Pune",
                    "GSTIN": "27AAAFC5288N1ZZ",
                    "PhoneNo": "12365478952",
                    "CompanyAbbreviation": "Attrib",
                    "EmailID": "attribsolutions@gmail.com",
                    "IsSCM": 0,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,

                }
                
                Companies_Serializer = C_CompanySerializer(data=CompanyJSON)
                
                if not Companies_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data': []})
                company_instance = Companies_Serializer.save()
                CompanyID = company_instance.id  # Store Company ID
                print('Company created')   
                
#===========================------EmployeeType------========================================================================= 
                EmployeeTypeJSON = [{
                    "Name": "SuperAdmin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "SuperAdmin",
                    "Company":CompanyID, 
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                },
                {
                    "Name": "Admin",
                    "IsPartyConnection": 0,
                    "IsSCM": 0,
                    "Description": "Admin", 
                    "Company":CompanyID, 
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }
                ]
                
                EmployeeType_Serializer = EmployeeTypeSerializer(data=EmployeeTypeJSON, many=True)
                
                if not EmployeeType_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': EmployeeType_Serializer.errors, 'Data': []})
                employee_type_instances = EmployeeType_Serializer.save()
                Employee_TypeID = employee_type_instances[0].id  # Store SuperAdmin EmployeeType ID
                print('EmployeeType created')

#=============================------Role-------=========================================================================== 

                RoleJSON =[ {
                    "Name": "SuperAdmin",
                    "Description": "SuperAdmin",
                    "isActive":  1,
                    "isSCMRole": 0,
                    "IsPartyConnection":0,
                    "Company":CompanyID,
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
                    "Company":CompanyID,
                    "Dashboard": "AdminDashboard",
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                }
                ]
                
                Role_Serializer = RoleSerializer(data=RoleJSON, many=True)
                if not Role_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Role_Serializer.errors, 'Data': []})
                role_instances = Role_Serializer.save()
                RoleID = role_instances[0].id  # Store SuperAdmin Role ID
                print('Role created')

#============================-----PartyType------========================================================================= 

                PartyTypeJSON = [{
                    "Name": "Company Division",
                    "IsSCM":0,
                    "IsDivision":1,
                    "IsRetailer":0,
                    "IsVendor":0,
                    "Company":CompanyID, 
                    "SAPIndicator" : 0, 
                    "CreatedBy": 1,
                    "UpdatedBy": 1
                }
                ]
                
                Partytypedata_Serializer = PartyTypeSerializer(data=PartyTypeJSON, many=True)
                
                if not Partytypedata_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Partytypedata_Serializer.errors, 'Data': []})
                party_type_instance = Partytypedata_Serializer.save()
                PartyTypeID = party_type_instance[0].id  # Store PartyType ID
                print('PartyType created')
                
#================================----General Master----================================================================================      
                
                GeneralMasterJSON =[
                    {
                    "Name": "Brand Name",
                    "IsActive": 1,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": CompanyID,
                    "TypeID":0
                    },
                    {
                    "Name": "Party Master Bulk Update",
                    "IsActive": 1,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": CompanyID,
                    "TypeID":0
                    },
                    {
                    "Name": "Receipt Mode",
                    "IsActive": 1,
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "Company": CompanyID,
                    "TypeID":0
                    }
                ]
                
                Generalmaster_Serializer = GeneralMasterserializer(data=GeneralMasterJSON, many=True)
                if not Generalmaster_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Generalmaster_Serializer.errors, 'Data': []})
                Generalmaster_Serializer.save()
                print('General Master created')


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
                    "Company": CompanyID,
                    "EmployeeType": Employee_TypeID,
                    "State": 1,
                    "District": 1,
                    "EmployeeParties": [
                        {"Party":  ""}
                        ]

                }
                
                Employee_Serializer = M_EmployeesSerializer(data=EmployeeJSON)
                if not Employee_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Employee_Serializer.errors, 'Data': []})
                employee_instance = Employee_Serializer.save()
                EmployeeID = employee_instance.id  # Store Employee ID
                print('Employee created')
                

# =============================================-----Party-----=========================================================================================

                PartyJSON = {
                    "Name": "TestParty",
                    "PriceList": 2,
                    "PartyType": PartyTypeID,
                    "Company": CompanyID,
                    "PAN": "AAAAA1234A",
                    "Email": "testparty@gmail.com",
                    "MobileNo": "9874563210",
                    "AlternateContactNo": "9632587410",
                    "Country": 1,
                    "State": 22,
                    "District": 26,
                    "City": 456,
                    "SAPPartyCode": None,
                    "Taluka": 0,
                    "Latitude": "",
                    "Longitude": "",
                    "Cluster": 1,
                    "SubCluster": 1,
                    "GSTIN": "",
                    "isActive": True,
                    "CreatedBy": 2,
                    "UpdatedBy": 2,
                    "IsApprovedParty": False,
                    "PartySubParty": [
                        {
                            "Party": 1,
                            "Distance": 5,
                            "CreatedBy": 2,
                            "UpdatedBy": 2,
                            "Creditlimit": "",
                            "Route": "",
                            "Delete": 0
                        }
                    ],
                    "PartyAddress": [
                        {
                            "Address": "Pune",
                            "FSSAINo": "",
                            "FSSAIExipry": None,
                            "PIN": "411001",
                            "IsDefault": True,
                            "fssaidocument": "",
                            "RowId": 1,
                            "id": "0"
                        }
                    ],
                    "PartyPrefix": [
                        {
                            "Orderprefix": "PO",
                            "Invoiceprefix": "IN",
                            "Grnprefix": "GRN",
                            "Receiptprefix": "RE",
                            "Challanprefix": "",
                            "WorkOrderprefix": "",
                            "MaterialIssueprefix": "",
                            "Demandprefix": "",
                            "IBChallanprefix": "",
                            "IBInwardprefix": "",
                            "PurchaseReturnprefix": "PR",
                            "Creditprefix": "CR",
                            "Debitprefix": "DR"
                        }
                    ]
                }
                
                Party_Serializer = M_PartiesSerializer(data=PartyJSON)
                
                if not Party_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Party_Serializer.errors, 'Data': []})
                party_instance = Party_Serializer.save()
                PartyID = party_instance.id  # Store Party ID
                print('Party created')

#================================----User----================================================================================ 

                UserJSON = {
                    "LoginName": "SuperAdmin19",
                    "password": "1234",
                    "Employee": EmployeeID,
                    "isActive": "1",
                    "AdminPassword": "1234",
                    "isSendOTP": "0",
                    "isLoginUsingMobile": "0",
                    "isLoginUsingEmail": "0",
                    "POSRateType" : 0,
                    
                    "CreatedBy": 1,
                    "UpdatedBy": 1,
                    "UserRole": [
                                {
                                    "Party": PartyID,
                                    "Role": RoleID
                                }
                    ]
                }
                
                User_Serializer = UserRegistrationSerializer(data=UserJSON)
                
                if not User_Serializer.is_valid():
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': User_Serializer.errors, 'Data': []})
                User_Serializer.save()
                print('User created')

#================================----RoleAccessdata----================================================================================ 
     
                
                RoleAccessdata = [
                    {
                        "Role": RoleID,
                        "Company":CompanyID, 
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company":CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company":CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company": CompanyID,
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
                        "Role": RoleID,
                        "Company":CompanyID,
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
                        "Role": RoleID,
                        "Company":CompanyID,
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
                        "Role": RoleID,
                        "Company":CompanyID,
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
