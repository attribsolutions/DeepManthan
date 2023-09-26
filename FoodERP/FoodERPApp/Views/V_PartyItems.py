from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyItems import *
from ..models import *



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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class PartyItemsFilterView(CreateAPIView):
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
                CompanyGroupID =Logindata['CompanyGroup'] 
                IsSCMCompany = Logindata['IsSCMCompany']

                if IsSCMCompany == 1:
                    Itemquery= MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName FROM M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  LEFT JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s LEFT JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id WHERE IsSCM=1 AND M_Items.Company_id IN (select id from C_Companies where CompanyGroup_id=%s) AND M_ChannelWiseItems.PartyType_id IN (SELECT distinct M_Parties.PartyType_id FROM MC_PartySubParty JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id WHERE (MC_PartySubParty.Party_id=%s OR SubParty_id=%s))  order by M_Group.id, MC_SubGroup.id ''',([PartyID],[CompanyGroupID],[PartyID],[PartyID]))
                else:
                    Itemquery= MC_PartyItems.objects.raw('''SELECT distinct M_Items.id,M_Items.Name,ifnull(MC_PartyItems.Party_id,0) Party_id,ifnull(M_Parties.Name,'') PartyName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName from M_Items JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.id  left JOIN MC_PartyItems ON MC_PartyItems.Item_id=M_ChannelWiseItems.Item_id AND MC_PartyItems.Party_id=%s left JOIN M_Parties ON M_Parties.id=MC_PartyItems.Party_id left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id where M_Items.Company_id =%s order by M_Group.id, MC_SubGroup.id''',([PartyID],[CompanyID]))
                
                if not Itemquery:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
            
                    Items_Serializer = MC_PartyItemSerializerSingleGet(
                        Itemquery, many=True).data
                    ItemList = list()
                    for a in Items_Serializer:
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
                            "InStock":InStock
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class PartyItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                PartyItems_data = JSONParser().parse(request)
                PartyItems_serializer = MC_PartyItemSerializer(data=PartyItems_data, many=True)
            if PartyItems_serializer.is_valid():
                id = PartyItems_serializer.data[0]['Party']
                MC_PartyItem_data = MC_PartyItems.objects.filter(Party=id)
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :str(MC_PartyItem_data.query)})
                MC_PartyItem_data.delete()
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data' :PartyItems_serializer.data[0]['Party']})
                PartyItems_serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyItems Save Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyItems_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class ChannelWiseItemsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Items_data = JSONParser().parse(request)
                Items_Serializer = M_ChannelWiseItemsSerializer(data=Items_data, many=True)
            if Items_Serializer.is_valid():
                id = Items_Serializer.data[0]['PartyType']
                ChanelWiseItem_data = M_ChannelWiseItems.objects.filter(PartyType_id=id)
                ChanelWiseItem_data.delete()
                Items_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'ChanelWiseItem Save Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Items_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class ChannelWiseItemsFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Itemsdata = JSONParser().parse(request)
                UserID = Itemsdata['UserID']   
                RoleID=  Itemsdata['RoleID']  
                CompanyID=Itemsdata['CompanyID']
                PartyTypeID=Itemsdata['PartyTypeID'] 
                CompanyGroupID =Itemsdata['CompanyGroup']
                IsSCMCompany = Itemsdata['IsSCMCompany']

                if IsSCMCompany == 1:
                    Itemquery= M_ChannelWiseItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(M_ChannelWiseItems.PartyType_id,0) PartyType_id,
ifnull(M_PartyType.Name,'') PartyTypeName,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,
ifnull(MC_SubGroup.Name,'') SubGroupName from M_Items left JOIN M_ChannelWiseItems ON M_ChannelWiseItems.item_id=M_Items.id 
AND M_ChannelWiseItems.PartyType_id=%s left JOIN M_PartyType ON M_PartyType.id=M_ChannelWiseItems.PartyType_id 
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id left JOIN M_GroupType 
ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id left JOIN M_Group
ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup 
ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id where M_Items.IsSCM=1 and M_Items.Company_id 
in (select id from C_Companies where CompanyGroup_id=%s  order by M_Group.id, MC_SubGroup.id)''',([PartyTypeID],[CompanyGroupID]))
                else:
                    Itemquery= M_ChannelWiseItems.objects.raw('''SELECT M_Items.id,M_Items.Name,ifnull(M_ChannelWiseItems.PartyType_id,0) PartyType_id,
ifnull(M_PartyType.Name,'') PartyTypeName,ifnull(M_GroupType.Name,'') GroupTypeName,
ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName from M_Items 
left JOIN M_ChannelWiseItems ON M_ChannelWiseItems.item_id=M_Items.id AND M_ChannelWiseItems.PartyType_id=%s
left JOIN M_PartyType ON M_PartyType.id=M_ChannelWiseItems.PartyType_id left JOIN MC_ItemGroupDetails 
ON MC_ItemGroupDetails.Item_id = M_Items.id left JOIN M_GroupType 
ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id left JOIN M_Group 
ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup 
ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id where M_Items.Company_id =%s 
order by M_Group.id, MC_SubGroup.id''',([PartyTypeID],[CompanyID]))
                # print(str(Itemquery.query))
                if not Itemquery:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Items Not available', 'Data': []})
                else:
                    ItemsList_Serializer = ChanelwiseItemListSerializer(
                        Itemquery, many=True).data
                    ItemList = list()
                    for a in ItemsList_Serializer:
                        
                        count= MC_PartyItems.objects.filter(Item_id=a['id']).count()
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
                            "InPartyItem":Flag
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
        
        
class CheckPartiesInChanelWiseItemsList(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                ChannelItemsdata = JSONParser().parse(request)
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
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartiesList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})     
        


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
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemList})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
