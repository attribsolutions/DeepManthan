from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyItems import *
from ..models import *
from ..Views.V_CommFunction import *
from django.utils import timezone


class PartyItemsListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = MC_PartyItems.objects.raw(
                    '''select MC_PartyItems.id,M_Parties.Name, MC_PartyItems.Party_id,count(MC_PartyItems.Item_id)As Total From MC_PartyItems join M_Parties on M_Parties.id=MC_PartyItems.Party_id group by MC_PartyItems.Party_id  ''')
                if not query:
                    log_entry = create_transaction_logNew(request,0,0,'Items Not available',180,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = MC_PartyItemListSerializer(
                        query, many=True).data
                    # return JsonResponse({ 'query': Items_Serializer[0]})
                    ItemList = list()
                    for a in Items_Serializer:
                        ItemList.append({
                            "id": a['Party_id'],
                            "Name": a['Name'],
                            "Total": a['Total']
                        })
                    log_entry = create_transaction_logNew(request,Items_Serializer,0,'',180,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'PartyItemList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class PartyItemsFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Logindata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 
                CompanyGroupID =Logindata['CompanyGroup'] 
                IsSCMCompany = Logindata['IsSCMCompany']
                
                ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(PartyID,0).split('!')

                if IsSCMCompany == 1:
                    Itemquery= MC_PartyItems.objects.raw(f'''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,
                                                         ifnull(M_Parties.Name,'') PartyName,
                                                         {ItemsGroupJoinsandOrderby[0]},
                                                         M_ItemMappingMaster.MapItem 
                                                         FROM M_Items 
                                                         JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  
                                                         LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s 
                                                         LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id 
                                                         {ItemsGroupJoinsandOrderby[1]}
                                                         left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s 
                                                         WHERE IsSCM=1 AND M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s)
                                                         AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id 
                                                         FROM MC_PartySubParty 
                                                         JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id 
                                                         WHERE (MC_PartySubParty.Party_id=%s OR SubParty_id=%s)) 
                                                         {ItemsGroupJoinsandOrderby[2]}''',([PartyID],[PartyID],[CompanyGroupID],[PartyID],[PartyID]))
                else:
                    # Itemquery= MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,M_ItemMappingMaster.MapItem from M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  left JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s left JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s where M_Items.Company_id =%s order by M_Group.id, MC_SubGroup.id''',([PartyID],[PartyID],[CompanyID]))
                    Itemquery= MC_PartyItems.objects.raw(f'''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,
                                                         ifnull(M_Parties.Name,'') PartyName,
                                                         {ItemsGroupJoinsandOrderby[0]},
                                                         M_ItemMappingMaster.MapItem
                                                         FROM M_Items 
                                                         JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  
                                                         LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s 
                                                         LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id 
                                                         {ItemsGroupJoinsandOrderby[1]} 
                                                         left join M_ItemMappingMaster on M_Items.id=M_ItemMappingMaster.Item_id and M_ItemMappingMaster.Party_id=%s
                                                         WHERE M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s)
                                                         AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id
                                                         WHERE (MC_PartySubParty.Party_id=%s OR SubParty_id=%s))  
                                                         {ItemsGroupJoinsandOrderby[2]} ''',([PartyID],[PartyID],[CompanyGroupID],[PartyID],[PartyID]))
        
                if not Itemquery:
                    log_entry = create_transaction_logNew(request,Logindata,0,'Items Not available',181,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
            
                    Items_Serializer = MC_PartyItemSerializerSingleGet(
                        Itemquery, many=True).data
                    ItemList = list() 
                    for a in Items_Serializer:
                        # GST_HSNCodeMaster = GSTHsnCodeMaster(ItemID=a['id'], EffectiveDate=date.today())
                        # GST = GST_HSNCodeMaster.GetTodaysGstHsnCode()
                        Gst = M_GSTHSNCode.objects.raw(f'''select 1 as id,
                                                       GSTHsnCodeMaster({a['id']},%s,1,0,0)GSTID,
                                                       GSTHsnCodeMaster({a['id']},%s,2,0,0)GSTPercentage 
                                                           ''',[date.today(),date.today()])

                        query=O_BatchWiseLiveStock.objects.filter(Item=a['id'],Party=PartyID,BaseUnitQuantity__gt=0)
                        if query.exists():
                            InStock = True
                        else:
                            InStock=False    
                            
                        ItemList.append({
                            "Item": a['id'],
                            "ItemName": a['Name'],
                            "Party": a['Party_id'], 
                            "PartyName": a['PartyName'],
                            "GroupTypeName": a['GroupTypeName'],
                            "GroupName": a['GroupName'], 
                            "SubGroupName": a['SubGroupName'],
                            "InStock":InStock,
                            "MapItem": a['MapItem'],
                            "GST": int(Gst[0].GSTID) if Gst[0].GSTID is not None else 0, 
                            "GSTID": int(Gst[0].GSTPercentage) if Gst[0].GSTPercentage is not None else 0
                        })
                    log_entry = create_transaction_logNew(request,Logindata,PartyID,'',181,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Logindata,0,'FetchSingleGETItem:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class PartyItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        PartyItems_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyItems_serializer = MC_PartyItemSerializer(data=PartyItems_data, many=True)
            if PartyItems_serializer.is_valid():
                PartyID = PartyItems_serializer.data[0]['Party']
                MC_PartyItem_data = MC_PartyItems.objects.filter(Party=PartyID)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :str(MC_PartyItem_data.query)})
                MC_PartyItem_data.delete()
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :PartyItems_serializer.data[0]['Party']})
                Item = PartyItems_serializer.save()
                LastInsertID = Item[0].id
                
                # Prepare transaction log details
                user = request.user.LoginName
                timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                # ItemDetails = ", ".join([f"ItemID:{item.Item.id}" for item in Item])
                TransactionDetails = f"PartyItem Saved by {user} on {timestamp}"
                
                log_entry = create_transaction_logNew(request,PartyItems_data,PartyID,TransactionDetails,182,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully','TransactionID':LastInsertID, 'Data': []})
            else:
                log_entry = create_transaction_logNew(request,PartyItems_data,PartyID,'PartyItem Save:'+str(PartyItems_serializer.errors),34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyItems_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,PartyItems_data,0,'PartyItem Save:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class ChannelWiseItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Items_data = JSONParser().parse(request)  
        try:
            with transaction.atomic():              
                Items_Serializer = M_ChannelWiseItemsSerializer(data=Items_data, many=True)
                
            if Items_Serializer.is_valid():
                   
                id = Items_Serializer.data[0]['PartyType']
                ChanelWiseItem_data = M_ChannelWiseItems.objects.filter(PartyType_id=id)
                ChanelWiseItem_data.delete()
                ChannelWiseItem = Items_Serializer.save()  
                Q11=M_Settings.objects.filter(id=45).values("DefaultValue")
                PartyTypeID1=str(Q11[0]['DefaultValue'])
                PartyTypeID1_list = [int(x) for x in PartyTypeID1.split(",")]
                
                if id in PartyTypeID1_list:                                     
                   
                    PartysID= M_Parties.objects.filter(PartyType_id=id).values('id')
                    # MC_PartyItem_data = MC_PartyItems.objects.filter(Party__in=PartysID)
                    MC_PartyItems.objects.filter(Party__in=PartysID).delete()                   
                    # MC_PartyItem_data.delete()                                     
                    for item_data in Items_Serializer.data:
                        item_value = item_data['Item']                                                
                        for PartyID in PartysID:  
                            Party=  PartyID['id']                              
                            PartyItems_data=[] 
                            party_item = {"Item": item_value,"Party": Party, "IsAvailableForOrdering": 0}
                            PartyItems_data.append(party_item)
                            # CustomPrint(PartyItems_data)        
                            PartyItems_serializer = MC_PartyItemSerializer(data=PartyItems_data, many=True)
                            if PartyItems_serializer.is_valid():                               
                                Item = PartyItems_serializer.save()                       
                LastInsertID = ChannelWiseItem[0].id
                log_entry = create_transaction_logNew(request,Items_data,0,'PartyTypeID:'+str(id)+','+'TransactionID:'+str(LastInsertID),183,LastInsertID)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ChanelWiseItem Save Successfully','TransactionID':LastInsertID, 'Data': []})
            else:
                log_entry = create_transaction_logNew(request,Items_data,0,'ChannelWiseItemSave:'+str(Items_Serializer.errors),34,0)
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Items_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Items_data,0,'ChannelWiseItemSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class ChannelWiseItemsFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        Itemsdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                UserID = Itemsdata['UserID']   
                RoleID=  Itemsdata['RoleID']  
                CompanyID=Itemsdata['CompanyID']
                PartyTypeID=Itemsdata['PartyTypeID'] 
                CompanyGroupID =Itemsdata['CompanyGroup']
                IsSCMCompany = Itemsdata['IsSCMCompany']

                if IsSCMCompany == 1:
                    Itemquery= M_ChannelWiseItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(M_ChannelWiseItems.PartyType_id,0) PartyType_id,ifnull(M_ChannelWiseItems.IsAvailableForOrdering,0) IsAvailableForOrdering,
ifnull(M_PartyType.Name,'') PartyTypeName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,
ifnull(MC_SubGroup.Name,'') SubGroupName from M_Items left JOIN M_ChannelWiseItems ON M_ChannelWiseItems.item_id=M_Items.id 
AND M_ChannelWiseItems.PartyType_id=%s left JOIN M_PartyType ON M_PartyType.id=M_ChannelWiseItems.PartyType_id 
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id where M_Items.IsSCM=1 and M_Items.Company_id 
in (select id from C_Companies where CompanyGroup_id=%s ORDER BY M_Group.Sequence,MC_SubGroup.Sequence,MC_ItemGroupDetails.ItemSequence)''',([PartyTypeID],[CompanyGroupID]))
                else:
                    Itemquery= M_ChannelWiseItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(M_ChannelWiseItems.PartyType_id,0) PartyType_id,ifnull(M_ChannelWiseItems.IsAvailableForOrdering,0) IsAvailableForOrdering,
ifnull(M_PartyType.Name,'') PartyTypeName,ifnull(M_GroupType.Name,'') GroupTypeName,
ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName from M_Items 
left JOIN M_ChannelWiseItems ON M_ChannelWiseItems.item_id=M_Items.id  AND M_ChannelWiseItems.PartyType_id=%s
left JOIN M_PartyType ON M_PartyType.id=M_ChannelWiseItems.PartyType_id 
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
where M_Items.Company_id =%s 
ORDER BY M_Group.Sequence,MC_SubGroup.Sequence,MC_ItemGroupDetails.ItemSequence''',([PartyTypeID],[CompanyID]))
                CustomPrint(str(Itemquery.query))
                if not Itemquery:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    ItemsList_Serializer = ChanelwiseItemListSerializer(
                        Itemquery, many=True).data
                    ItemList = list()
                    for a in ItemsList_Serializer:
                        ItemID=a['id']
                        # count= MC_PartyItems.objects.filter(Item_id=a['id']).count()
                        Count=MC_PartyItems.objects.raw('''select 1 as id,count(*) cnt from MC_PartyItems join M_Parties on M_Parties.id=MC_PartyItems.Party_id where Item_id=%s and M_Parties.PartyType_id=%s''',(ItemID,PartyTypeID))
                        for row in Count:
                            count = row.cnt
                        if count > 0:
                            Flag = True
                        else:
                            Flag = False 
                              
                        ItemList.append({
                            "Item": a['id'],
                            "ItemName": a['Name'],
                            "PartyType": a['PartyType_id'], 
                            "PartyTypeName": a['PartyTypeName'],
                            "GroupTypeName": a['GroupTypeName'],
                            "GroupName": a['GroupName'], 
                            "SubGroupName": a['SubGroupName'],
                            "InPartyItem":Flag,
                            "IsAvailableForOrdering":a['IsAvailableForOrdering']
                        })
                    log_entry = create_transaction_logNew(request,Itemsdata,0,'',184,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Itemsdata,0,'ChannelWiseItemDetails:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
        
        
class CheckPartiesInChanelWiseItemsList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        ChannelItemsdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Item = ChannelItemsdata['Item']   
                PartyType=  ChannelItemsdata['PartyType']
                
                party_ids = MC_PartyItems.objects.filter(Item_id=Item).values_list('Party_id') 
                PartiesList = M_Parties.objects.filter(id__in=party_ids,PartyType=PartyType)
            
                Parties_Serializer = CheckPartiesImChannelItemSerializer(PartiesList, many=True).data
        
                PartiesList = list()
                for a in Parties_Serializer:
                    PartiesList.append({
                        "id": a['id'],
                        "Name": a['Name']
                    })
                log_entry = create_transaction_logNew(request,ChannelItemsdata,0,'',409,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartiesList})
        except Exception as e:
            log_entry = create_transaction_logNew(request,ChannelItemsdata,0,'PartiesInChanelWiseItemsList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})     
        


class ChanelWiseItemsListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = M_ChannelWiseItems.objects.raw(
                    '''select M_ChannelWiseItems.id,M_PartyType.Name, M_ChannelWiseItems.PartyType_id,count(M_ChannelWiseItems.Item_id)As Total 
From M_ChannelWiseItems join M_PartyType on M_PartyType.id=M_ChannelWiseItems.PartyType_id group by M_ChannelWiseItems.PartyType_id''')
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    Items_Serializer = ChanelwiseItemSerializer(
                        query, many=True).data
                    # return JsonResponse({ 'query': Items_Serializer[0]})
                    ItemList = list()
                    for a in Items_Serializer:
                        ItemList.append({
                            "id": a['PartyType_id'],
                            "Name": a['Name'],
                            "Total": a['Total']
                        
                        })
                    log_entry = create_transaction_logNew(request,Items_Serializer,0,'',410,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            log_entry = create_transaction_logNew(request,0,0,'ChanelWiseItemsList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
