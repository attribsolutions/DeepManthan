from django.http import JsonResponse
from ..Serializer.S_Companies import C_CompanySerializer
from ..Serializer.S_Employees import *
from ..models import *
from ..Serializer.S_Login import *
from django.db import IntegrityError, transaction
# from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from rest_framework.views import APIView
import jwt
from .V_CommFunction import create_transaction_logNew
from django.db.models import *


# Create your views here.


class UserRegistrationView(CreateAPIView):

    permission_classes = ()
    serializer_class = UserRegistrationSerializer
    authentication_class = ()

    def post(self, request):
        # try:
        #     with transaction.atomic():

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            status_code = 200
            response = {
                'StatusCode': status_code,
                'Status': True,
                'Message': 'User registered  successfully',
                'Data': []
            }

            return Response(response, status=status_code)
        else:
            # transaction.set_rollback(True)
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': serializer.errors, 'Data': []})
        # except Exception as e:
        #     raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class UserListView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID'] 
                PartyID = Logindata.get('PartyID', None)       
                
                if (RoleID == 1):
                    employees = M_Employees.objects.filter(Company_id=CompanyID).values_list('id',flat=True)                
                    Usersdata = M_Users.objects.filter(Employee__in=employees) 
                else:                
                     
                    Usersdata = M_Users.objects.filter(CreatedBy=UserID) 
                    SettingQuery=M_Settings.objects.filter(id=47).values("DefaultValue")
                    RoleID_List=str(SettingQuery[0]['DefaultValue'])                    
                    RoleID_list = [int(x) for x in RoleID_List.split(",")]
                    # print(RoleID_list)
                    if RoleID in RoleID_list:                    
                        Clause= {'Employee__CreatedBy': UserID}
                    else:
                        Clause= {}
                    employees = M_Employees.objects.filter(Company_id=CompanyID).values_list('id',flat=True)                
                    Usersdata = M_Users.objects.filter(Employee__in=employees,**Clause)
                     
                if PartyID:
                    Usersdata = Usersdata.filter(UserRole__Party__id=PartyID)              
                if Usersdata.exists():
                    Usersdata_Serializer = UserListSerializer(Usersdata, many=True).data
                    UserData = list()
                       
                    for a in Usersdata_Serializer:
                        RoleData = list()
                        for b in a["UserRole"]:
                            RoleData.append({
                                'Party': b['Party']['id'],
                                'PartyName': b['Party']['Name'],
                                'Role': b['Role']['id'],
                                'RoleName': b['Role']['Name'],

                            })
                        
                        UserData.append({
                            'id': a["id"],
                            'LoginName': a["LoginName"],
                            'password': a["password"],
                            'last_login': a["last_login"],
                            'isActive': a["isActive"],
                            'isSendOTP': a["isSendOTP"],
                            'isLoginUsingMobile': a["isLoginUsingMobile"],
                            'isLoginUsingEmail': a["isLoginUsingEmail"],
                            'IsLoginPermissions' : a['IsLoginPermissions'],
                            'AdminPassword': a["AdminPassword"],
                            'CreatedBy': a["CreatedBy"],
                            'CreatedOn': a["CreatedOn"],
                            'UpdatedBy': a["UpdatedBy"],
                            'UpdatedOn': a["UpdatedOn"],
                            'POSRateType' : a["POSRateType" ],
                            'Employee': a["Employee"]["id"],
                            'EmployeeName': a["Employee"]["Name"],
                            'CompanyName': a["Employee"]["Company"]["Name"],
                            'UserRole': RoleData,

                        })
                    log_entry = create_transaction_logNew(request, Logindata,0,'RoleID:'+str(RoleID)+','+'CompanyID:'+str(CompanyID),136,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserData})
                log_entry = create_transaction_logNew(request, Logindata,0,"User List Not available",136,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'UserList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class UserListViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Usersdata = M_Users.objects.filter(id=id)
                if Usersdata.exists():
                    Usersdata_Serializer = UserListSerializer(Usersdata, many=True).data
                    CustomPrint(Usersdata_Serializer)
                    UserData = list()
                    for a in Usersdata_Serializer:
                        RoleData = list()
                        UserPartiesQuery = MC_UserRoles.objects.raw('''SELECT MC_UserRoles.id,MC_UserRoles.Party_id ,M_Parties.Name PartyName FROM MC_UserRoles left join M_Parties on M_Parties.id= MC_UserRoles.Party_id Where MC_UserRoles.User_id=%s  ''',[id])
                        # CustomPrint(UserPartiesQuery)
                        if not UserPartiesQuery:
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Not Found', 'Data':[] })    
                        else:    
                            # SingleGetUserListUserPartiesSerializerData = SingleGetUserListUserPartiesSerializer(UserPartiesQuery,  many=True).data
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':SingleGetUserListUserPartiesSerializerData})  
                            # for b in SingleGetUserListUserPartiesSerializerData:
                                # PartyID=b['Party_id']
                                
                                # if PartyID is None:
                                #     PartyRoles = MC_UserRoles.objects.raw('''SELECT MC_UserRoles.id,MC_UserRoles.Role_id ,M_Roles.Name RoleName FROM MC_UserRoles join M_Roles on M_Roles.id= MC_UserRoles.Role_id Where MC_UserRoles.Party_id is null and  MC_UserRoles.User_id=%s ''',([id]))
                                # else:    
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ccccccccccc', 'Data':PartyID})  
                                # PartyRoles = MC_UserRoles.objects.raw('''SELECT MC_UserRoles.id,MC_UserRoles.Role_id ,M_Roles.Name RoleName FROM MC_UserRoles join M_Roles on M_Roles.id= MC_UserRoles.Role_id Where MC_UserRoles.Party_id=%s and  MC_UserRoles.User_id=%s ''',([PartyID],[id]))
                               
                                # SingleGetUserListUserPartyRoleData = SingleGetUserListUserPartyRoleSerializer(PartyRoles,  many=True).data
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':SingleGetUserListUserPartyRoleData})    
                                # PartyRoleData = list()
                                # for c in SingleGetUserListUserPartyRoleData:
                                #     PartyRoleData.append({
                                #         'Role': c['Role_id'],
                                #         'RoleName': c['RoleName']
                                #     })
                                # # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyRoleData[0]})    
                                # RoleData.append({
                                #     # 'Role': b['Role']['id'],
                                #     # 'RoleName': b['Role']['Name'],
                                #     'Party': b['Party_id'],
                                #     'PartyName': b['PartyName'],
                                #     'PartyRoles':PartyRoleData
                                # })
                               

                                    PartyRoleData = {}
                                    for b in a["UserRole"]:
                                        party_id = b['Party']['id'] if b['Party']['id'] is not None else ''
                                        party_name = b['Party']['Name'] if b['Party']['id'] is not None else ''
                                        role_id = b['Role']['id']
                                        role_name = b['Role']['Name']

                                        
                                        if party_id in PartyRoleData:
                                            PartyRoleData[party_id]['PartyRoles'].append({
                                                'Role': role_id,
                                                'RoleName': role_name
                                            })
                                        else:
                                            
                                            PartyRoleData[party_id] = {
                                                'Party': party_id,
                                                'PartyName': party_name,
                                                'PartyRoles': [{
                                                    'Role': role_id,
                                                    'RoleName': role_name
                                                }]
                                            }                                    
                                    RoleData = list(PartyRoleData.values())
                            
                    UserData.append({
                        'id': a["id"],
                        'LoginName': a["LoginName"],
                        'password': a["password"],
                        'last_login': a["last_login"],
                        'isActive': a["isActive"],
                        'isSendOTP': a["isSendOTP"],
                        'isLoginUsingMobile': a["isLoginUsingMobile"],
                        'isLoginUsingEmail': a["isLoginUsingEmail"],
                        'IsLoginPermissions' : a['IsLoginPermissions'],
                        'AdminPassword': a["AdminPassword"],
                        'CreatedBy': a["CreatedBy"],
                        'CreatedOn': a["CreatedOn"],
                        'UpdatedBy': a["UpdatedBy"],
                        'UpdatedOn': a["UpdatedOn"],
                        'POSRateType': a['POSRateType'],
                        'Employee': a["Employee"]["id"],
                        'EmployeeName': a["Employee"]["Name"],
                        'EmployeeMobile': a["Employee"]["Mobile"],
                        'EmployeeEmail': a["Employee"]["email"],
                        'UserRole': RoleData,

                    })
                    log_entry = create_transaction_logNew(request, Usersdata_Serializer,0,"Single User",137,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserData[0]})
                log_entry = create_transaction_logNew(request, Usersdata_Serializer,0,"User Not available",137,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'User Not available', 'Data': ''})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'User Details:'+"Execution Error",135,0) 
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': e, 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Usersdata = M_Users.objects.get(id=id)
                Usersdata.delete()
                log_entry = create_transaction_logNew(request, {"UserID":id},0,'UserID:'+str(id),138,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Deleted Successfully', 'Data': []})
        except Exception:
            log_entry = create_transaction_logNew(request, 0,0,'UserDelete:'+"Execution Errors",135,0)
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Execution Errors', 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Usersdata = JSONParser().parse(request)
                UsersdataByID = M_Users.objects.get(id=id)
                Usersdata_Serializer = UserRegistrationSerializer(
                    UsersdataByID, data=Usersdata)
                if Usersdata_Serializer.is_valid():
                    Usersdata_Serializer.save()
                    log_entry = create_transaction_logNew(request, Usersdata,0,"User Updated Successfully",139,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, Usersdata,0,'UserEdit:'+str(Usersdata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Usersdata_Serializer.errors, 'Data': []})
        except Exception:
            log_entry = create_transaction_logNew(request, 0,0,'UserEdit:'+"Execution Errors",135,0)
            raise JsonResponse(
                {'StatusCode': 200, 'Status': True, 'Message':  'Execution Error', 'Data': []})


class UserLoginView(RetrieveAPIView):

    permission_classes = ()
    authentication_classes = ()

    # serializer_class = UserLoginSerializer

    def post(self, request):
        aa = request.data.get('LoginName')
        LoginName = str(aa)
        # findUser = M_Users.objects.raw('''SELECT M_Employees.id id,M_Employees.Name EmployeeName,M_Users.id UserID,M_Users.LoginName  FROM M_Employees join M_Users on M_Employees.id=M_Users.Employee_id
        # where (M_Users.isLoginUsingEmail=1 and M_Employees.email = %s) OR (M_Users.isLoginUsingMobile=1 and  M_Employees.Mobile=%s) OR (M_Users.LoginName=%s) ''', ([LoginName], [LoginName], [LoginName]))
        find_user = M_Users.objects.filter(
                    Q(isLoginUsingEmail=1, Employee__email=LoginName) |
                    Q(isLoginUsingMobile=1, Employee__Mobile=LoginName) |
                    Q(LoginName=LoginName)).values( 'id', 'LoginName','IsLoginPermissions')
        
        # employee = find_user.Employee
        if find_user:
            login_name=find_user[0]['LoginName']
            password=request.data.get('password')
            user = authenticate(LoginName=login_name, password=password)
            if user:
                # If user is authenticated, generate JWT token
                update_last_login(None, user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    "Status": True,
                    "StatusCode": 200,
                    "Message": "User logged in  successfully",
                    'refreshtoken': str(refresh),
                    'token': str(refresh.access_token),
                    "UserID": find_user[0]['id'],
                    "IsLoginPermissions": find_user[0]['IsLoginPermissions']  
                }, status=status.HTTP_200_OK)
                
            else:
                return Response({'StatusCode': 401, 'Status': True, 'Message': 'Invalid credentials', 'Data': []}, status=status.HTTP_401_UNAUTHORIZED)

        else:
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Invalid UserName', 'Data': []}, status=status.HTTP_401_UNAUTHORIZED)

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        # if not find_user:
            
        #     return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Invalid UserName', 'Data': []})
        
        # # FindUserSerializer_data = FindUserSerializer(find_user, many=True).data
        
        # a = {
        #     "LoginName": find_user[0]['LoginName'],
        #     "password": request.data.get('password')
        # }
        
        # serializer = UserLoginSerializer(data=a)
        
        # if serializer.is_valid():
        
        #     response = {
        #         'Status': True,
        #         'StatusCode': status.HTTP_200_OK,
        #         'Message': 'User logged in  successfully',
        #         'token': serializer.data['token'],
        #         'refreshtoken': serializer.data['refreshtoken'],
        #         'UserID': serializer.data['UserID']
        #     }
            
        #     status_code = status.HTTP_200_OK
        #     log_entry = create_transaction_logNew(request,serializer.data,0,"Login Successfully",140,0)
        #     return Response(response, status=status_code)
        # else:
         
        #     # log_entry = create_transaction_logNew(request, serializer.data,0,"Incorrect LoginName and Password",141,0)
        #     # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Incorrect LoginName and Password ', 'Data': []})
        #     return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': serializer.errors['non_field_errors'][0], 'Data': []})


class ChangePasswordView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
  
    def post(self, request):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                LoginName = Logindata['LoginName']   
                password=  Logindata['password']  
                newpassword=Logindata['newpassword']
                
                user = authenticate(LoginName=LoginName, password=password)
                if user is None:
                    log_entry = create_transaction_logNew(request,Logindata,0,"A user with this LoginName and password is not found",142,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'A user with this LoginName and password is not found', 'Data':[]}) 
                else:
                    user.set_password(newpassword)
                    user.AdminPassword = newpassword
                    user.save()

                    log_entry = create_transaction_logNew(request,Logindata,0,"Password change successfully",143,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Password change successfully', 'Data':[]}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'PasswordChangemethod:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})

# class RegenrateToken(APIView):

#     permission_classes = (IsAuthenticated,)
#     # authentication__Class = JSONWebTokenAuthentication

#     def post(self, request):
#         OldToken = request.data['OldToken']
#         Other_Fields = request.data['Other_Fields']
#         Decode = jwt.decode(OldToken, None, None)
#         payload_data = {
#             'Decode': Decode,
#             'Other_Fields': Other_Fields
#         }
#         my_secret = 'my_super_secret'
#         return Response({jwt.encode(payload=payload_data, key=my_secret)})


class UserPartiesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_EmployeeParties.objects.raw(
                    '''SELECT  a.id,b.Role_id Role,M_Roles.Name AS RoleName,a.Party_id,M_Parties.Name AS PartyName ,a.Employee_id,M_Parties.SAPPartyCode,M_PartyType.IsSCM as IsSCMPartyType,M_Parties.GSTIN from (SELECT MC_EmployeeParties.id,MC_EmployeeParties.Party_id,'0' RoleID,Employee_id FROM MC_EmployeeParties where Employee_id=%s)a left join (select MC_UserRoles.Party_id,MC_UserRoles.Role_id,Employee_id FROM MC_UserRoles join M_Users on M_Users.id=MC_UserRoles.User_id WHERE M_Users.Employee_id=%s)b on a.Party_id=b.Party_id left join M_Parties on M_Parties.id=a.Party_id Left join M_Roles on M_Roles.id=b.Role_id left join M_PartyType on M_Parties.PartyType_id=M_PartyType.id''', ([id], [id]))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                else:
                    UserSerializer = MultipeRoleForOneUser(query, many=True).data                                               
                    User_List = []
                    party_roles = {}  
                    for a in UserSerializer:
                        party_id = a["Party_id"]                       
                       
                        if party_id not in party_roles:
                            party_roles[party_id] = {                               
                                "PartyID": party_id,
                                "Partyname": a["PartyName"],
                                "RoleDetails": []                                
                            }
                        
                        if a["Role"]:
                            party_roles[party_id]["RoleDetails"].append({
                                "RoleName": a["RoleName"],
                                "Role": a["Role"]
                            })
                    
                    User_List = list(party_roles.values())           

                log_entry = create_transaction_logNew(request,{'UserID':id},0,"UserPartiesForUserMaster",144,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': User_List})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'UserPartiesForUserMaster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})

class UserPartiesForLoginPage(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    # serializer_class = M_UserPartiesSerializer

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                # query = MC_EmployeeParties.objects.raw(
                #     '''SELECT  MC_UserRoles.id,MC_UserRoles.Party_id,MC_UserRoles.Role_id Role,M_Roles.Name AS RoleName,M_Parties.Name AS PartyName ,M_Users.Employee_id,M_Parties.SAPPartyCode,M_PartyType.IsSCM as IsSCMPartyType,M_Parties.GSTIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_PartyType.id PartyTypeID,M_PartyType.Name PartyType,M_Parties.UploadSalesDatafromExcelParty

                #      FROM  MC_UserRoles
                #      JOIN M_Users on M_Users.id=MC_UserRoles.User_id
                #      left JOIN M_Parties on M_Parties.id=MC_UserRoles.Party_id
                #      left join MC_PartyAddress on MC_PartyAddress.Party_id=M_Parties.id and MC_PartyAddress.IsDefault=1
                #      left join M_PartyType on M_Parties.PartyType_id=M_PartyType.id
                #      Left JOIN M_Roles on M_Roles.id=MC_UserRoles.Role_id		 
                #      WHERE M_Users.Employee_id=%s ''', [id])

                query = (
                    MC_UserRoles.objects.select_related('User', 'Party', 'Role')
                    .filter(User__Employee_id=id,Party__PartyAddress__IsDefault=1,Party__PartyDetailsParty__Group_id__isnull=True)
                    .annotate(
                        RoleName=F('Role__Name'),
                        PartyName=F('Party__Name'),
                        PartyAddress=F('Party__PartyAddress__Address'),
                        IsSCMPartyType=F('Party__PartyType__IsSCM'),
                        IsFranchises=F('Party__PartyType__IsFranchises'),
                        GSTIN=F('Party__GSTIN'),
                        FSSAINo=F('Party__PartyAddress__FSSAINo'),
                        FSSAIExpiry=F('Party__PartyAddress__FSSAIExipry'),
                        PartyTypeID=F('Party__PartyType_id'),
                        PartyType=F('Party__PartyType__Name'),
                        Country_id=F('Party__PartyType__Country__id'),
                        CurrencySymbol=F('Party__PartyType__Country__CurrencySymbol'), 
                        Country=F('Party__PartyType__Country__Country'),
                        Weight=F('Party__PartyType__Country__Weight'), 
                        UploadSalesDatafromExcelParty=F('Party__UploadSalesDatafromExcelParty'),
                        ClusterName=F('Party__PartyDetailsParty__Cluster__Name'),
                        SubClusterName=F('Party__PartyDetailsParty__SubCluster__Name'),
                        MobileNo=F('Party__MobileNo'),
                        AlternateContactNo=F('Party__AlternateContactNo')
                        # IsDefaultPartyAddress=F('Party__PartyAddress__IsDefault')      
                    ).annotate(
                        IsSCMPartyTypeInt=Case(When(IsSCMPartyType=True, then=Value(1)),default=Value(0),output_field=IntegerField()),
                        IsFranchisesInt=Case(When(IsFranchises=True, then=Value(1)),default=Value(0),output_field=IntegerField()),
                        UploadSalesDatafromExcelPartyInt=Case( When(UploadSalesDatafromExcelParty=True, then=Value(1)), default=Value(0), output_field=IntegerField() ) 
                    )
                    .values(
                        'id', 'Party_id', 'Role_id', 'RoleName', 'PartyName','PartyAddress', 'User__Employee_id',
                        'Party__SAPPartyCode', 'IsSCMPartyTypeInt','IsFranchisesInt', 'GSTIN', 'FSSAINo', 'FSSAIExpiry',
                        'PartyTypeID', 'PartyType','Country_id','CurrencySymbol','Country','Weight', 'UploadSalesDatafromExcelPartyInt','Party__PriceList_id',
                        'ClusterName', 'SubClusterName','MobileNo', 'AlternateContactNo'
                    )
                    # .filter(IsDefaultPartyAddress=True)
                    
                )    
                # UserID = request.user.id
                # print(str(query.query))
                if not query:
                    log_entry = create_transaction_logNew(request,0,0,"Parties Not available",145,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                else:
                    # M_UserParties_Serializer = self.serializer_class(
                    #     query, many=True).data
                    UserPartiesData = list()
                    for item in query:
                        UserPartiesData.append({
                            "id" : item['id'],
                            "Role" : item['Role_id'],
                            "RoleName" : item['RoleName'],
                            "Party_id" :item['Party_id'],
                            "PartyName" : item['PartyName'],
                            "PartyAddress": item['PartyAddress'], 
                            "Employee_id" : id,
                            "SAPPartyCode" :item['Party__SAPPartyCode'],
                            "IsSCMPartyType" :item['IsSCMPartyTypeInt'],
                            "IsFranchises": item['IsFranchisesInt'],
                            "GSTIN":item['GSTIN'],
                            "FSSAINo": item['FSSAINo'],
                            "FSSAIExipry" :item['FSSAIExpiry'],
                            "PartyTypeID":item['PartyTypeID'],
                            "PartyType":item['PartyType'],
                            "Country_id":item['Country_id'],
                            "CurrencySymbol":item['CurrencySymbol'],
                            "Country":item['Country'],
                            "Weight":item['Weight'],
                            "UploadSalesDatafromExcelParty":item['UploadSalesDatafromExcelPartyInt'],
                            "PriceList_id":item['Party__PriceList_id'],
                            "ClusterName": item['ClusterName'],
                            "SubClusterName": item['SubClusterName'],
                            "MobileNo": item['MobileNo'],
                            "AlternateContactNo": item['AlternateContactNo']
                        }) 
                    log_entry = create_transaction_logNew(request,UserPartiesData,0 ,"PartyDropdownforloginpage",145,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserPartiesData})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0 ,'PartyDropdownforloginpage:'+str(e),34,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})



class GetEmployeeViewForUserCreation(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name, M_Employees.Mobile as EmployeeMobile, M_Employees.email as EmployeeEmail   FROM M_Employees where M_Employees.id 
NOT IN (SELECT Employee_id From M_Users) ''')
                if not query:
                    log_entry = create_transaction_logNew(request,{"UserID":id},0 ,"Employees Not available",146,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employees Not available', 'Data': []})
                else:
                    M_Employees_Serializer = EmployeeSerializerForUserCreation(query, many=True).data
                    log_entry = create_transaction_logNew(request,{"UserID":id},0 ,"GetEmployeeForUserCreation",146,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Employees_Serializer})
        except Exception:
            log_entry = create_transaction_logNew(request,0,0 ,'GetEmployeeForUserCreation:'+'Exception',33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})


class GetUserDetailsView(APIView):
    # print('aaaaaaaaaaaaaaaaaa')
    permission_classes = (IsAuthenticated,)
    # print('bbbbbbbbbbbbbbbbbbb')
    # authentication__Class = JSONWebTokenAuthentication
   
    def post(self, request):
        try:
            with transaction.atomic():
        
            # auth_header = request.META.get('HTTP_AUTHORIZATION')
            # if auth_header:
                            
            #     # Parsing the authorization header
            #     auth_type, auth_string = auth_header.split(' ', 1)
            #     print(auth_type,auth_string)
                # print(request.headers)
                UserId = request.data['UserId']
                
                '''New code Date 26/07/2023'''
                
                # user = M_Users.objects.select_related(M_Employees).prefetch_related.values('Employee', 'LoginName').get(id=UserId)
                
                # employee = M_Employees.objects.values('Company','Name').get(id=user['Employee'])
                # company = C_Companies.objects.values ('Name','IsSCM','CompanyGroup').get(id=employee['Company'])
                
                # user = M_Users.objects.select_related('Employee__Company').get(id=UserId)
                # user = M_Users.objects.select_related('Employee').get(id=UserId)
                user = M_Users.objects.select_related('Employee__Company').get(id=UserId)
                employee = user.Employee
                company = employee.Company
                companygroup = company.CompanyGroup
                  
                # Get PartyName
                PartyData=M_Users.objects.raw(f'''select m.id,m.LoginName,p.id,p.Name as PartyName,p.AlternateContactNo
                                                From M_Users as m
                                                LEFT JOIN MC_EmployeeParties as ep on m.Employee_id=ep.Employee_id
                                                LEFT JOIN M_Parties as p on ep.Party_id=p.id
                                                where m.id={UserId}''')
                #End
                  
                a = list()
                
                if PartyData:
                    for p in PartyData:
                        
                        a.append({
                            "UserID": UserId,
                            "UserName":user.LoginName,
                            "EmployeeID": employee.id,
                            "EmployeeName": employee.Name,
                            "EmpMobileNumber": employee.Mobile,
                            "CompanyID": company.id,
                            "CompanyName": company.Name,
                            "IsSCMCompany": company.IsSCM,
                            "CompanyGroup": companygroup.id,
                            "AlternateContactNo":p.AlternateContactNo,
                        })
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': a[0]})
        except Exception as e:
            
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]}) 

# Registration Input json
# {

#   "email": "ram@gmail.com",
#   "LoginName": "Pradnya",
#   "password": "123456",
#   "Employee": "1",
#   "isActive": "1",
#   "AdminPassword": "1234",
#   "isSendOTP": "1",
#   "CreatedBy": 1,
#   "UpdatedBy": 1,
#   "UserRole": [
#     {
#       "Role": 1
#     },
#     {

#       "Role": 1
#     }
#   ]
# }

# Login Input JSON
# {
# "LoginName": "LoginName11",
# "password": "1234"
# }
