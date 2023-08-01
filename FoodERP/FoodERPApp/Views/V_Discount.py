
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Discount import *

from ..Serializer.S_PriceLists import *
from ..Serializer.S_Items import *
from ..Serializer.S_GeneralMaster import *
from ..Serializer.S_Parties import *
from ..models import *


class DiscountMastergo(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                
                Discountdata = JSONParser().parse(request)
                FromDate = Discountdata['FromDate']
                ToDate = Discountdata['ToDate']
                Party = Discountdata['Party']
                PartyType = Discountdata["PartyType"]
                PriceList = Discountdata["PriceList"]
                Customer = Discountdata["Customer"]

                if not Customer:
                    Discountquery = M_DiscountMaster.objects.raw('''select id,ItemID,ItemName,(case WHEN RecordCount =1 then oldDiscountType else  DiscountType end)DiscountType,(case WHEN RecordCount =1 then oldDiscount else  Discount end)Discount,GroupTypeName, GroupName,SubGroupName,RecordCount from (SELECT M_DiscountMaster.id,M_Items.id ItemID,M_Items.name ItemName,M_DiscountMaster.DiscountType,M_DiscountMaster.Discount,ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName,(SELECT count(*) FROM M_DiscountMaster where M_DiscountMaster.Party_id = %s AND  M_DiscountMaster.Customer_id is null And PartyType_id=%s and PriceList_id=%s and Item_id=M_Items.id and (FromDate between %s and %s or ToDate between %s and %s))RecordCount,(SELECT DiscountType FROM M_DiscountMaster where M_DiscountMaster.Party_id = %s AND  M_DiscountMaster.Customer_id is null And PartyType_id=%s and PriceList_id=%s and Item_id=M_Items.id and (FromDate between %s and %s or ToDate between %s and %s))oldDiscountType, (SELECT Discount FROM M_DiscountMaster where M_DiscountMaster.Party_id = %s AND  M_DiscountMaster.Customer_id is null And PartyType_id=%s and PriceList_id=%s and Item_id=M_Items.id and (FromDate between %s and %s or ToDate between %s and %s))oldDiscount FROM M_Items LEFT JOIN MC_PartyItems ON Item_id=M_Items.ID AND Party_id = %s LEFT JOIN  M_DiscountMaster ON M_DiscountMaster.Item_id=M_Items.ID AND M_DiscountMaster.Party_id = %s and  M_DiscountMaster.Customer_id is null AND PartyType_id = %s and PriceList_id=%s AND FromDate = %s AND ToDate = %s left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id WHERE MC_PartyItems.Item_id IS NOT NULL ORDER BY M_Items.Sequence)a''', ([Party], [PartyType], [PriceList], [FromDate], [ToDate], [FromDate], [ToDate], [Party], [PartyType], [PriceList], [FromDate], [ToDate], [FromDate], [ToDate], [Party], [PartyType], [PriceList], [FromDate], [ToDate], [FromDate], [ToDate], [Party], [Party], [PartyType], [PriceList], [FromDate], [ToDate]))

                else:
                    Discountquery = M_DiscountMaster.objects.raw('''select id,ItemID,ItemName,
                    (case WHEN RecordCount =1 then oldDiscountType else  DiscountType end)DiscountType,
                    (case WHEN RecordCount =1 then oldDiscount else  Discount end)Discount,
                    GroupTypeName, GroupName,SubGroupName,RecordCount from (SELECT M_DiscountMaster.id,M_Items.id ItemID,M_Items.name ItemName,M_DiscountMaster.DiscountType,M_DiscountMaster.Discount  ,
                    ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
                    ,(SELECT count(*) FROM M_DiscountMaster where M_DiscountMaster.Party_id = %s AND  M_DiscountMaster.Customer_id = %s And PartyType_id=%s and PriceList_id=%s and Item_id=M_Items.id
                   
                    and (FromDate between %s and %s or ToDate between %s and %s))RecordCount,
                    (SELECT DiscountType FROM M_DiscountMaster where M_DiscountMaster.Party_id = %s AND  M_DiscountMaster.Customer_id is null And PartyType_id=%s and PriceList_id=%s and Item_id=M_Items.id
                    
                    and (FromDate between %s and %s or ToDate between %s and %s))oldDiscountType,
                    (SELECT Discount FROM M_DiscountMaster where M_DiscountMaster.Party_id = %s AND  M_DiscountMaster.Customer_id is null And PartyType_id=%s and PriceList_id=%s and Item_id=M_Items.id
                   
                    and (FromDate between %s and %s or ToDate between %s and %s))oldDiscount
                    FROM M_Items
                    
                    LEFT JOIN MC_PartyItems ON Item_id=M_Items.ID AND Party_id = %s
                    LEFT JOIN  M_DiscountMaster ON M_DiscountMaster.Item_id=M_Items.ID
                    AND M_DiscountMaster.Party_id = %s and  M_DiscountMaster.Customer_id = %s
                    AND PartyType_id = %s and PriceList_id=%s
                    AND FromDate = %s AND ToDate = %s
                    left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
                    left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
                    left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
                    left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                    WHERE MC_PartyItems.Item_id IS NOT NULL
                    ORDER BY M_Items.Sequence)a''', ([Party], [Customer], [PartyType], [PriceList], [FromDate], [ToDate], [FromDate],  [ToDate], [Party], [PartyType], [PriceList], [FromDate], [ToDate], [FromDate], [ToDate], [Party],  [PartyType], [PriceList], [FromDate], [ToDate], [FromDate], [ToDate], [Party],  [Party], [Customer], [PartyType], [PriceList], [FromDate], [ToDate]))
                if Discountquery:
                    Discountdata = DiscountMasterSerializer(Discountquery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Discountdata})
                else:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data':''})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DiscountMasterSaveView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                DiscountMaster_data = JSONParser().parse(request)
                Discount_serializer = DiscountSerializer(
                    data=DiscountMaster_data, many=True)
                if Discount_serializer.is_valid():
                    Discount_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Discount Master Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Discount_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DiscountMasterFilter(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Discountdata = JSONParser().parse(request)
                FromDate = Discountdata['FromDate']
                ToDate = Discountdata['ToDate']
                Party = Discountdata['Party']
                today = date.today()

                if FromDate:

                    Discountquery = M_DiscountMaster.objects.raw('''SELECT M_DiscountMaster.id, M_DiscountMaster.FromDate, M_DiscountMaster.ToDate, M_Parties.Name CustomerName, M_Items.name ItemName, M_DiscountMaster.DiscountType, M_DiscountMaster.Discount,M_PartyType.Name Partytype,M_PriceList.Name PriceListName,
M_DiscountMaster.CreatedBy,M_DiscountMaster.CreatedOn
FROM M_DiscountMaster 

LEFT JOIN M_Parties ON M_Parties.id = M_DiscountMaster.Customer_id 
JOIN M_Items ON M_Items.id = M_DiscountMaster.Item_id 
JOIN M_PartyType ON M_PartyType.id=M_DiscountMaster.PartyType_id
join M_PriceList on M_PriceList.id=M_DiscountMaster.PriceList_id
WHERE M_DiscountMaster.Party_id= %s and M_DiscountMaster.FromDate between %s and %s
ORDER BY M_DiscountMaster.id DESC''', ([Party], [FromDate], [ToDate]))
                else:
                    Discountquery = M_DiscountMaster.objects.raw('''SELECT M_DiscountMaster.id, M_DiscountMaster.FromDate, M_DiscountMaster.ToDate, M_Parties.Name CustomerName, M_Items.name ItemName, M_DiscountMaster.DiscountType, M_DiscountMaster.Discount,M_PartyType.Name Partytype,M_PriceList.Name PriceListName,
M_DiscountMaster.CreatedBy,M_DiscountMaster.CreatedOn
FROM M_DiscountMaster 

LEFT JOIN M_Parties ON M_Parties.ID = M_DiscountMaster.Customer_id 
JOIN M_Items ON M_Items.id = M_DiscountMaster.Item_id 
JOIN M_PartyType ON M_PartyType.id=M_DiscountMaster.PartyType_id
join M_PriceList on M_PriceList.id=M_DiscountMaster.PriceList_id
WHERE M_DiscountMaster.Party_id= %s and %s >= M_DiscountMaster.FromDate and %s <= M_DiscountMaster.ToDate
ORDER BY M_DiscountMaster.id DESC''', ([Party], [today], [today]))

                if Discountquery:
                    Discountdata = DiscountMasterFilterSerializer(
                        Discountquery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Discountdata})
                else:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Record Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DiscountPartyTypeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                q0 = MC_PartySubParty.objects.filter(
                    Party=id).values("SubParty")
                query = M_Parties.objects.filter(
                    id__in=q0).distinct().values('PartyType')
                query2 = M_PartyType.objects.filter(id__in=query)
                if not query2:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    PartyTypes_Serializer = PartyTypeSerializer(
                        query2, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': PartyTypes_Serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DiscountCustomerView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, Party=0, PartyType=0, PriceList=0):
        try:
            with transaction.atomic():
                q0 = MC_PartySubParty.objects.filter(
                    Party=Party).values("SubParty")
                query = M_Parties.objects.filter(id__in=q0).filter(
                    PartyType=PartyType, PriceList=PriceList)
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
                else:
                    M_Parties_serializer = PartiesSerializer(
                        query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': M_Parties_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
