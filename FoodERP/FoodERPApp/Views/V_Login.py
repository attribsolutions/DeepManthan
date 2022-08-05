from django.http import JsonResponse
from ..models import *
from ..Serializer.S_Login import   *
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
                        'Data':[]
                    }

                    return Response(response, status=status_code)
            else:
                    # transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': serializer.errors, 'Data' : []})
        # except Exception as e:
        #     raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
   
class UserListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                PageListData=list()
                Usersdata = M_Users.objects.all()
                if Usersdata.exists():
                        Usersdata_Serializer = UserListSerializer(Usersdata, many=True).data
                        UserData=list()
                        for a in Usersdata_Serializer:
                            RoleData=list()
                            for b in a["UserRole"]:
                                    RoleData.append({
                                        'Role': b['Role']['id'],
                                        'Name': b['Role']['Name'],
                                        
                                    })
                            UserData.append({ 
                                'id': a["id"],
                                'LoginName': a["LoginName"],
                                'password': a["password"],
                                'last_login': a["last_login"],
                                'isActive': a["isActive"],
                                'isSendOTP': a["isSendOTP"],
                                'isLoginUsingMobile' : a["isLoginUsingMobile"],
                                'isLoginUsingEmail' : a["isLoginUsingEmail"],
                                'AdminPassword': a["AdminPassword"],
                                'CreatedBy': a["CreatedBy"],
                                'CreatedOn': a["CreatedOn"],
                                'UpdatedBy': a["UpdatedBy"],
                                'UpdatedOn': a["UpdatedOn"],
                                'Employee': a["Employee"]["id"],
                                'EmployeeName': a["Employee"]["Name"],
                                'UserRole': RoleData,

                            })
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': UserData})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Records Not available', 'Data':[] })                      
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data':[] })                      
        
        

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
                    UserData=list()
                    for a in Usersdata_Serializer:
                       RoleData=list()
                       for b in a["UserRole"]:
                            RoleData.append({
                                'Role': b['Role']['id'],
                                'Name': b['Role']['Name'],
                                
                            })
                    UserData.append({ 
                        'id': a["id"],
                        'LoginName': a["LoginName"],
                        'password': a["password"],
                        'last_login': a["last_login"],
                        'isActive': a["isActive"],
                        'isSendOTP': a["isSendOTP"],
                        'isLoginUsingMobile' : a["isLoginUsingMobile"],
                        'isLoginUsingEmail' : a["isLoginUsingEmail"],
                        'AdminPassword': a["AdminPassword"],
                        'CreatedBy': a["CreatedBy"],
                        'CreatedOn': a["CreatedOn"],
                        'UpdatedBy': a["UpdatedBy"],
                        'UpdatedOn': a["UpdatedOn"],
                        'Employee': a["Employee"]["id"],
                        'EmployeeName': a["Employee"]["Name"],
                        'UserRole': RoleData,

                    })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': UserData[0]})               
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'User Not available', 'Data':'' })                     
        except Exception :
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Execution Error', 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Usersdata = M_Users.objects.get(id=id)
                Usersdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Deleted Successfully', 'Data':[]})
        except Exception :
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Execution Errors', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Usersdata = JSONParser().parse(request)
                UsersdataByID = M_Users.objects.get(id=id)
                Usersdata_Serializer = UserRegistrationSerializer(UsersdataByID, data=Usersdata)
                if Usersdata_Serializer.is_valid():
                    Usersdata_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Usersdata_Serializer.errors, 'Data':[]})
        except Exception :
            raise JsonResponse({'StatusCode': 200, 'Status': True, 'Message':  'Execution Error', 'Data':[]})
                  

class UserLoginView(RetrieveAPIView):
    
    permission_classes = ()
    authentication_classes = ()

    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        LoginName = serializer.data['LoginName']
        EmployeeID= serializer.data['EmployeeID']
        GETLoginName =M_Employees.objects.get(id=EmployeeID)
        EmployeesSerializer_data=M_employeesSerializer(GETLoginName).data
        CompanyGroupID = C_CompanyGroups.objects.get(id=EmployeeID)
        CompanyGroupSerializer_data = C_CompanyGroupSerializer(CompanyGroupID).data	
         	        
         
        def extendtoken():
            payload_data =  {
                "LoginName": LoginName,
                "EmployeeID": EmployeeID,
                "EmployeeNfame": EmployeesSerializer_data['Name'],
                'CompanyGroupID' : CompanyGroupSerializer_data['id']
            }
            my_secret = 'my_super_secret'
            return{jwt.encode(payload=payload_data, key=my_secret)}
             

         
        response = {
            'Status': 'True',
            'StatusCode': status.HTTP_200_OK,
            'Message': 'User logged in  successfully',
            'token': serializer.data['token'],
            
            'Token2' : extendtoken()
            # 'UserID': serializer.data['UserID'],
            # 'OTP': serializer.data['OTP'],
        }
        status_code = status.HTTP_200_OK

        return Response(response, status=status_code)\

        

class ChangePasswordView(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    serializer_class =ChangePasswordSerializer

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
        Decode= jwt.decode(OldToken ,None,None)
        payload_data = {
            'Decode' : Decode,
            'Other_Fields' : Other_Fields
        }
        my_secret = 'my_super_secret'
        return Response({jwt.encode(payload=payload_data, key=my_secret)})


class UserPartiesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0 ):
        try:
            with transaction.atomic():
                query = MC_EmployeeParties.objects.raw('''SELECT  a.id,a.Party_id,b.Role_id  from (SELECT mc_employeeparties.id,mc_employeeparties.Party_id,'0' RoleID FROM mc_employeeparties where Employee_id=1)a left join (select mc_userroles.Party_id,mc_userroles.Role_id FROM mc_userroles join m_users on m_users.id=mc_userroles.User_id WHERE m_users.Employee_id=1)b on a.Party_id=b.Party_id''')
                print(str(query.query))
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Items Not available', 'Data': []}) 
                else:
                    M_UserParties_Serializer = M_UserPartiesSerializer(query, many=True).data

                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': M_UserParties_Serializer})  
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})


 
 

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