from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Roles import *

from ..models import *



class M_RolesViewFilter(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 

                # if(RoleID == 1 ):
                #     M_Roles_data = M_Roles.objects.all()
                # else:
                #     M_Roles_data = M_Roles.objects.filter(CreatedBy=UserID)
                
                M_Roles_data = M_Roles.objects.filter(Company=CompanyID)
                
                if M_Roles_data.exists():
                    M_Roles_serializer = M_RolesSerializerforFilter(M_Roles_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Roles_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Role Not available', 'Data': []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})


class M_RolesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                M_Rolesdata = JSONParser().parse(request)
                M_Roles_Serializer = M_RolesSerializer(data=M_Rolesdata)
            if M_Roles_Serializer.is_valid():
                M_Roles_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Save Successfully', 'Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Roles_Serializer.errors, 'Data' : []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})


class M_RolesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Rolesdata = M_Roles.objects.filter(id=id)
                if M_Rolesdata.exists():
                    M_Roles_Serializer = M_RolesSerializerSecond(M_Rolesdata, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': M_Roles_Serializer})
                    RolesData=list()
                    for a in M_Roles_Serializer:
                        
                        RoleEmployeeTypesdata=list()
                        for b in a['RoleEmployeeTypes']:
                            RoleEmployeeTypesdata.append({
                               "EmployeeType":b['EmployeeType']['id'],
                               "EmployeeTypeName":b['EmployeeType']['Name'] 
                            })
                            
                        RolesData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "Description": a['Description'],
                            "isActive": a['isActive'],
                            "isSCMRole":a['isSCMRole'],
                            "IsPartyConnection": a['IsPartyConnection'],
                            "Dashboard": a['Dashboard'],
                            "CreatedBy":a['CreatedBy'],
                            "UpdatedBy": a['UpdatedBy'],
                            "RoleEmployeeTypes":RoleEmployeeTypesdata
                            
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': RolesData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'M_Roles Not available ', 'Data': []})
        except  M_Roles.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'M_Roles Not available', 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data':[]})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Rolesdata = JSONParser().parse(request)
                M_RolesdataByID = M_Roles.objects.get(id=id)
                M_Roles_Serializer = M_RolesSerializer(
                    M_RolesdataByID, data=M_Rolesdata)
                if M_Roles_Serializer.is_valid():
                    M_Roles_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Roles_Serializer.errors, 'Data' :[]})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Executiono Error', 'Data':[]})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Rolesdata = M_Roles.objects.get(id=id)
                M_Rolesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Deleted Successfully','Data':[]})
        except M_Roles.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Role Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Role used in another table', 'Data': []})