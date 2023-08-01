from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_SubGroup import *
from ..models import *
from ..Serializer.S_Orders import *

class SubGroupView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                SubGroupquery = MC_SubGroup.objects.all()
                if SubGroupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    SubGroupdata = SubGroupSerializerSecond(
                        SubGroupquery, many=True).data
                    SubGroupList = list()
                    for a in SubGroupdata:
                        SubGroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "Group": a['Group']['id'],
                            "GroupName": a['Group']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "Sequence":a['Sequence']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubGroupList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SubGroup Not available ', 'Data': []})
        except MC_SubGroup.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'SubGroup Not available', 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                SubGroup_data = JSONParser().parse(request)
                SubGroup_Serializer = SubGroupSerializer(data=SubGroup_data)
                if SubGroup_Serializer.is_valid():
                    SubGroup_Serializer.save()
                    log_entry = create_transaction_log(request, SubGroup_data, 0, 0, 'SubGroup Save Successfully')
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubGroup Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  SubGroup_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class SubGroupViewSecond(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                SubGroupquery = MC_SubGroup.objects.filter(id=id)
                if SubGroupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    SubGroupdata = SubGroupSerializerSecond(SubGroupquery, many=True).data
                    SubGroupList=list()
                    for a in SubGroupdata:
                        SubGroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "Group": a['Group']['id'],
                            "GroupName": a['Group']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "Sequence":a['Sequence']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubGroupList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SubGroup Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                SubGroup_data = JSONParser().parse(request)
                SubGroup_dataByID = MC_SubGroup.objects.get(id=id)
                SubGroup_Serializer = SubGroupSerializer(
                    SubGroup_dataByID, data=SubGroup_data)
                if SubGroup_Serializer.is_valid():
                    SubGroup_Serializer.save()
                    log_entry = create_transaction_log(request, SubGroup_data, 0, 0, 'SubGroup Updated Successfully')
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubGroup Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubGroup_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                SubGroup_data = MC_SubGroup.objects.get(id=id)
                SubGroup_data.delete()
                log_entry = create_transaction_log(request, SubGroup_data, 0, 0, 'SubGroup Deleted Successfully')
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubGroup Deleted Successfully', 'Data':[]})
        except MC_SubGroup.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'SubGroup Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'SubGroup used in another table', 'Data': []})   

class GetSubGroupByGroupID(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                SubGroupquery = MC_SubGroup.objects.filter(Group_id=id)
                if SubGroupquery.exists():
                    # return JsonResponse({'query':  str(SubGroupquery.query)})
                    SubGroupdata = SubGroupSerializerSecond(SubGroupquery, many=True).data
                    SubGroupList=list()
                    for a in SubGroupdata:
                        SubGroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "Group": a['Group']['id'],
                            "GroupName": a['Group']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "Sequence":a['Sequence']

                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubGroupList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SubGroup Not available ', 'Data': []})
        except MC_SubGroup.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'SubGroup Not available', 'Data': []})
