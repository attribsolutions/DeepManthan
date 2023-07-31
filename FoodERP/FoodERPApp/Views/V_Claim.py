
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
                Mode =Orderdata['Mode']

                if Mode == 2:
                   
                    Q1=M_Parties.objects.raw('''select M_Parties.id ,M_Parties.Name PartyName,M_Parties.MobileNo, MC_PartyAddress.Address ,MC_PartyAddress.FSSAINo,M_Parties.GSTIN 
from M_Parties 
join MC_PartyAddress on M_Parties.id=MC_PartyAddress.Party_id and IsDefault=1
where Party_id = %s''',([Party]))
                    print(Q1)
                    q0 = T_PurchaseReturn.objects.raw('''SELECT 1 as id,T_PurchaseReturn.ReturnDate,T_PurchaseReturn.FullReturnNumber,M_Parties.Name CustomerName,M_Items.Name ItemName,
MRPValue MRP,Quantity,GSTPercentage GST,Rate,
 Amount, CGST, SGST, ApprovedQuantity,  ifnull(Discount,0) Discount, ifnull(DiscountAmount,0) DiscountAmount, DiscountType,BasicAmount TaxableAmount
FROM T_PurchaseReturn
join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id

join M_Parties  on M_Parties.id=T_PurchaseReturn.Customer_id

join M_Items on M_Items.id=TC_PurchaseReturnItems.Item_id

where IsApproved=1 and  T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Party_id=%s Order By GSTPercentage  ''',([FromDate],[ToDate],[Party]))
                else:
                    Q1=M_Parties.objects.raw('''select M_Parties.id ,M_Parties.Name PartyName,M_Parties.MobileNo, MC_PartyAddress.Address ,MC_PartyAddress.FSSAINo,M_Parties.GSTIN 
from M_Parties 
join MC_PartyAddress on M_Parties.id=MC_PartyAddress.Party_id and IsDefault=1
where Party_id = %s''',([Party]))
                    print(Q1)
                    q0 = T_PurchaseReturn.objects.raw('''SELECT 1 as id,'' ReturnDate,'' FullReturnNumber,'' CustomerName,ItemName,
MRP,Quantity,GST,Rate,TaxableAmount,
 Amount, CGST, SGST, ApprovedQuantity,  Discount, DiscountAmount, DiscountType from
(SELECT M_Items.id,M_Items.Name ItemName,sum(BasicAmount)TaxableAmount,sum(MRPValue)MRP,sum(Quantity)Quantity,GSTPercentage GST,Rate,
 sum(Amount)Amount, sum(CGST)CGST,sum(SGST)SGST, sum(ApprovedQuantity)ApprovedQuantity,  ifnull(sum(Discount),0)Discount, ifnull(sum(DiscountAmount),0)DiscountAmount,DiscountType

FROM T_PurchaseReturn
join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id

join M_Parties  on M_Parties.id=T_PurchaseReturn.Customer_id

join M_Items on M_Items.id=TC_PurchaseReturnItems.Item_id

where IsApproved=1 and  T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Party_id=%s group by Item_id,GSTPercentage,Rate Order By GSTPercentage )j ''',([FromDate],[ToDate],[Party]))
                
                
                
                
                
                
                
                
                
                
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

class ItemWiseClaimSummaryView(CreateAPIView):
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

where IsApproved=1 and  T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Party_id=%s group by TC_PurchaseReturnItems.Item_id  order by GSTPercentage  ''',([FromDate],[ToDate],[Party]))
                
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



class MasterClaimView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party  = Orderdata['Party']
                
                q0=MC_ReturnReasonwiseMasterClaim.objects.filter(FromDate=FromDate,ToDate=ToDate,Party_id=Party)
                if(q0.count() == 0):
                    q1=M_PartyType.objects.filter(IsSCM=1,Company_id=3).values("id")
                    for i in q1:
                        PartyType=i["id"]
                        print(PartyType)
                        claimREasonwise=MC_ReturnReasonwiseMasterClaim.objects.raw('''select 1 as id, ItemReason_id,PA PrimaryAmount,SA secondaryAmount,ReturnAmount ,(PA-ReturnAmount)NetPurchaseValue, 
    (CASE WHEN ItemReason_id=54 THEN ((PA-ReturnAmount)*0.01) ELSE 0 END)Budget,ReturnAmount ClaimAmount,
    (ReturnAmount/(PA-ReturnAmount))ClaimAgainstNetSale
    from
    (SELECT ItemReason_id,sum(TC_PurchaseReturnItems.Amount)ReturnAmount,
    (select sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices 
    join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
    where InvoiceDate between %s and %sand Customer_id=%s )PA,
    (select sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices 
    join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
    where InvoiceDate between %s and %sand Party_id=%s )SA
    FROM T_PurchaseReturn
    join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id
    join M_Parties on M_Parties.id=T_PurchaseReturn.Customer_id
    where IsApproved=1 and M_Parties.PartyType_id=%s  and  T_PurchaseReturn.ReturnDate between %s and %sand Party_id=%s group by ItemReason_id)p ''',
    ([FromDate],[ToDate], [Party],[FromDate],[ToDate], [Party],[PartyType],[FromDate],[ToDate], [Party]))
                    
                    
                        serializer=MasterclaimReasonReportSerializer(claimREasonwise, many=True).data
                        # print(serializer)
                        for a in serializer:
                        
                            stock=MC_ReturnReasonwiseMasterClaim(FromDate=FromDate,ToDate=ToDate,PrimaryAmount=a["PrimaryAmount"], SecondaryAmount=a["secondaryAmount"], ReturnAmount=a["ReturnAmount"], NetSaleValue=a["NetPurchaseValue"], Budget=a["Budget"], ClaimAmount=a["ReturnAmount"], ClaimAgainstNetSale=a["ClaimAgainstNetSale"], ItemReason_id=a["ItemReason_id"], PartyType=PartyType, Party_id=Party,CreatedBy=0)
                            stock.save()
                        
                        
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    StockProcessQuery = O_DateWiseLiveStock.objects.raw('''select * from (select 1 as id, I.Item_id,ifnull(PA.PrimaryAmount,0)PrimaryAmount,ifnull(SA.secondaryAmount,0)secondaryAmount,ifnull(RA.ReturnAmount,0)ReturnAmount,
                        ifnull((PA.PrimaryAmount-RA.ReturnAmount),0)NetPurchaseValue ,ifnull(((PA.PrimaryAmount-RA.ReturnAmount)*0.01),0)Budget,ifnull((RA.ReturnAmount/(PA.PrimaryAmount-RA.ReturnAmount)),0)ClaimAgainstNetSale
    from
    (Select Item_id from MC_PartyItems  where Party_id=%s)I
    left join


    (select TC_InvoiceItems.Item_id,sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
    where InvoiceDate between %s and %s and Customer_id=%s group by Item_id)PA
    on I.Item_id=PA.Item_id
    left join 

    (select TC_InvoiceItems.Item_id,sum(TC_InvoiceItems.Amount)secondaryAmount from T_Invoices 
    join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
    join M_Parties on M_Parties.id=T_Invoices.Customer_id
    where  InvoiceDate between %s and %s and Party_id=%s group by Item_id)SA
    on I.Item_id=SA.Item_id
    left join 


    (SELECT TC_PurchaseReturnItems.Item_id,sum(TC_PurchaseReturnItems.Amount)ReturnAmount
    FROM T_PurchaseReturn
    join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id
    join M_Parties on M_Parties.id=T_PurchaseReturn.Customer_id
    where IsApproved=1  and  T_PurchaseReturn.ReturnDate between %s and %s and Party_id=%s group by Item_id)RA

    on  I.Item_id=RA.Item_id)aaa where PrimaryAmount !=0 OR secondaryAmount !=0 OR ReturnAmount !=0
    ''',
    ([Party], [FromDate],[ToDate], [Party],[FromDate],[ToDate], [Party],[FromDate],[ToDate], [Party]))
                        
                    print(StockProcessQuery)
                    serializer=MasterclaimReportSerializer(StockProcessQuery, many=True).data
                        # print(serializer)
                    for a in serializer:
                        
                        stock=M_MasterClaim(FromDate=FromDate,ToDate=ToDate,PrimaryAmount=a["PrimaryAmount"], SecondaryAmount=a["secondaryAmount"], ReturnAmount=a["ReturnAmount"], NetSaleValue=a["NetPurchaseValue"], Budget=a["Budget"], ClaimAmount=a["ReturnAmount"], ClaimAgainstNetSale=a["ClaimAgainstNetSale"], Item_id=a["Item_id"], Customer_id=1, Party_id=Party,CreatedBy=0)
                        stock.save()
                    

                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'Master Claim Create Successfully', 'Data':[]})
                else:
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'Master Claim Already Created...!', 'Data':[]})
                


        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                    


class MasterClaimPrintView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party  = Orderdata['Party']
                MasterClaimData=list()
                ReasonwiseMasterClaimList=list()
                q1=M_PartyType.objects.filter(IsSCM=1,Company_id=3).values("id","Name")
                for i in q1:
                    PartyTypeID=i["id"]
                    PartyTypeName=i["Name"]
                    printReasonwisequery=MC_ReturnReasonwiseMasterClaim.objects.raw(''' SELECT 1 as id, M_GeneralMaster.Name ItemReasonName, PrimaryAmount, SecondaryAmount, ReturnAmount, NetSaleValue, 
Budget, ClaimAmount, ClaimAgainstNetSale
 FROM MC_ReturnReasonwiseMasterClaim 
join M_GeneralMaster on M_GeneralMaster.id=MC_ReturnReasonwiseMasterClaim.ItemReason_id 
where FromDate=%s and ToDate=%s and Party_id=%s and PartyType=%s

order by M_GeneralMaster.id
''',([FromDate],[ToDate],[Party],[PartyTypeID]))
                    ReasonwiseMasterClaim=ReasonwiseMasterClaimSerializer(printReasonwisequery, many=True).data
                    if ReasonwiseMasterClaim:
                        ReasonwiseMasterClaimList.append({
                            PartyTypeName +'Claim' : ReasonwiseMasterClaim

                        })
                
                
                
                printProductwisequery=M_MasterClaim.objects.raw('''SELECT 1 as id,  M_Group.Name Product, sum(PrimaryAmount)PrimaryAmount, sum(SecondaryAmount)SecondaryAmount, sum(ReturnAmount)ReturnAmount, sum(NetSaleValue)NetSaleValue, 
sum(Budget)Budget, sum(ClaimAmount)ClaimAmount, sum(ClaimAgainstNetSale)ClaimAgainstNetSale
FROM M_MasterClaim
left join M_Items on M_Items.id=M_MasterClaim.Item_id
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 



 where FromDate=%s and ToDate=%s and Party_id=%s
 group by M_Group.id''',([FromDate],[ToDate],[Party]))
                ProductwiseMasterClaim=ProductwiseMasterClaimSerializer(printProductwisequery, many=True).data
                MasterClaimData.append({
                        "ReasonwiseMasterClaim": ReasonwiseMasterClaimList,
                        "ProductwiseBudgetReport": ProductwiseMasterClaim          
                    })
        
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message':'', 'Data':MasterClaimData[0]})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                  