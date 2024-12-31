import base64
from ..models import *
from ..Serializer.S_SweetPosRoleAccess import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from datetime import datetime
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
import pdb
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew
from FoodERPApp.models import *
from rest_framework.authentication import BasicAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication

def BasicAuthenticationfunction(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
                    
        # Parsing the authorization header
        auth_type, auth_string = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            
            
            try:
                username, password = base64.b64decode(
                    auth_string).decode().split(':', 1)
            except (TypeError, ValueError, UnicodeDecodeError):
                return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                
        user = authenticate(request, username=username, password=password)
    return user



class SweetPosRoleAccessView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        SPOSRoleAccessdata = JSONParser().parse(request)
        try:  
            with transaction.atomic():
               
                response_data = []
                
                for data in SPOSRoleAccessdata:
                    
                    if 'Party' in data and M_SweetPOSRoleAccess.objects.using('sweetpos_db').filter(Party=data['Party']).exists():
                        obj = M_SweetPOSRoleAccess.objects.using('sweetpos_db').get(Party=data['Party'])
                        for key, value in data.items():
                           setattr(obj, key, value)
                        obj.save(using='sweetpos_db')
                        
                    else:
                       
                        obj = M_SweetPOSRoleAccess(**data)
                        obj.save(using='sweetpos_db')
                        

                log_entry = create_transaction_logNew(request, SPOSRoleAccessdata,SPOSRoleAccessdata[0]['Party'],'',346,0)    

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SweetPosRoleAccess Save Successfully', 'Data':[]}) 
        except Exception as e:
            log_entry = create_transaction_logNew(request, SPOSRoleAccessdata,0,'SweetPosRoleAccess Save:'+str(list(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  list(e), 'Data':[]})
        
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                RoleAccessData = M_SweetPOSRoleAccess.objects.raw('''Select A.id, A.Name,A.id Party, B.*
                                        From FoodERP.M_Parties A
                                        Left Join SweetPOS.M_SweetPOSRoleAccess B on A.id = B.Party
                                        where A.PartyType_id = 19''')                       
                RoleAccess_serializer = SPOSRoleAccessSerializerSecond(RoleAccessData, many=True).data
                
                log_entry = create_transaction_logNew(request, RoleAccess_serializer,0,'',347,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': RoleAccess_serializer})
        except  M_SweetPOSRoleAccess.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSRoleAccessDetails'+'RoleAccess Not available',347,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'RoleAccess Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'GETSweetPOSRoleAccessDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})



class SPOSLog_inView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request ):
        SPOSLog_in_data = JSONParser().parse(request)
        try:
            
            with transaction.atomic():
               
                # pdb.set_trace()
                Division = SPOSLog_in_data['DivisionID']

                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                    obj = M_SweetPOSLogin(**SPOSLog_in_data)
                    obj.save(using='sweetpos_db')
                    
                    # responce=M_SweetPOSRoleAccess.objects.using('sweetpos_db').get(Party=Division)
                    
                    # responce_serializer=SPOSRoleAccessSerializer(responce).data
                    
                    log_entry = create_transaction_logNew(request, SPOSLog_in_data,0,'',348,0)
                    return JsonResponse({"Success":True,"Status":200,"Message":"Loged In Successfully..!"})
                    

        except Exception as e:
            log_entry = create_transaction_logNew(request, SPOSLog_in_data,0,'SweetPOSLogin:'+str(e),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
class MachineTypeSaveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        MachineType_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                    query = M_SweetPOSMachine.objects.filter(MacID=MachineType_Data['MacID'])
                    if query.exists():
                        return JsonResponse({'StatusCode': 400,'Status': False,'Message': 'MacID already exist!', 'Data': []})
                    MachineType_serializer = MachineTypeSerializer(data=MachineType_Data)
                    if MachineType_serializer.is_valid():
                        MachineType = MachineType_serializer.save()
                        LastInsertID = MachineType.id
                        log_entry = create_transaction_logNew(request, MachineType_Data, MachineType_Data['Party'], '', 416, LastInsertID)        
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Machine Type Save Successfully',"TransactionID" : LastInsertID, 'Data':[]})
                    log_entry = create_transaction_logNew(request, MachineType_Data, MachineType_Data['Party'], '', 416, 0)
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': MachineType_serializer.errors, 'Data': []})
                    
        except Exception as e:
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'MachineTypeSave:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
        
class MachineTypeListView(CreateAPIView):
     
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
 
    @transaction.atomic
    def post(self, request):
       
        if not request.user or not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication failed.")
        
        MachineType_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = MachineType_Data['Party']
                query = M_SweetPOSMachine.objects.raw('''Select A.id, A.Party, A.MacID, ifnull(A.MachineType,'') MachineType ,  B.Name MachineTypeName, A.IsServer, A.ClientID,A.IsAutoUpdate,A.IsGiveUpdate,A.IsService,IFNULL(A.MachineName, '') AS MachineName,A.ServerSequence,A.UploadSaleRecordCount,A.Validity,IFNULL(A.Version,'') AS Version, A.SeverName, A.ServerHost, A.ServerUser, A.ServerPassWord, A.ServerDatabase, A.Invoiceprefix
                        From SweetPOS.M_SweetPOSMachine A
                        left JOIN  FoodERP.M_GeneralMaster B on B.id = A.MachineType
                        WHERE A.Party = %s''',[Party])
              
                MachineTypeList= list()
                for a in query:
                    MachineTypeIDs = a.MachineType.split(',') if a.MachineType else []
                    MachineTypeDetails = []
                    RoleIDs = []
                    
                    for MachineTypeID in MachineTypeIDs:
                        subquery = M_GeneralMaster.objects.filter(id=MachineTypeID.strip()).values('id', 'Name').first() 
                        if subquery:
                            MachineTypeDetails.append({
                                "id": subquery['id'],
                                "MachineTypeName": subquery['Name']
                            })  
                        q1 =  M_Settings.objects.filter(id=48).values('DefaultValue')
                        b = q1[0]['DefaultValue'].split('!')
                        c = [bb.strip().split('-') for bb in b]
                
                        for d in c:
                            if MachineTypeID.strip() == d[0]:
                                RoleIDs.append(d[1])  
                                role_names = []
                                if RoleIDs:
                                    roles = M_Roles.objects.filter(id__in=RoleIDs).values('id', 'Name')
                                    for role in roles: 
                                        role_names.append(role['Name'])
                                MachineRole_Name = ','.join(role_names)
                                
                    RoleID = ','.join(RoleIDs) or ""   
                    
                    MachineTypeList.append({
                                "id": a.id,
                                "Party": a.Party,
                                "MacID": a.MacID,
                                "MachineTypeDetails": MachineTypeDetails,
                                "IsServer": a.IsServer,
                                "ClientID": a.ClientID,
                                "MachineRole":RoleID, 
                                "MachineRoleName":MachineRole_Name if RoleID not in [None, ""] else None,
                                "IsAutoUpdate":a.IsAutoUpdate,
                                "IsGiveUpdate":a.IsGiveUpdate,
                                "IsService":a.IsService,
                                "MachineName":a.MachineName,
                                "ServerSequence":a.ServerSequence,
                                "UploadSaleRecordCount":a.UploadSaleRecordCount,
                                "Validity":a.Validity,
                                "Version":a.Version,
                                "ServerName":a.SeverName,
                                "ServerHost": a.ServerHost,
                                "ServerUser": a.ServerUser,
                                "ServerPassWord": a.ServerPassWord,
                                "ServerDatabase": a.ServerDatabase,
                                "Invoiceprefix": a.Invoiceprefix
                                })
                log_entry = create_transaction_logNew(request, MachineType_Data, Party, '', 417, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :MachineTypeList})
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'Machine Type not available', 417, 0)
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Machine Type not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'Machine Type List:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]})
        

class SPOSLoginDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
   
    @transaction.atomic()
    def post(self, request):
        LoginData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDateStr = LoginData['FromDate']
                ToDateStr = LoginData['ToDate']
                FromDate = datetime.strptime(FromDateStr, '%Y-%m-%d %H:%M:%S')
                ToDate = datetime.strptime(ToDateStr, '%Y-%m-%d %H:%M:%S')
                DivisionID = LoginData['DivisionID']

                if DivisionID == 0:
                    SPOSLoginDetailsQuery = M_SweetPOSLogin.objects.raw('''
                        SELECT L.id, L.UserName, L.DivisionID, L.ClientID, L.MacID, L.ExePath,
                               L.ExeVersion, L.CreatedOn, M.MachineName, P.Name AS DivisionName
                        FROM SweetPOS.M_SweetPOSLogin L

                        JOIN SweetPOS.M_SweetPOSMachine M ON L.ClientID = M.id
                        LEFT JOIN FoodERP.M_Parties P ON L.DivisionID = P.id
                        WHERE L.CreatedOn BETWEEN %s AND %s''', [FromDate, ToDate])
                else:
                    SPOSLoginDetailsQuery = M_SweetPOSLogin.objects.raw('''
                        SELECT L.id, L.UserName, L.DivisionID, L.ClientID, L.MacID, L.ExePath,
                               L.ExeVersion, L.CreatedOn, M.MachineName, P.Name AS DivisionName
                        FROM SweetPOS.M_SweetPOSLogin L
                        JOIN SweetPOS.M_SweetPOSMachine M ON L.ClientID = M.id 
                        LEFT JOIN M_Parties P ON L.DivisionID = P.id
                        WHERE L.CreatedOn BETWEEN %s AND %s AND L.DivisionID = %s''', [FromDate, ToDate, DivisionID])


                SPOSLoginDetailsList = list()
 
                for a in SPOSLoginDetailsQuery:
                    SPOSLoginDetailsList.append({
                        "id": a.id,
                        "UserName": a.UserName,
                        "DivisionID": a.DivisionID,
                        "DivisionName": a.DivisionName,
                        "ClientID": a.ClientID,
                        "MacID": a.MacID,
                        "MachineName": a.MachineName,
                        "ExePath": a.ExePath,
                        "ExeVersion": a.ExeVersion,
                        "CreatedOn": a.CreatedOn
                    })

                if SPOSLoginDetailsList:
                    log_entry = create_transaction_logNew(request, LoginData, 0, 'SPOSLoginDetails', 422, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SPOSLoginDetailsList})
                else:
                    log_entry = create_transaction_logNew(request, LoginData, 0, "SPOSLoginDetails Not available", 422, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SPOSLoginDetails Not available', 'Data': []})

 
        except Exception as e:
            log_entry = create_transaction_logNew(request, LoginData, 0, 'SPOSLoginDetails:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


        
class MachineTypeUpdateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def put(self, request):
        MachineType_Data = JSONParser().parse(request)
        try:
            query = M_SweetPOSMachine.objects.filter(Party=MachineType_Data['Party'],MacID=MachineType_Data['MacID'])
            if not query:
                log_entry = create_transaction_logNew(request, MachineType_Data, MachineType_Data['Party'], 'Machine Type not available', 418, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Record Not Found', 'TransactionID': 0, 'Data': []})
            MachineType_serializer = MachineTypeSerializer(query[0], data=MachineType_Data)
            if MachineType_serializer.is_valid():
                MachineType_serializer.save()
                log_entry = create_transaction_logNew(request, MachineType_Data, MachineType_Data['Party'], '', 418, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': 'Machine Type Update Successfully', 'Data': []})
            else:
                return JsonResponse({'StatusCode': 400,'Status': True,'Message': MachineType_serializer.errors,'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'MachineTypeUpdate:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
               




