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
            log_entry = create_transaction_logNew(request,0, 0,'GroupList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

    @transaction.atomic()
    def post(self, request):
        Group_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Group_Serializer = M_GroupSerializerForItem(data=Group_data)
                if Group_Serializer.is_valid():
                    Group = Group_Serializer.save()
                    LastInsertID = Group.id
                    log_entry = create_transaction_logNew(request, Group_data, 0,'TransactionID:'+str(LastInsertID),22,LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Save Successfully','TransactionID':LastInsertID, 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request,Group_data, 0,'GroupSave:'+str(Group_Serializer.errors),22,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Group_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Group_data, 0,'GroupSave:'+str(e),33,0)
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
            log_entry = create_transaction_logNew(request,0, 0,'GroupGETMethod'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        Group_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Group_dataByID = M_Group.objects.get(id=id)
                Group_Serializer = GroupSerializerThird(
                    Group_dataByID, data=Group_data)
                if Group_Serializer.is_valid():
                    Group_Serializer.save()
                    log_entry = create_transaction_logNew(request, Group_data, 0,'GroupID:'+str(id),23,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Group Updated Successfully', 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request,Group_data, 0,'GroupEdit:'+str(Group_Serializer.errors),23,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Group_Serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Group_data, 0,'GroupEdit:'+str(e),33,0)
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
            log_entry = create_transaction_logNew(request,0, 0,'Group Not available',24,0)
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
            log_entry = create_transaction_logNew(request,0, 0,'GetGroupByGroupTypeIDmethod:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class DetailsOfSubgroups_GroupsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query1 = M_Group.objects.filter(GroupType_id=id)
                if not query1.exists():
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'GroupType Not available', 'Data': []})

                GroupSubgroupItemList = []
                for aa in query1:
                    query2 = MC_SubGroup.objects.filter(Group=aa)
                    for subgroup in query2:
                            if query2.exists():
                                query3 = MC_ItemGroupDetails.objects.filter(Group=aa, SubGroup=subgroup).select_related('Item').order_by('ItemSequence')
                                SubGroupID = subgroup.id
                                SubGroupName = subgroup.Name
                                SubGroupSequence = subgroup.Sequence     
                            else:
                                query3 = MC_ItemGroupDetails.objects.filter(Group=aa).select_related('Item').order_by('ItemSequence')
                                SubGroupID = None
                                SubGroupName = None
                                SubGroupSequence = None
                            ItemList = list()
                            for a in query3:
                                ItemList.append(
                                            {
                                            "ItemID": a.Item.id,
                                            "ItemName": a.Item.Name,
                                            "ItemSequence": a.ItemSequence
                                        } 
                                            )
                            GroupSubgroupItemList.append({
                                            "GroupTypeID": aa.GroupType_id,
                                            "GroupID": aa.id,
                                            "GroupName": aa.Name,
                                            "GroupSequence": aa.Sequence,
                                            "SubGroupID": SubGroupID,
                                            "SubGroupName": SubGroupName,
                                            "SubGroupSequence": SubGroupSequence,
                                            "Items": ItemList
                                        })
                log_entry = create_transaction_logNew(request,0, 0,'GroupTypeID:'+str(id),393,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupSubgroupItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0, 0,'DetailsOfsubgroups_groups:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


class UpdateGroupSubGroupSequenceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        SequenceData = JSONParser().parse(request)
        try:
            if not isinstance(SequenceData, list):
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid data format', 'Data': []})

            Group_IDs = list(set(item['GroupID'] for item in SequenceData))
            groups = M_Group.objects.filter(id__in=Group_IDs)
            if groups.count() != len(Group_IDs):
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'One or more groups not found', 'Data': []})

            SubGroup_IDs = list(set(item['SubGroupID'] for item in SequenceData if 'SubGroupID' in item and item['SubGroupID'] is not None))
            subgroups = MC_SubGroup.objects.filter(id__in=SubGroup_IDs)
            if subgroups.count() != len(SubGroup_IDs):
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'One or more subgroups not found', 'Data': []})

            Item_IDs = list(set(item['ItemID'] for group in SequenceData if 'Items' in group for item in group['Items']))
            items = M_Items.objects.filter(id__in=Item_IDs)
            if items.count() != len(Item_IDs):
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'One or more items not found', 'Data': []})

            item_group_details = MC_ItemGroupDetails.objects.filter(Item__in=Item_IDs, Group__in=Group_IDs)

            Group_Data = {group.id: group for group in groups}
            SubGroup_Data = {subgroup.id: subgroup for subgroup in subgroups}
            Item_Data = {item.id: item for item in items}
            ItemGroup_Data = {(item_detail.Item.id, item_detail.Group.id): item_detail for item_detail in item_group_details}

            for group_data in SequenceData:
                Group_ID = group_data['GroupID']
                Group_Sequence = group_data['GroupSequence']
                Group = Group_Data[Group_ID]
                Group.Sequence = Group_Sequence
                Group.save()

                SubGroup_ID = group_data.get('SubGroupID')
                if SubGroup_ID is not None:
                    SubGroup_Sequence = group_data['SubGroupSequence']
                    SubGroup = SubGroup_Data[SubGroup_ID]
                    SubGroup.Sequence = SubGroup_Sequence
                    SubGroup.save()

                for item_data in group_data['Items']:
                    Item_ID = item_data['ItemID']
                    Item_Sequence = item_data['ItemSequence']
                    item_group_detail = ItemGroup_Data.get((Item_ID, Group_ID))

                    if item_group_detail:
                        item_group_detail.ItemSequence = Item_Sequence
                        item_group_detail.save()

            log_entry = create_transaction_logNew(request,SequenceData, 0,'',394,0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Sequences updated successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request,SequenceData, 0,'GroupSubGroupSequenceUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


        
    