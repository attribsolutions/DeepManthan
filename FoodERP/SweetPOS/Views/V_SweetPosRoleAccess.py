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
                for a in MachineType_Data:
                    query = M_SweetPOSMachine.objects.filter(MacID=a['MacID'])
                    if query:
                        MachineType_serializer = MachineTypeSerializer(query[0],data=a)
                    else:
                        MachineType_serializer = MachineTypeSerializer(data=a)

                    if MachineType_serializer.is_valid():
                        MachineType = MachineType_serializer.save()
                        LastInsertID = MachineType.id
                    
                log_entry = create_transaction_logNew(request, MachineType_Data, MachineType_Data[0]['Party'], '', 416, LastInsertID)        
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Machine Type Save Successfully', 'TransactionID':LastInsertID, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'MachineTypeSave:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data':[]})
        
class MachineTypeListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        MachineType_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = MachineType_Data['Party']
                query = M_SweetPOSMachine.objects.raw('''Select A.id, A.Party, A.MacID, IFNULL(A.MachineRole, 0) AS MachineRole ,  B.Name MachineTypeName, A.IsServer, A.ClientID
                        From SweetPOS.M_SweetPOSMachine A 
                        left JOIN  FoodERP.M_GeneralMaster B on B.id = A.MachineRole
                        WHERE A.Party = %s''',[Party])
                
                MachineTypeList= list()
                for a in query:
                    q1 =  M_Settings.objects.filter(id=48).values('DefaultValue')
                    b = q1[0]['DefaultValue'].split('!')
                    c = [bb.strip().split('-') for bb in b]
                    for d in c:
                        if int(a.MachineRole) ==  int(d[0]):
                            RoleID = d[1]
                        else:
                            RoleID = ""
                    MachineTypeList.append({
                                "id": a.id,
                                "Party": a.Party,
                                "MacID": a.MacID,
                                "MachineType": a.MachineRole,
                                "MachineTypeName": a.MachineTypeName,
                                "IsServer": a.IsServer,
                                "ClientID": a.ClientID,
                                "MachineRole":RoleID
                                })
                log_entry = create_transaction_logNew(request, MachineType_Data, Party, '', 417, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :MachineTypeList})
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'Machine Role not available', 417, 0)
            return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Machine Role not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, MachineType_Data, 0, 'Machine Role List:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})
        
        

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

                SPOSLoginDetailsQuery = M_SweetPOSLogin.objects.raw('''SELECT M_SweetPOSLogin.id,UserName,DivisionID,ClientID,MacID,ExePath,ExeVersion,CreatedOn FROM SweetPOS.M_SweetPOSLogin WHERE CreatedOn BETWEEN %s AND %s AND DivisionID=%s''',[FromDate,ToDate,DivisionID])
                SPOSLoginDetailsList = list()

                for a in SPOSLoginDetailsQuery:
                    SPOSLoginDetailsList.append({
                        "id": a.id,
                        "UserName": a.UserName,
                        "DivisionID": a.DivisionID,
                        "ClientID": a.ClientID,
                        "MacID": a.MacID,
                        "ExePath": a.ExePath,
                        "ExeVersion": a.ExeVersion,
                        "CreatedOn": a.CreatedOn
                    })
                    
                log_entry = create_transaction_logNew(request, LoginData, 0, 'SPOSLoginDetails', 421, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': SPOSLoginDetailsList})
        except Exception as e:
            log_entry = create_transaction_logNew(request, LoginData, 0, 'SPOSLoginDetails:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
               




