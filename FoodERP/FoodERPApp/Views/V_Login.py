import re
from django.http import JsonResponse

from ..Serializer.S_Companies import C_CompanySerializer2

from ..Serializer.S_Employees import *
from ..models import *
from ..Serializer.S_Login import *
# from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

from django.shortcuts import render
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.parsers import JSONParser


from rest_framework import status
from rest_framework.response import Response
from django.db import connection, transaction

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
            status_code = status.HTTP_201_CREATED
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
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                PageListData = list()
                Usersdata = M_Users.objects.all()
                if Usersdata.exists():
                    Usersdata_Serializer = UserListSerializer(
                        Usersdata, many=True).data
                    UserData = list()
                    for a in Usersdata_Serializer:
                        # RoleData = list()
                        # for b in a["UserRole"]:
                        #     RoleData.append({
                        #         'Role': b['Role']['id'],
                        #         'Name': b['Role']['Name'],

                        #     })
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
                            # 'UserRole': RoleData,

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data': []})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})


class UserListViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

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
                        UserPartiesQuery = MC_UserRoles.objects.raw('''SELECT mc_userroles.id,mc_userroles.Party_id ,m_parties.Name PartyName FROM mc_userroles join m_parties on m_parties.id= mc_userroles.Party_id Where mc_userroles.User_id=%s group by Party_id ''',[id])
                        if not UserPartiesQuery:
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Not Found', 'Data':[] })    
                        else:    
                            SingleGetUserListUserPartiesSerializerData = SingleGetUserListUserPartiesSerializer(UserPartiesQuery,  many=True).data
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':SingleGetUserListUserPartiesSerializerData})  
                            for b in SingleGetUserListUserPartiesSerializerData:
                                PartyID=b['Party_id']
                                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':PartyID})  
                                PartyRoles = MC_UserRoles.objects.raw('''SELECT mc_userroles.id,mc_userroles.Role_id ,m_roles.Name RoleName FROM mc_userroles join m_roles on m_roles.id= mc_userroles.Role_id Where mc_userroles.Party_id=%s and  mc_userroles.User_id=%s ''',([PartyID],[id]))
                                
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
        findUser = M_Users.objects.raw('''SELECT m_employees.id id,m_employees.Name EmployeeName,m_users.id UserID,m_users.LoginName  FROM m_employees join m_users on m_employees.id=m_users.Employee_id
        where (m_users.isLoginUsingEmail=1 and m_employees.email = %s) OR (m_users.isLoginUsingMobile=1 and  m_employees.Mobile=%s) OR (m_users.LoginName=%s) ''', ([LoginName], [LoginName], [LoginName]))
        if not findUser:
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Invalid UserName', 'Data': []})
        FindUserSerializer_data = FindUserSerializer(findUser, many=True).data
        a = {
            "LoginName": FindUserSerializer_data[0]['LoginName'],
            "password": request.data.get('password')
        }

        serializer = self.serializer_class(data=a)
        serializer.is_valid(raise_exception=True)

        response = {
            'Status': 'True',
            'StatusCode': status.HTTP_200_OK,
            'Message': 'User logged in  successfully',
            'token': serializer.data['token'],
            'UserID': serializer.data['UserID']


        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class ChangePasswordView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = {
            'Status': 'True',
            'StatusCode': status.HTTP_200_OK,
            'Message': 'Password change successfully',
            # 'token': serializer.data,
        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)


class RegenrateToken(APIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request):
        OldToken = request.data['OldToken']
        Other_Fields = request.data['Other_Fields']
        Decode = jwt.decode(OldToken, None, None)
        payload_data = {
            'Decode': Decode,
            'Other_Fields': Other_Fields
        }
        my_secret = 'my_super_secret'
        return Response({jwt.encode(payload=payload_data, key=my_secret)})


class UserPartiesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_EmployeeParties.objects.raw(
                    '''SELECT  a.id,b.Role_id Role,m_roles.Name AS RoleName,a.Party_id,m_parties.Name AS PartyName ,a.Employee_id from (SELECT mc_employeeparties.id,mc_employeeparties.Party_id,'0' RoleID,Employee_id FROM mc_employeeparties where Employee_id=%s)a left join (select mc_userroles.Party_id,mc_userroles.Role_id,Employee_id FROM mc_userroles join m_users on m_users.id=mc_userroles.User_id WHERE m_users.Employee_id=%s)b on a.Party_id=b.Party_id left join m_parties on m_parties.id=a.Party_id Left join m_roles on m_roles.id=b.Role_id''', ([id], [id]))
                # print(str(query.query))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                else:
                    M_UserParties_Serializer = M_UserPartiesSerializer(
                        query, many=True).data

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_UserParties_Serializer})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})

class UserPartiesForLoginPage(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    serializer_class = M_UserPartiesSerializer

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_EmployeeParties.objects.raw(
                    '''SELECT  mc_userroles.id,mc_userroles.Role_id Role,m_roles.Name AS RoleName,mc_userroles.Party_id,m_parties.Name AS PartyName ,m_users.Employee_id

                     FROM  mc_userroles
                     JOIN m_users on m_users.id=mc_userroles.User_id
                     left JOIN m_parties on m_parties.id=mc_userroles.Party_id
                     Left JOIN m_roles on m_roles.id=mc_userroles.Role_id		 
                     WHERE m_users.Employee_id=%s group by mc_userroles.Party_id''', [id])
                # print(str(query.query))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Parties Not available', 'Data': []})
                else:
                    M_UserParties_Serializer = self.serializer_class(
                        query, many=True).data

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_UserParties_Serializer})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})



class GetEmployeeViewForUserCreation(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_Employees.objects.raw('''SELECT M_Employees.id,M_Employees.Name FROM M_Employees where M_Employees.id 
NOT IN (SELECT Employee_id From m_users) ''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Employees Not available', 'Data': []})
                else:
                    M_Employees_Serializer = EmployeeSerializerForUserCreation(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Employees_Serializer})
        except Exception:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Exception Found', 'Data': []})


class GerUserDetialsView(APIView):

    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    def post(self, request):
        UserId = request.data['UserId']
        Userdata = M_Users.objects.filter(id=UserId)

        EmployeeID = UserListSerializerforgetdata(Userdata, many=True).data

        company = M_Employees.objects.filter(id=EmployeeID[0]['Employee'])
        CompanyID = M_EmployeesSerializerforgetdata(company, many=True).data

        company_Group = C_Companies.objects.filter(id=CompanyID[0]['Company'])
        CompanyGroupID = C_CompanySerializer2(company_Group, many=True).data

        a = list()
        a.append({
            "UserID": UserId,
            "EmployeeID": EmployeeID[0]["Employee"],
            "CompanyID": CompanyID[0]["Company"],
            "CompanyGroup": CompanyGroupID[0]["CompanyGroup"]

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
