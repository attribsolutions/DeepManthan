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
        
        
class DetailsOfSubgroups_GroupsViewNEW(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        DetailsOfSubgroups = JSONParser().parse(request)
        try:
            with transaction.atomic():
                GroupType_id = DetailsOfSubgroups['GroupType_id']
                Company_id = DetailsOfSubgroups['Company_id']
                
                GroupSubgroupItemList = []
                query = M_Items.objects.raw(f'''select * from 
                (select 1 as id,  G.Id as GroupID,G.name as GroupName,G.Sequence GroupSequence,IGD.GroupType_Id,IGD.SubGroup_Id,IGD.ItemSequence,
                SG.Id as SubGroupID, SG.Name as SubGroupName,SG.Sequence as SubGroupSequence,I.Id ItemID,I.Name ItemName
from M_Group G 
left join MC_ItemGroupDetails IGD on IGD.Group_Id=G.Id
left join MC_SubGroup SG ON SG.Id = IGD.SubGroup_id 
left join M_Items I on I.Id=IGD.Item_Id 
where G.GroupType_Id={GroupType_id} and I.Company_id={Company_id}

union
select 1 as id, g.id as GroupID,g.name as GroupName,g.Sequence GroupSequence,igd.GroupType_id,igd.SubGroup_id,igd.ItemSequence,
                sg.id as SubGroupID, sg.Name as SubGroupName,sg.Sequence as SubGroupSequence,i.id ItemID,i.Name ItemName
                from M_Items as i 
                left join MC_ItemGroupDetails as igd ON i.id=igd.Item_ID and igd.GroupType_id={GroupType_id}
                left join M_Group as g ON g.id=igd.Group_id
                left join MC_SubGroup as sg on sg.id=igd.SubGroup_id
                where i.Company_id={Company_id} )a order by GroupSequence,SubGroupSequence,ItemSequence''')
                
                grouped_data = {}

                for a in query:
                    group_key = (a.GroupID, a.SubGroupID)
                    
                    if group_key not in grouped_data:
                        grouped_data[group_key] = {
                            "GroupTypeID": GroupType_id,
                            "GroupID": a.GroupID,
                            "GroupName": a.GroupName,
                            "GroupSequence": a.GroupSequence,
                            "SubGroupID": a.SubGroupID,
                            "SubGroupName": a.SubGroupName,
                            "SubGroupSequence": a.SubGroupSequence,
                            "Items": []
                        }

                    grouped_data[group_key]["Items"].append({
                        "ItemID": a.ItemID,
                        "ItemName": a.ItemName,
                        "ItemSequence": a.ItemSequence
                    })

                for key, group_data in grouped_data.items():
                    GroupSubgroupItemList.append(group_data)
                    
                log_entry = create_transaction_logNew(request,DetailsOfSubgroups, 0,'GroupTypeID:'+str(id),393,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupSubgroupItemList})                
        except Exception as e:
                log_entry = create_transaction_logNew(request,DetailsOfSubgroups, 0,'DetailsOfsubgroups_groups:'+str(e),33,0)
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
                GroupType_ID = group_data['GroupTypeID']
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
                        # Delete item_group_detail if GroupTypeID matches
                        if item_group_detail.GroupType.id == GroupType_ID:
                            item_group_detail.delete()
                            continue  # Skip to the next item, as this one is deleted
                        
                        # item_group_detail.ItemSequence = Item_Sequence 
                        
                        # # Update SubGroupID 
                        # if SubGroup_ID is not None: 
                        #     item_group_detail.SubGroup = SubGroup_Data[SubGroup_ID]  # Update the SubGroup field
                        # # End Update 
                         
                        # item_group_detail.save()
                        
            log_entry = create_transaction_logNew(request,SequenceData, 0,'',394,0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Sequences updated successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request,SequenceData, 0,'GroupSubGroupSequenceUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': Exception(e), 'Data': []})
  
  
class UpdateGroupSubGroupSequenceViewNew(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        GivenJSONData = JSONParser().parse(request)
        try:
            GroupID = list({group['GroupID'] for group in GivenJSONData}) 
            SubGroupID = [group.get('SubGroupID') for group in GivenJSONData if group.get('SubGroupID') is not None]
            Item_ID = [item['ItemID'] for group in GivenJSONData for item in group['Items']]
           
            items_to_update = []
            items_to_create = []
            query = MC_ItemGroupDetails.objects.filter(SubGroup_id__in=SubGroupID, Group__in=GroupID).delete()
            for a in GivenJSONData:
                Group_ID = a['GroupID']
                GroupType_ID = a['GroupTypeID']
                SubGroup_ID = a['SubGroupID']
                Group_Sequence = a['GroupSequence']
                SubGroupSequence = a['SubGroupSequence']
                
                if Group_Sequence is not None:
                    M_Group.objects.filter(id=Group_ID).update(Sequence=Group_Sequence)
                
                if SubGroupSequence is not None:
                    MC_SubGroup.objects.filter(id=SubGroup_ID).update(Sequence=SubGroupSequence)

                for b in a['Items']:
                    Item_ID = b['ItemID']
                    Item_Sequence = b['ItemSequence']

                    q0 = MC_ItemGroupDetails.objects.filter(
                        Item_id=Item_ID, Group_id=Group_ID, SubGroup_id=SubGroup_ID)
                    if q0:
                        q0.ItemSequence = Item_Sequence
                        q0.GroupType_id = GroupType_ID
                        items_to_update.append(q0)
                    else:
                        q1 = MC_ItemGroupDetails(
                            Item_id=Item_ID,
                            Group_id=Group_ID,
                            ItemSequence=Item_Sequence,
                            GroupType_id=GroupType_ID,
                            SubGroup_id=SubGroup_ID
                        )
                        items_to_create.append(q1)

            if items_to_update:
                MC_ItemGroupDetails.objects.bulk_update(items_to_update, ['ItemSequence', 'GroupType_id'])

            if items_to_create:
                MC_ItemGroupDetails.objects.bulk_create(items_to_create)
            
            log_entry = create_transaction_logNew(request, GivenJSONData, 0, '', 394, 0)
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Sequences updated successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, GivenJSONData, 0, 'GroupSubGroupSequenceUpdate:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
  
# class UpdateGroupSubGroupSequenceViewNew(CreateAPIView):
#     permission_classes = (IsAuthenticated,)

#     @transaction.atomic
#     def post(self, request):
#         GivenJSONData = JSONParser().parse(request)
#         try:
#             if not isinstance(GivenJSONData, list):
#                 return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Data expected in list format', 'Data': []})
                
#             # Get all distinct group IDs from GivenJSONData
#             distinct_group_ids = list({group['GroupID'] for group in GivenJSONData}) 
            
#             # Get all item IDs from GivenJSONData
#             item_ids = [item['ItemID'] for group in GivenJSONData for item in group['Items']] 
 
#             # Fetch existing item group details
#             item_group_details = MC_ItemGroupDetails.objects.filter(Item__in=item_ids, Group__in=distinct_group_ids)
            
#             # Count the existing item group details
#             item_group_details_count = item_group_details.count() 
             
#             if item_group_details_count > 0: 
#                 # Filter items where PriviousGroup_ID is not None
#                 filtered_items = [item for group in GivenJSONData for item in group['Items'] if item['PriviousGroup_ID'] is not None]
                 
#                 # Get ItemIDs from filtered_items
#                 if filtered_items:
#                     item_ids_for_delete = [item['ItemID'] for item in filtered_items]
#                     print("Item IDs to delete:", item_ids_for_delete)

#                     # Perform the deletion
#                     if item_ids_for_delete:
#                         deleted_count = MC_ItemGroupDetails.objects.filter(Item__in=item_ids_for_delete).delete()
#                         print(f"Deleted {deleted_count} items.")
#                 #     else:
#                 #         print("No Item IDs found for deletion.")
#                 # else:
#                 #     print("No items with PriviousGroup_ID found.")
                 
                
#                 # Delete existing records
#                 MC_ItemGroupDetails.objects.filter(Item__in=item_ids, Group__in=distinct_group_ids).delete()
#                 print("Delete")
              
              
#             # Prepare data for saving
#             items_to_save = []
#             for group_data in GivenJSONData:
#                 Group_ID = group_data['GroupID']
#                 GroupType_ID = group_data.get('GroupTypeID', None)
#                 SubGroup_ID = group_data.get('SubGroupID', None)  
#                 Group_Sequence = group_data.get('GroupSequence', None)  
#                 SubGroupSequence=group_data.get('SubGroupSequence',None)
                 
#                 # Update the GroupSequence in the M_Group model
#                 if Group_Sequence is not None:
#                     M_Group.objects.filter(id=Group_ID).update(Sequence=Group_Sequence)
#                     print(f"Updated GroupSequence for Group {Group_ID} to {Group_Sequence}")
                
#                 if SubGroupSequence is not None :
#                     MC_SubGroup.objects.filter(id=SubGroup_ID).update(Sequence=SubGroupSequence)
#                     print(f"Updated GroupSequence for Group {SubGroup_ID} to {SubGroupSequence}")
                          
#                 for item_data in group_data['Items']:
#                     Item_ID = item_data['ItemID']
#                     Item_Sequence = item_data['ItemSequence']
#                     # Create a new instance of MC_ItemGroupDetails
#                     item_group_detail = MC_ItemGroupDetails(
#                         Item_id=Item_ID,
#                         Group_id=Group_ID,
#                         ItemSequence=Item_Sequence,
#                         GroupType_id=GroupType_ID,
#                         SubGroup_id=SubGroup_ID
#                     )
#                     items_to_save.append(item_group_detail)
            
#             # Save new data in bulk
#             MC_ItemGroupDetails.objects.bulk_create(items_to_save)
#             print("save")
 
#             return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GivenJSONData updated successfully', 'Data': []})

#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
   
 
        
    