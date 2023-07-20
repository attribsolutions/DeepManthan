
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

                Discountquery = M_DiscountMaster.objects.raw('''SELECT M_DiscountMaster.id,M_Items.id ItemID,M_Items.name ItemName,M_DiscountMaster.DiscountType,M_DiscountMaster.Discount  ,
ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
FROM M_Items
LEFT JOIN MC_PartyItems ON Item_id=M_Items.ID AND Party_id = %s
LEFT JOIN  M_DiscountMaster ON M_DiscountMaster.Item_id=M_Items.ID 
AND M_DiscountMaster.Party_id = %s 
AND FromDate = %s AND ToDate = %s 
AND PartyType_id = %s and PriceList_id=%s
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
WHERE MC_PartyItems.Item_id IS NOT NULL							
ORDER BY M_Items.Sequence''', ([Party], [Party], [FromDate], [ToDate], [PartyType], [PriceList]))
                print(Discountquery.query)
                Discountdata = DiscountMasterSerializer(
                    Discountquery, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Discountdata})
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
                Discount_serializer = DiscountSerializer(data=DiscountMaster_data, many=True)
                if Discount_serializer.is_valid():
                    Discount_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Discount Master Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Discount_serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


