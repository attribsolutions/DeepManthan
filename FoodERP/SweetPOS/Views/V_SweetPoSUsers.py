import base64
from ..models import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from FoodERPApp.models import *
from ..Serializer.S_SweetPoSUsers import *
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew
from ftplib import FTP
import configparser
import os


class SweetPOSUsersView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        User_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                User_data_serializer  = UsersSerializer(data=User_data )
                if User_data_serializer .is_valid():
                    User_data_serializer .save()
                    log_entry = create_transaction_logNew(request, User_data,0,'',372,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Data Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, User_data,0,'UserSave:'+str(User_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': User_data_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, User_data, 0,'UserSave:'+str(e),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
 

class SweetPOSSingleUserView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_SweetPOSUser.objects.raw(f'''
                    SELECT SU.id, CompanyID, DivisionID, LoginName, Password, RoleID, IsActive, SU.CreatedBy, SU.CreatedOn, SU.UpdatedBy, SU.UpdatedOn, M_SweetPOSRoles.Name as RoleName
                    FROM SweetPOS.M_SweetPOSUser SU
                    JOIN SweetPOS.M_SweetPOSRoles ON SweetPOS.SU.RoleID = SweetPOS.M_SweetPOSRoles.id
                    WHERE SU.id = %s
                ''', [id])

                if not query:
                    raise M_SweetPOSUser.DoesNotExist

                user = query[0]
                UserList = {
                    "id": user.id,
                    "CompanyID": user.CompanyID,
                    "DivisionID": user.DivisionID,
                    "LoginName": user.LoginName,
                    "Password": user.Password,
                    "RoleID": user.RoleID,
                    "IsActive": user.IsActive,
                    "CreatedBy": user.CreatedBy,
                    "CreatedOn": user.CreatedOn,
                    "UpdatedBy": user.UpdatedBy,
                    "UpdatedOn": user.UpdatedOn,
                    "RoleName": user.RoleName,
                }

            log_entry = create_transaction_logNew(request, UserList, 0, '', 373, 0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': UserList})
        except M_SweetPOSUser.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0, 0, 'Users Data Does Not Exist', 373, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Users Data Not available', 'Data': {}})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'GETAllUsers:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': {}})
        
    @transaction.atomic()
    def put(self, request, id=0):
        User_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                User_DataByID  = M_SweetPOSUser.objects.get(id=id)
                User_data_serializer = UsersSerializer(User_DataByID , data=User_data)
                if User_data_serializer.is_valid():
                    User_data_serializer.save()
                    log_entry = create_transaction_logNew(request, User_data,0,'',375,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Data Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, User_data,0,'UserEdit:'+str(User_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': User_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, User_data, 0,'UserEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                User_data = M_SweetPOSUser.objects.get(id=id)
                User_data.delete()
                log_entry = create_transaction_logNew(request, User_data,0,'',376,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'User Data Deleted Successfully','Data':[]})
        except M_SweetPOSUser.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'User Data Not available',376,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'User Data Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'User Data used in another table',8,0)  
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'User Data used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'UserDelete:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})  


       
# Don't CommentOut below Logs without Permission  -- Commented By Pratiksha

class SweetPOSUsersSecondView(CreateAPIView):
    permission_classes = ()

    @transaction.atomic()
    def get(self, request, Division_id=0):
        try:
            with transaction.atomic():
                query = M_SweetPOSUser.objects.raw(f""" SELECT SU.id, CompanyID, DivisionID, LoginName, Password, RoleID, IsActive, SU.CreatedBy, SU.CreatedOn, SU.UpdatedBy, SU.UpdatedOn, M_SweetPOSRoles.Name as RoleName
                                FROM SweetPOS.M_SweetPOSUser SU
                                JOIN SweetPOS.M_SweetPOSRoles  ON SU.RoleID = SweetPOS.M_SweetPOSRoles.id
                                WHERE SU.DivisionID = {Division_id}""")
                
                user_list = []
                for row in query:
                    user_list.append({
                        "id": row.id,
                        "CompanyID": row.CompanyID,
                        "DivisionID": row.DivisionID,
                        "LoginName": row.LoginName,
                        "Password": row.Password,
                        "RoleID": row.RoleID,
                        "IsActive": row.IsActive,
                        "CreatedBy": row.CreatedBy,
                        "CreatedOn": row.CreatedOn,
                        "UpdatedBy": row.UpdatedBy,
                        "UpdatedOn": row.UpdatedOn,
                        "RoleName": row.RoleName,
                    })

                # log_entry = create_transaction_logNew(request, user_list, 0, '', 374, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': user_list})
        except M_SweetPOSUser.DoesNotExist:
            # log_entry = create_transaction_logNew(request, 0, 0, 'User data not available', 374, 0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'User data not available', 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0, 'GETUser:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})



   

class SweetPOSRolesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                role_data = M_SweetPOSRoles.objects.raw('''SELECT S.id, S.Name, S.CreatedBy, S.CreatedOn, S.UpdatedBy, S.UpdatedOn
FROM SweetPOS.M_SweetPOSRoles S''')
                role_data_serializer = RolesSerializer(role_data,many=True).data
                log_entry = create_transaction_logNew(request, role_data_serializer,0,'',377,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': role_data_serializer})
        except  M_SweetPOSRoles.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Role Data Does Not Exist',377,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Role Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllRoles:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
        
        
        
        

        
        
class LVersionsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        UserData = JSONParser().parse(request)      
        try:
            with transaction.atomic():
                Party = UserData['Party'] 
                Q11=M_Settings.objects.filter(id=58).values("DefaultValue")
                PartyTypeID1=Q11[0]['DefaultValue'].split(',')
                ExeVersion=PartyTypeID1[0].strip()
                WinVersion=PartyTypeID1[1].strip()
                print(ExeVersion,WinVersion)
                # ftp_host = "web.chitalebandhu.in"  
                # ftp_user = "attribftp"  
                # ftp_pass = "Attrib@318" 
                              
                # ftp = FTP(ftp_host)
                # ftp.login(ftp_user, ftp_pass)
                # ftp.cwd("SweetPOSPython")
                
                # local_path = os.path.join(os.path.expanduser("~"), "version.ini")
                # filename = "version.ini"
                # with open(local_path, "wb") as file:
                #     ftp.retrbinary(f"RETR {filename}", file.write)

                # ftp.quit()
                # print(f"{filename}: {local_path}")
                
                
                # config = configparser.ConfigParser()
                # config.read(local_path)
                # exe_version = config.get("current_version", "ExeVersion", fallback=None)
                # Service_Version = config.get("current_version", "ServiceVersion", fallback=None)    
                # if not exe_version:
                #     return JsonResponse({"StatusCode": 404, "Status": False, "Message": "'ExeVersion' Not Found", "Data": []})
                # else:
                #     return Response({"message": "'ExeVersion' Not Found", "status": "error"}, status=404)                 
                query = M_SweetPOSUser.objects.raw("""SELECT 1 AS id,l.MacID, 
                    MAX(CASE WHEN l.ExeVersion LIKE 'WS%%' THEN l.ExeVersion END) AS WinService,
                    MAX(CASE WHEN l.ExeVersion NOT LIKE 'WS%%' THEN l.ExeVersion END) AS ExeVersion,
                    m.MachineName 
                    FROM SweetPOS.M_SweetPOSLogin l
                    LEFT JOIN SweetPOS.M_SweetPOSMachine m ON m.MacID = l.MacID
                    WHERE l.DivisionID =%s GROUP BY l.MacID, m.MachineName""", [Party])            
                user_list = []
                for row in query:
                    user_list.append({
                            "id": row.id,
                            "MacID": row.MacID,                            
                            "Version":{
                                "ExeVersion": row.ExeVersion,
                                "WinServise":row.WinService
                            },
                            "MachineName":row.MachineName                           
                        })  
                              
                # log_entry = create_transaction_logNew( request, user_list, Party, '', 444, 0,0,0,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Latest_EXE_version': ExeVersion,'Latest_Service_Version':WinVersion,'Data': user_list})        

        except Exception as e:
            log_entry = create_transaction_logNew( request, 0, 0, str(e), 33,0,0,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})