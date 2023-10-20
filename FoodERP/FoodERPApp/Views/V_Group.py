from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Group import *
from ..models import *
from ..Serializer.S_Orders import *


class GroupView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Groupquery = M_Group.objects.all()
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Groupdata = GroupSerializerSecond(
                        Groupquery, many=True).data
                    GroupList = list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GroupType": a['GroupType']['id'],
                            "GroupTypeName": a['GroupType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "Sequence":a['Sequence']
                        })
                    log_entry = create_transaction_logNew(request,Groupdata, 0,'',220,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList})
                log_entry = create_transaction_logNew(request,Groupdata, 0,'List Not available',220,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Group_data = JSONParser().parse(request)
                Group_Serializer = GroupSerializer(data=Group_data)
                if Group_Serializer.is_valid():
                    Group = Group_Serializer.save()
                    LastInsertID = Group.id
                    log_entry = create_transaction_logNew(request, Group_data, 0,'TransactionID:'+str(LastInsertID),22,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Save Successfully','TransactionID':LastInsertID, 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,Group_data, 0,Group_Serializer.errors,22,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Group_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class GroupViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = M_Group.objects.filter(id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Groupdata = GroupSerializerSecond(Groupquery, many=True).data
                    GroupList=list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GroupType": a['GroupType']['id'],
                            "GroupTypeName": a['GroupType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "Sequence":a['Sequence']
                        })
                    log_entry = create_transaction_logNew(request,Groupdata, 0,'',221,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList[0]})
                log_entry = create_transaction_logNew(request,Groupdata, 0,'Details Not available',221,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Group_data = JSONParser().parse(request)
                Group_dataByID = M_Group.objects.get(id=id)
                Group_Serializer = GroupSerializer(
                    Group_dataByID, data=Group_data)
                if Group_Serializer.is_valid():
                    Group_Serializer.save()
                    log_entry = create_transaction_logNew(request, Group_data, 0,'GroupID:'+str(id),23,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,Group_data, 0,Group_Serializer.errors,23,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Group_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Group_data = M_Group.objects.get(id=id)
                Group_data.delete()
                log_entry = create_transaction_logNew(request,{'GroupID':id}, 0,'',24,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Deleted Successfully', 'Data':[]})
        except M_Group.DoesNotExist:
            log_entry = create_transaction_logNew(request,{'GroupID':id}, 0,'Group Not available',24,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group Not available', 'Data': []})
        except IntegrityError:   
            log_entry = create_transaction_logNew(request,0, 0,'Group used in another table',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Group used in another table', 'Data': []})   

class GetGroupByGroupTypeID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = M_Group.objects.filter(GroupType_id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Groupdata = GroupSerializerSecond(Groupquery, many=True).data
                    GroupList=list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "GroupType": a['GroupType']['id'],
                            "GroupTypeName": a['GroupType']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "Sequence":a['Sequence']
                        })
                    log_entry = create_transaction_logNew(request,Groupdata, 0,'',222,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList})
                log_entry = create_transaction_logNew(request,Groupdata, 0,'Group Not available',222,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
