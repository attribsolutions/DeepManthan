
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Claim import *
from ..models import *


class ClaimSummaryView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party  = Orderdata['Party']
                

                
                   
                Q1=M_Parties.objects.raw('''select M_Parties.id ,M_Parties.Name PartyName,M_Parties.MobileNo, MC_PartyAddress.Address ,MC_PartyAddress.FSSAINo,M_Parties.GSTIN 
from M_Parties 
join MC_PartyAddress on M_Parties.id=MC_PartyAddress.Party_id and IsDefault=1
where Party_id = %s''',([Party]))
                print(Q1)
                q0 = T_PurchaseReturn.objects.raw('''SELECT 1 as id,T_PurchaseReturn.ReturnDate,T_PurchaseReturn.FullReturnNumber,M_Parties.Name CustomerName,M_Items.Name ItemName,
MRPValue MRP,Quantity,GSTPercentage GST,Rate,
 Amount, CGST, SGST, ApprovedQuantity,  Discount, DiscountAmount, DiscountType
FROM T_PurchaseReturn
join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id

join M_Parties  on M_Parties.id=T_PurchaseReturn.Customer_id

join M_Items on M_Items.id=TC_PurchaseReturnItems.Item_id

where IsApproved=1 and  T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Party_id=%s  ''',([FromDate],[ToDate],[Party]))
                
                print(q0.query)
                if q0:
                    ClaimSummaryData = list()
                    M_Parties_serializer =PartyDetailSerializer(Q1,many=True).data
                    ClaimSummary_serializer = ClaimSummarySerializer(q0, many=True).data
                    # M_Parties_serializer.append({  
                    #           "ClaimSummaryItemDetails": ClaimSummary_serializer
                    #           })
                    ClaimSummaryData.append({
                        "PartyDetails": M_Parties_serializer[0],
                        "ClaimSummaryItemDetails": ClaimSummary_serializer          
                    })
                    

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ClaimSummaryData[0]})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})