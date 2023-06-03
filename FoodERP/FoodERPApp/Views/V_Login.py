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
                
                # if (RoleID == 1):
                #     Usersdata = M_Users.objects.all()
                # else:                
                #     Usersdata = M_Users.objects.filter(CreatedBy=UserID)    
                Usersdata = M_Users.objects.filter(CreatedBy=UserID) 
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
                            'AdminPassword': a["AdminPassword"],
                            'CreatedBy': a["CreatedBy"],
                            'CreatedOn': a["CreatedOn"],
                            'UpdatedBy': a["UpdatedBy"],
                            'UpdatedOn': a["UpdatedOn"],
                            'Employee': a["Employee"]["id"],
                            'EmployeeName': a["Employee"]["Name"],
                            'CompanyName': a["Employee"]["Company"]["Name"],
                            'UserRole': RoleData,

                        })
                       
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


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
                    # print(Usersdata_Serializer)
                    UserData = list()
                    for a in Usersdata_Serializer:
                        RoleData = list()
                        UserPartiesQuery = MC_UserRoles.objects.raw('''SELECT MC_UserRoles.id,MC_UserRoles.Party_id ,M_Parties.Name PartyName FROM MC_UserRoles left join M_Parties on M_Parties.id= MC_UserRoles.Party_id Where MC_UserRoles.User_id=%s  ''',[id])
                        if not UserPartiesQuery:
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Not Found', 'Data':[] })    
                        else:    
                            SingleGetUserListUserPartiesSerializerData = SingleGetUserListUserPartiesSerializer(UserPartiesQuery,  many=True).data
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':SingleGetUserListUserPartiesSerializerData})  
                            for b in SingleGetUserListUserPartiesSerializerData:
                                PartyID=b['Party_id']
                                
                                if PartyID is None:
                                    PartyRoles = MC_UserRoles.objects.raw('''SELECT MC_UserRoles.id,MC_UserRoles.Role_id ,M_Roles.Name RoleName FROM MC_UserRoles join M_Roles on M_Roles.id= MC_UserRoles.Role_id Where MC_UserRoles.Party_id is null and  MC_UserRoles.User_id=%s ''',([id]))
                                else:    
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ccccccccccc', 'Data':PartyID})  
                                    PartyRoles = MC_UserRoles.objects.raw('''SELECT MC_UserRoles.id,MC_UserRoles.Role_id ,M_Roles.Name RoleName FROM MC_UserRoles join M_Roles on M_Roles.id= MC_UserRoles.Role_id Where MC_UserRoles.Party_id=%s and  MC_UserRoles.User_id=%s ''',([PartyID],[id]))
                               
                                SingleGetUserListUserPartyRoleData = SingleGetUserListUserPartyRoleSerializer(PartyRoles,  many=True).data
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':SingleGetUserListUserPartyRoleData})    
                                PartyRoleData = list()
                                for c in SingleGetUserListUserPartyRoleData:
                                    PartyRoleData.append({
                                        'Role': c['Role_id'],
                                        'RoleName': c['RoleName'], 
                                    })
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyRoleData[0]})    
                                RoleData.append({
                                    # 'Role': b['Role']['id'],
                                    # 'RoleName': b['Role']['Name'],
                                    'Party': b['Party_id'],
                                    'PartyName': b['PartyName'],
                                    'PartyRoles':PartyRoleData

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
                        'AdminPassword': a["AdminPassword"],
                        'CreatedBy': a["CreatedBy"],
                        'CreatedOn': a["CreatedOn"],
                        'UpdatedBy': a["UpdatedBy"],
                        'UpdatedOn': a["UpdatedOn"],
                        'Employee': a["Employee"]["id"],
                        'EmployeeName': a["Employee"]["Name"],
                        'UserRole': RoleData,

                    })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserData[0]})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'User Not available', 'Data': ''})
        except Exception:
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Execution Error', 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Usersdata = M_Users.objects.get(id=id)
                Usersdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Deleted Successfully', 'Data': []})
        except Exception:
            raise JsonResponse(
                {'StatusCode': 200, 'Status': True, 'Message':  'Execution Errors', 'Data': []})

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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Updated Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Usersdata_Serializer.errors, 'Data': []})
        except Exception:
            raise JsonResponse(
                {'StatusCode': 200, 'Status': True, 'Message':  'Execution Error', 'Data': []})


class UserLoginView(RetrieveAPIView):

    permission_classes = ()
    authentication_classes = ()

    serializer_class = UserLoginSerializer

    def post(self, request):
        aa = request.data.get('LoginName')
        LoginName = str(aa)
        findUser = M_Users.objects.raw('''SELECT M_Employees.id id,M_Employees.Name EmployeeName,M_Users.id UserID,M_Users.LoginName  FROM M_Employees join M_Users on M_Employees.id=M_Users.Employee_id
        where (M_Users.isLoginUsingEmail=1 and M_Employees.email = %s) OR (M_Users.isLoginUsingMobile=1 and  M_Employees.Mobile=%s) OR (M_Users.LoginName=%s) ''', ([LoginName], [LoginName], [LoginName]))
        if not findUser:
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Invalid UserName', 'Data': []})
        FindUserSerializer_data = FindUserSerializer(findUser, many=True).data
        a = {
            "LoginName": FindUserSerializer_data[0]['LoginName'],
            "password": request.data.get('password')
        }

        serializer = UserLoginSerializer(data=a)
        
        if serializer.is_valid():
        
            response = {
                'Status': True,
                'StatusCode': status.HTTP_200_OK,
                'Message': 'User logged in  successfully',
                'token': serializer.data['token'],
                'refreshtoken': serializer.data['refreshtoken'],
                'UserID': serializer.data['UserID']
            }
            status_code = status.HTTP_200_OK
            return Response(response, status=status_code)
        else:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Incorrect LoginName and Password ', 'Data': []})


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
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'A user with this LoginName and password is not found', 'Data':[]}) 
                else:
                    user.set_password(newpassword)
                    user.AdminPassword = newpassword
                    user.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Password change successfully', 'Data':[]}) 
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

        


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
                    '''SELECT  a.id,b.Role_id Role,M_Roles.Name AS RoleName,a.Party_id,M_Parties.Name AS PartyName ,a.Employee_id,M_Parties.SAPPartyCode from (SELECT MC_EmployeeParties.id,MC_EmployeeParties.Party_id,'0' RoleID,Employee_id FROM MC_EmployeeParties where Employee_id=%s)a left join (select MC_UserRoles.Party_id,MC_UserRoles.Role_id,Employee_id FROM MC_UserRoles join M_Users on M_Users.id=MC_UserRoles.User_id WHERE M_Users.Employee_id=%s)b on a.Party_id=b.Party_id left join M_Parties on M_Parties.id=a.Party_id Left join M_Roles on M_Roles.id=b.Role_id''', ([id], [id]))
                # print(str(query.query))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                else:
                    M_UserParties_Serializer = M_UserPartiesSerializer(
                        query, many=True).data

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_UserParties_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})

class UserPartiesForLoginPage(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    serializer_class = M_UserPartiesSerializer

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_EmployeeParties.objects.raw(
                    '''SELECT  MC_UserRoles.id,MC_UserRoles.Party_id,MC_UserRoles.Role_id Role,M_Roles.Name AS RoleName,M_Parties.Name AS PartyName ,M_Users.Employee_id,M_Parties.SAPPartyCode,M_PartyType.IsSCM

                     FROM  MC_UserRoles
                     JOIN M_Users on M_Users.id=MC_UserRoles.User_id
                     left JOIN M_Parties on M_Parties.id=MC_UserRoles.Party_id
                     left join M_PartyType on M_Parties.PartyType_id=M_PartyType.id
                     Left JOIN M_Roles on M_Roles.id=MC_UserRoles.Role_id		 
                     WHERE M_Users.Employee_id=%s ''', [id])
                # print(str(query.query))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                else:
                    M_UserParties_Serializer = self.serializer_class(
                        query, many=True).data

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_UserParties_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})



class GetEmployeeViewForUserCreation(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name FROM M_Employees where M_Employees.id 
NOT IN (SELECT Employee_id From M_Users) ''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employees Not available', 'Data': []})
                else:
                    M_Employees_Serializer = EmployeeSerializerForUserCreation(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Employees_Serializer})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})


class GetUserDetailsView(APIView):

    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def post(self, request):
        UserId = request.data['UserId']
        Userdata = M_Users.objects.filter(id=UserId)

        UserSerializer = UserListSerializerforgetdata(Userdata, many=True).data

        Employee = M_Employees.objects.filter(id=UserSerializer[0]['Employee'])
        EmployeeSerializer = M_EmployeesSerializerforgetdata(Employee, many=True).data

        Company = C_Companies.objects.filter(id=EmployeeSerializer[0]['Company'])
        CompanySerializer = C_CompanySerializer(Company, many=True).data

        request.session['UserID'] = UserId
        request.session['UserName'] = UserSerializer[0]["LoginName"]
        request.session['EmployeeID'] = UserSerializer[0]["Employee"]
        request.session['CompanyID'] = EmployeeSerializer[0]["Company"]
        request.session['IsSCMCompany'] = CompanySerializer[0]["IsSCM"]
        request.session['CompanyGroup'] = CompanySerializer[0]["CompanyGroup"]
        print(request.session.get('UserName'),request.session.get('IsSCMCompany'),request.session.get('CompanyGroup'))

        a = list()
        a.append({
            "UserID": UserId,
            "UserName":UserSerializer[0]["LoginName"],
            "EmployeeID": UserSerializer[0]["Employee"],
            "CompanyID": EmployeeSerializer[0]["Company"],
            "CompanyName": CompanySerializer[0]["Name"],
            "IsSCMCompany": CompanySerializer[0]["IsSCM"],
            "CompanyGroup": CompanySerializer[0]["CompanyGroup"]

        })

        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': a[0]})


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
