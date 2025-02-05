
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser,MultiPartParser,FormParser
from ..Serializer.S_Claim import *
from ..models import *
from datetime import date
import base64
from io import BytesIO
from PIL import Image
from .V_CommFunction import *
import calendar


class ClaimSummaryView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                Mode = Orderdata['Mode']

                if Mode == 2:  # Customer Wise return Summury

                    Q1 = M_Parties.objects.raw('''select M_Parties.id ,M_Parties.Name PartyName,M_Parties.MobileNo, MC_PartyAddress.Address ,MC_PartyAddress.FSSAINo,M_Parties.GSTIN 
from M_Parties 
join MC_PartyAddress on M_Parties.id=MC_PartyAddress.Party_id and IsDefault=1
where Party_id = %s''', ([Party]))

                    q0 = T_PurchaseReturn.objects.raw('''SELECT 1 as id,T_PurchaseReturn.ReturnDate,T_PurchaseReturn.FullReturnNumber,M_Parties.Name CustomerName,M_Items.Name ItemName,
MRPValue MRP,Quantity,ApprovedGSTPercentage GST,ApprovedRate Rate,
 ApprovedAmount Amount, ApprovedCGST CGST, ApprovedSGST SGST, ApprovedByCompany ApprovedQuantity,  ifnull(Discount,0) Discount, ifnull(ApprovedDiscountAmount,0) DiscountAmount, DiscountType,ApprovedBasicAmount TaxableAmount
FROM T_PurchaseReturn
join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id

join M_Parties  on M_Parties.id=T_PurchaseReturn.Customer_id

join M_Items on M_Items.id=TC_PurchaseReturnItems.Item_id

 where IsApproved=1 and 
T_PurchaseReturn.id in (SELECT TC_PurchaseReturnReferences.SubReturn_id FROM T_PurchaseReturn join TC_PurchaseReturnReferences on T_PurchaseReturn.id=TC_PurchaseReturnReferences.PurchaseReturn_id
where T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Customer_id=%s ) Order By GSTPercentage''', ([FromDate], [ToDate], [Party]))
                else:   # Return Item Summury
                    Q1 = M_Parties.objects.raw('''select M_Parties.id ,M_Parties.Name PartyName,M_Parties.MobileNo, MC_PartyAddress.Address ,MC_PartyAddress.FSSAINo,M_Parties.GSTIN 
from M_Parties 
join MC_PartyAddress on M_Parties.id=MC_PartyAddress.Party_id and IsDefault=1
where Party_id = %s''', ([Party]))

                    q0 = T_PurchaseReturn.objects.raw('''SELECT 1 as id,'' ReturnDate, FullReturnNumber,'' CustomerName,ItemName,
MRP,Quantity,GST,Rate,TaxableAmount,
 Amount, CGST, SGST, ApprovedQuantity,  Discount, DiscountAmount, DiscountType 
 from
(SELECT FullReturnNumber, M_Items.id,M_Items.Name ItemName,sum(ApprovedBasicAmount)TaxableAmount,(MRPValue)MRP,sum(Quantity)Quantity,ApprovedGSTPercentage GST,ApprovedRate Rate,
 sum(ApprovedAmount)Amount, sum(ApprovedCGST)CGST,sum(ApprovedSGST)SGST, sum(ApprovedByCompany)ApprovedQuantity,  ifnull(Discount,0)Discount, ifnull(sum(ApprovedDiscountAmount),0)DiscountAmount,DiscountType

FROM T_PurchaseReturn
join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id

join M_Parties  on M_Parties.id=T_PurchaseReturn.Customer_id

join M_Items on M_Items.id=TC_PurchaseReturnItems.Item_id

where IsApproved=1 and  T_PurchaseReturn.ReturnDate between %s and %s and (T_PurchaseReturn.Customer_id=%s ) group by FullReturnNumber, Item_id,ApprovedGSTPercentage,ApprovedRate,MRPValue ,Discount,DiscountType Order By ApprovedGSTPercentage desc ,Item_id desc )j ''', ([FromDate], [ToDate], [Party]))

                if q0:
                    ClaimSummaryData = list()
                    M_Parties_serializer = PartyDetailSerializer(
                        Q1, many=True).data
                    for a in M_Parties_serializer:
                            Full_Return_Numbers = T_PurchaseReturn.objects.filter( IsApproved=1,ReturnDate__range=[FromDate, ToDate],Customer=Party ).values_list('FullReturnNumber', flat=True)
                            a['FullReturnNumbers'] = ', '.join(Full_Return_Numbers)
                    ClaimSummary_serializer = ClaimSummarySerializer(
                        q0, many=True).data
                    
                    # M_Parties_serializer.append({
                    #           "ClaimSummaryItemDetails": ClaimSummary_serializer
                    #           })
                    ClaimSummaryData.append({
                        "PartyDetails": M_Parties_serializer[0],
                        "ClaimSummaryItemDetails": ClaimSummary_serializer
                    })
                    log_entry = create_transaction_logNew(request, Orderdata,Party,'From:'+str(FromDate)+'To:'+str(ToDate),254,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ClaimSummaryData[0]})
                else:
                    log_entry = create_transaction_logNew(request, Orderdata,Party,'ClaimSummary Not available',254,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Records Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata,0,'ClaimSummary:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class MasterClaimView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():

                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']

                q = M_Claim.objects.filter(
                    FromDate=FromDate, ToDate=ToDate, Customer_id=Party)
                # CustomPrint(q.query)
                # CustomPrint(q)
                q.delete()
                q0 = MC_ReturnReasonwiseMasterClaim.objects.filter(
                    FromDate=FromDate, ToDate=ToDate, Party_id=Party)
                q0.delete()
                q2 = M_MasterClaim.objects.filter(
                    FromDate=FromDate, ToDate=ToDate, Party_id=Party)
                q2.delete()
                log_entry = create_transaction_logNew(request, Orderdata,Party,'From:'+str(FromDate)+','+'To:'+str(ToDate)+','+'DeletedClaimID:'+str(id),256,0,FromDate,ToDate,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Claim Deleted Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata,0,'DeleteClaim:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                PartyID = Orderdata['Party']
                LoginParty = Orderdata['LoginParty']
                
                q11=M_Parties.objects.raw(''' select * from 
 (select 1 as id,M_Parties.id PartyID ,M_Parties.Name from M_Parties join MC_PartySubParty on M_Parties.id=MC_PartySubParty.SubParty_id
 where MC_PartySubParty.Party_id=%s and M_Parties.PartyType_id in(9,10,15) 
 union
 select 2 as id,M_Parties.id PartyID ,M_Parties.Name from M_Parties where id=%s)a 
 left join
 (select count(*)returncnt ,Customer_id from T_PurchaseReturn where T_PurchaseReturn.ReturnDate between %s and %s group by Customer_id)b
 on partyID=b.Customer_id  where returncnt >0 order by id ''',([PartyID],[PartyID],[FromDate],[ToDate]))
                
                for row in q11:
                    Party = row.PartyID
                    PartyName=row.Name
                    # CustomPrint(PartyName)
                
                
                    q10 = T_PurchaseReturn.objects.raw('''SELECT 1 as id,count(*) cnt
        FROM T_PurchaseReturn
        join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id
        where IsApproved=1   
        and Customer_id=%s and FinalApprovalDate is null and ApprovedQuantity  > 0 and T_PurchaseReturn.id in(SELECT TC_PurchaseReturnReferences.SubReturn_id
        FROM T_PurchaseReturn
        join TC_PurchaseReturnReferences on TC_PurchaseReturnReferences.PurchaseReturn_id=T_PurchaseReturn.id
        where T_PurchaseReturn.ReturnDate between %s and %s 
        and Customer_id=%s)''', ( [Party],[FromDate], [ToDate], [PartyID]))
                    # CustomPrint(q10.query)
                    for row in q10:
                        count = row.cnt

                    if count != 0:
                        log_entry = create_transaction_logNew(request, Orderdata,PartyID,'',260,0,FromDate,ToDate,0)

                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': PartyName+ ' Final Approval is Remaining...!', 'Data': []})

                    else:

                        q0 = MC_ReturnReasonwiseMasterClaim.objects.filter(
                            FromDate=FromDate, ToDate=ToDate, Party_id=Party)
                        if(q0.count() == 0):

                            Claim = M_Claim(Date=date.today(), FromDate=FromDate, ToDate=ToDate,
                                            Customer_id=Party, Party_id=LoginParty, CreatedBy=0)
                            Claim.save()
                            ClaimID = Claim.id

                            # q1 = M_Settings.objects.raw('''SELECT id,DefaultValue FROM M_Settings where id=25''')
                            q1 = M_Settings.objects.filter(
                                id=25).values("DefaultValue")
                            # CustomPrint(q1)
                            value = q1[0]['DefaultValue']
                            # CustomPrint(value)
                            id = 0
                            PartyType_list = value.split(":")
                            for row in PartyType_list:
                                # CustomPrint('aaaaaaaaaaaaaaaaaaaaaaaaaaa')
                                # CustomPrint(row)

                                # q1 = M_PartyType.objects.filter(
                                #     IsSCM=1, Company_id=3).values("id")
                                # for i in q1:

                                PartyType = row.split(",")
                                # CustomPrint('----------',id)
                                if id == 0:
                                    PartyTypeID = 11
                                else:
                                    PartyTypeID = 15
                                # CustomPrint(PartyType)
                                # CustomPrint('-----------')
                                # CustomPrint(PartyTypeID)
    # ===========================================================================================================================================

                                claimREasonwise = MC_ReturnReasonwiseMasterClaim.objects.raw('''select 1 as id, ItemReason_id,IFNULL(PA,0) PrimaryAmount,IFNULL(SA,0) secondaryAmount,IFNULL(ReturnAmount,0)ReturnAmount ,
                                IFNULL((PA-ReturnAmount),0)NetPurchaseValue, 
            (CASE WHEN ItemReason_id=54 THEN IFNULL(((PA)*0.01),0) ELSE 0 END)Budget,IFNULL(ReturnAmount,0) ClaimAmount,
            IFNULL((ReturnAmount/PA)*100,0)ClaimAgainstNetSale
            from
            (SELECT TC_PurchaseReturnItems.ItemReason_id,sum(TC_PurchaseReturnItems.ApprovedAmount)ReturnAmount,
            (select sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices 
            join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
            join TC_GRNReferences on TC_GRNReferences.Invoice_id = T_Invoices.id
            where InvoiceDate between %s and %s and Customer_id=%s )PA,
            (select sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices 
            join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
            where InvoiceDate between %s and %s and Party_id=%s )SA
            FROM T_PurchaseReturn
            join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id
            join TC_PurchaseReturnItems PRIPS on TC_PurchaseReturnItems.primarySourceID=PRIPS.id
            join T_PurchaseReturn PRPS on PRPS.id=PRIPS.PurchaseReturn_id
            join M_Parties on M_Parties.id=PRPS.Customer_id
            where T_PurchaseReturn.IsApproved=1 and M_Parties.PartyType_id in %s  and  T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Customer_id=%s group by TC_PurchaseReturnItems.ItemReason_id)p ''',
                                                                                            ([FromDate], [ToDate], [Party], [FromDate], [ToDate], [Party], PartyType, [FromDate], [ToDate], [Party]))
                                # CustomPrint('==============================================')
                                # CustomPrint(PartyType, claimREasonwise.query)
                                serializer = MasterclaimReasonReportSerializer(
                                    claimREasonwise, many=True).data

                                for a in serializer:
                                    # CustomPrint('========',PartyTypeID,'=============',a)
                                    stock = MC_ReturnReasonwiseMasterClaim(Claim_id=ClaimID, FromDate=FromDate, ToDate=ToDate, PrimaryAmount=a["PrimaryAmount"], SecondaryAmount=a["secondaryAmount"], ReturnAmount=a["ReturnAmount"], NetSaleValue=a[
                                        "NetPurchaseValue"], Budget=a["Budget"], ClaimAmount=a["ReturnAmount"], ClaimAgainstNetSale=a["ClaimAgainstNetSale"], ItemReason_id=a["ItemReason_id"], PartyType=PartyTypeID, Party_id=Party, CreatedBy=0)
                                    stock.save()
                                id = id+1
    # ===========================================================================================================================================
                            # for all partyType
                            claimREasonwise = MC_ReturnReasonwiseMasterClaim.objects.raw('''select 1 as id, ItemReason_id,IFNULL(PA,0) PrimaryAmount,IFNULL(SA,0) secondaryAmount,IFNULL(ReturnAmount,0)ReturnAmount ,
                                IFNULL((PA-ReturnAmount),0)NetPurchaseValue, 
            (CASE WHEN ItemReason_id=54 THEN IFNULL(((PA)*0.01),0) ELSE 0 END)Budget,IFNULL(ReturnAmount,0) ClaimAmount,
            
            IFNULL((ReturnAmount/PA)*100,0)ClaimAgainstNetSale
            from
            (SELECT TC_PurchaseReturnItems.ItemReason_id,sum(TC_PurchaseReturnItems.ApprovedAmount)ReturnAmount,
            (select sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices 
            join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
            join TC_GRNReferences on TC_GRNReferences.Invoice_id = T_Invoices.id
            where InvoiceDate between %s and %s and Customer_id=%s )PA,
            (select sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices 
            join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
            where InvoiceDate between %s and %s and Party_id=%s )SA
            FROM T_PurchaseReturn
            join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id
            join TC_PurchaseReturnItems PRIPS on TC_PurchaseReturnItems.primarySourceID=PRIPS.id
            join T_PurchaseReturn PRPS on PRPS.id=PRIPS.PurchaseReturn_id
            join M_Parties on M_Parties.id=PRPS.Customer_id
            where T_PurchaseReturn.IsApproved=1   and  T_PurchaseReturn.ReturnDate between %s and %s and T_PurchaseReturn.Customer_id=%s group by TC_PurchaseReturnItems.ItemReason_id)p ''',
                                                                                        ([FromDate], [ToDate], [Party], [FromDate], [ToDate], [Party], [FromDate], [ToDate], [Party]))

                            serializer = MasterclaimReasonReportSerializer(
                                claimREasonwise, many=True).data

                            PrimaryAmount = 0.0
                            SecondaryAmount = 0.0
                            ReturnAmount = 0.0
                            for a in serializer:

                                PrimaryAmount = float(a["PrimaryAmount"])
                                SecondaryAmount = float(a["secondaryAmount"])
                                ReturnAmount += float(a["ReturnAmount"])

                                stock = MC_ReturnReasonwiseMasterClaim(Claim_id=ClaimID, FromDate=FromDate, ToDate=ToDate, PrimaryAmount=a["PrimaryAmount"], SecondaryAmount=a["secondaryAmount"], ReturnAmount=a["ReturnAmount"], NetSaleValue=a[
                                    "NetPurchaseValue"], Budget=a["Budget"], ClaimAmount=a["ReturnAmount"], ClaimAgainstNetSale=a["ClaimAgainstNetSale"], ItemReason_id=a["ItemReason_id"], PartyType=0, Party_id=Party, CreatedBy=0)
                                stock.save()
                            claimupdate = M_Claim.objects.filter(id=ClaimID).update(
                                PrimaryAmount=PrimaryAmount, SecondaryAmount=SecondaryAmount, ReturnAmount=ReturnAmount)
    # ===========================================================================================================================================
    #  (Select Item_id from T_Orders JOIN TC_OrderItems ON Order_id = T_Orders.id WHERE Customer_id = %s Group By Item_id)I
                            StockProcessQuery = O_DateWiseLiveStock.objects.raw('''select * from (select 1 as id, I.Item_id,ifnull(PA.PrimaryAmount,0)PrimaryAmount,ifnull(SA.secondaryAmount,0)secondaryAmount,ifnull(RA.ReturnAmount,0)ReturnAmount,
                                ifnull((PA.PrimaryAmount-RA.ReturnAmount),0)NetPurchaseValue ,ifnull(((PA.PrimaryAmount)*0.01),0)Budget,IFNULL((RA.ReturnAmount/PA.PrimaryAmount)*100,0)ClaimAgainstNetSale

            from
            (Select id Item_id from M_Items )I
            left join


            (select TC_InvoiceItems.Item_id,sum(TC_InvoiceItems.Amount)PrimaryAmount from T_Invoices
            join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
            join TC_GRNReferences on TC_GRNReferences.Invoice_id = T_Invoices.id
            where InvoiceDate between %s and %s and Customer_id=%s group by Item_id)PA
            on I.Item_id=PA.Item_id
            left join 

            (select TC_InvoiceItems.Item_id,sum(TC_InvoiceItems.Amount)secondaryAmount from T_Invoices 
            join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
            join M_Parties on M_Parties.id=T_Invoices.Customer_id
            where  InvoiceDate between %s and %s and Party_id=%s group by Item_id)SA
            on I.Item_id=SA.Item_id
            left join 


            (SELECT TC_PurchaseReturnItems.Item_id,sum(TC_PurchaseReturnItems.ApprovedAmount)ReturnAmount
            FROM T_PurchaseReturn
            join TC_PurchaseReturnItems on T_PurchaseReturn.id=TC_PurchaseReturnItems.PurchaseReturn_id
            join M_Parties on M_Parties.id=T_PurchaseReturn.Customer_id
            where IsApproved=1  and  T_PurchaseReturn.ReturnDate between %s and %s and Customer_id=%s group by Item_id)RA

            on  I.Item_id=RA.Item_id)aaa where PrimaryAmount !=0 OR secondaryAmount !=0 OR ReturnAmount !=0
            ''',
                                                                                ( [FromDate], [ToDate], [Party], [FromDate], [ToDate], [Party], [FromDate], [ToDate], [Party]))

                            # CustomPrint(StockProcessQuery.query)
                            serializer = MasterclaimReportSerializer(
                                StockProcessQuery, many=True).data

                            for a in serializer:

                                stock = M_MasterClaim(Claim_id=ClaimID, FromDate=FromDate, ToDate=ToDate, PrimaryAmount=a["PrimaryAmount"], SecondaryAmount=a["secondaryAmount"], ReturnAmount=a["ReturnAmount"], NetSaleValue=a[
                                    "NetPurchaseValue"], Budget=a["Budget"], ClaimAmount=a["ReturnAmount"], ClaimAgainstNetSale=a["ClaimAgainstNetSale"], Item_id=a["Item_id"],  Party_id=Party, CreatedBy=0)
                                stock.save()
    # ===========================================================================================================================================
                            # CustomPrint(PartyName +'Master Claim Create Successfully')
                            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': PartyName +' Master Claim Create Successfully', 'Data': []})
                        else:
                            log_entry = create_transaction_logNew(request, Orderdata,PartyID,'',259,0,FromDate,ToDate,0)
                            # CustomPrint(PartyName +' Master Claim Already Created...!')
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': PartyName +' Master Claim Already Created...!', 'Data': []})
                log_entry = create_transaction_logNew(request, Orderdata,0,'',258,0,FromDate,ToDate,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Master Claim Create Successfully', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata,0,'ClaimSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  (e), 'Data': []})


class MasterClaimPrintView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                MasterClaimData = list()
                ReasonwiseMasterClaimList = list()
                q1 = M_PartyType.objects.filter(
                    IsSCM=1, Company_id=3).values("id", "Name")
                dict_list = list(q1)
                new_dict = {'id': 0, 'Name': 'Retailer AND Xpress'}
                dict_list.append(new_dict)
                sorted_data_list = sorted(dict_list, key=lambda x: x['id'])

                for i in sorted_data_list:
                    PartyTypeID = i["id"]
                    PartyTypeName = i["Name"]
                    Reasonwisequery = MC_ReturnReasonwiseMasterClaim.objects.raw(''' SELECT 1 as id, M_GeneralMaster.Name ItemReasonName, PrimaryAmount PurchaseAmount, SecondaryAmount SaleAmount, ReturnAmount, NetSaleValue, 
MC_ReturnReasonwiseMasterClaim.Budget, ClaimAmount, ClaimAgainstNetSale
 FROM MC_ReturnReasonwiseMasterClaim 
join M_GeneralMaster on M_GeneralMaster.id=MC_ReturnReasonwiseMasterClaim.ItemReason_id 
where FromDate=%s and ToDate=%s and Party_id=%s and PartyType=%s

order by M_GeneralMaster.id
''', ([FromDate], [ToDate], [Party], [PartyTypeID]))
                    ReasonwiseMasterClaim = ReasonwiseMasterClaimSerializer(
                        Reasonwisequery, many=True).data
                    if ReasonwiseMasterClaim:
                        ReasonwiseMasterClaimList.append({
                            PartyTypeName + ' Claim': ReasonwiseMasterClaim

                        })

                printProductwisequery = M_MasterClaim.objects.raw('''
                select 1 as id, Product,PurchaseAmount,SaleAmount,ReturnAmount,IFNULL((PurchaseAmount-ReturnAmount),0)NetSaleValue,
                IFNULL(((PurchaseAmount)*0.01),0)Budget,ClaimAmount,IFNULL(((ReturnAmount/PurchaseAmount)*100),0)ClaimAgainstNetSale
                
                from (SELECT  M_Group.Name Product, sum(PrimaryAmount)PurchaseAmount, sum(SecondaryAmount)SaleAmount, sum(ReturnAmount)ReturnAmount, 
                sum(ClaimAmount)ClaimAmount
FROM M_MasterClaim
left join M_Items on M_Items.id=M_MasterClaim.Item_id
left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1
left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
where FromDate=%s and ToDate=%s and Party_id=%s
group by M_Group.id)a''', ([FromDate], [ToDate], [Party]))
                ProductwiseMasterClaim = ProductwiseMasterClaimSerializer(
                    printProductwisequery, many=True).data
                MasterClaimData.append({
                    "ReasonwiseMasterClaim": ReasonwiseMasterClaimList,
                    "ProductwiseBudgetReport": ProductwiseMasterClaim
                })
                log_entry = create_transaction_logNew(request, Orderdata,Party,'From:'+str(FromDate)+','+'To:'+str(ToDate),255,0,FromDate,ToDate,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MasterClaimData[0]})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata,0,'MasterClaimPrint:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ClaimlistView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                Claimlistquery = M_Claim.objects.raw('''select id,PartyID,PartyName,PartyType, PrimaryAmount, ReturnAmount, SecondaryAmount,returncnt,ClaimDate,CreatedOn from (SELECT Distinct M_Parties.id PartyID,M_Parties.Name PartyName,M_PartyType.id M_PartyTypeID,M_PartyType.Name PartyType 
                FROM M_Parties 
join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id
join M_PartyType on M_PartyType.id=M_Parties.PartyType_id 
where ( MC_PartySubParty.Party_id=%s or MC_PartySubParty.SubParty_id=%s) and M_PartyType.IsVendor=0 and M_PartyType.IsRetailer=0)a
left join 
(select id,Date ClaimDate ,Customer_id, PrimaryAmount, ReturnAmount, SecondaryAmount,CreatedOn from M_Claim where FromDate=%s and ToDate=%s )b
on a.PartyID=b.Customer_id
left join
(select count(*)returncnt ,Customer_id from T_PurchaseReturn where T_PurchaseReturn.ReturnDate between %s and %s group by Customer_id )c
on a.PartyID=c.Customer_id''', ([Party], [Party], [FromDate], [ToDate], [FromDate], [ToDate]))
                # prCustomPrintint(Claimlistquery.query)
                if Claimlistquery:

                    Claimlist = ClaimlistSerializer(
                        Claimlistquery, many=True).data
                    log_entry = create_transaction_logNew(request, Orderdata,Party,'From:'+str(FromDate)+','+'To:'+str(ToDate),253,0,FromDate,ToDate,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Claimlist})
                else:
                    log_entry = create_transaction_logNew(request, Orderdata,Party,'ClaimList Not Available',253,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Orderdata,0,'ClaimList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not available', 'Data': []})


class Listofclaimforclaimtracking(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        ClaimTrackingdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Year = ClaimTrackingdata['Year']
                Month = ClaimTrackingdata['Month']
                FromDate = Year+'-'+Month+'-'+'01'
                Claimlistquery = M_Claim.objects.raw(
                    '''select MC_ReturnReasonwiseMasterClaim.Claim_id As id,SUM(MC_ReturnReasonwiseMasterClaim.ReturnAmount) As ClaimAmount, M_Parties.id As PartyID,M_Parties.Name PartyName,MC_ReturnReasonwiseMasterClaim.PartyType AS PartyTypeID,M_PartyType.Name AS PartyTypeName FROM M_Claim  JOIN MC_ReturnReasonwiseMasterClaim ON MC_ReturnReasonwiseMasterClaim.Claim_id=M_Claim.id  JOIN M_Parties ON M_Parties.id=M_Claim.Customer_id LEFT JOIN M_PartyType ON M_PartyType.id = MC_ReturnReasonwiseMasterClaim.PartyType WHERE M_Claim.FromDate =%s AND MC_ReturnReasonwiseMasterClaim.PartyType !=0  group by id,PartyID,PartyName,PartyType,PartyTypeName ''', ([FromDate]))
                # CustomPrint(Claimlistquery.query)
                if Claimlistquery:
                    Claimlist = ClaimlistforClaimTrackingSerializer(
                        Claimlistquery, many=True).data
                    log_entry = create_transaction_logNew(request, ClaimTrackingdata,0,'',261,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Claimlist})
                else:
                    log_entry = create_transaction_logNew(request, ClaimTrackingdata,0,'Claimlist Not available',261,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ClaimTrackingdata, 0,'Claimlist:'+str(e),33,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not available', 'Data': []})


class ClaimTrackingEntryListView(CreateAPIView):

    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        ClaimTrackingdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = ClaimTrackingdata['FromDate']
                ToDate = ClaimTrackingdata['ToDate']
                Party = ClaimTrackingdata['Party']
                Employee = ClaimTrackingdata['Employee']

                if Employee > 0:
                    EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[Employee])
                    for row in EmpPartys:
                        p=row.id
                    PartyIDs = p.split(",")

                ClaimTrackingquery = '''SELECT T_ClaimTrackingEntry.id, X.id Party_id, M_Cluster.Name Cluster, M_SubCluster.Name SubCluster, X.Name PartyName, T_ClaimTrackingEntry.FullClaimNo, Claim_id,
                                                            T_ClaimTrackingEntry.Date, T_ClaimTrackingEntry.Month, 
                                                            T_ClaimTrackingEntry.Year, a.Name TypeName,
                                                            b.Name TypeOfClaimName, M_PriceList.Name ClaimTradeName,  ClaimAmount,
                                                            d.Name AS CreditNoteStatus,
                                                            CreditNoteNo, CreditNoteDate, CreditNoteAmount, ClaimSummaryDate, 
                                                            CreditNoteUpload,  ClaimReceivedSource , T_ClaimTrackingEntry.Remark,T_ClaimTrackingEntry.IsDeleted
                                                            FROM T_ClaimTrackingEntry
                                                            LEFT JOIN M_PartyType ON M_PartyType.id= T_ClaimTrackingEntry.PartyType_id
                                                            LEFT JOIN M_Parties X ON X.id=T_ClaimTrackingEntry.Party_id 
                                                            Left join M_PartyDetails Y on X.id = Y.Party_id and Y.Group_id IS NULL
                                                            Left join M_Cluster on Y.Cluster_id = M_Cluster.id
                                                            left join M_SubCluster on Y.SubCluster_id = M_SubCluster.id
                                                            LEFT JOIN M_GeneralMaster a ON a.id = T_ClaimTrackingEntry.Type
                                                            LEFT JOIN M_GeneralMaster b ON b.id = T_ClaimTrackingEntry.TypeOfClaim
                                                            LEFT JOIN M_GeneralMaster c ON c.id = T_ClaimTrackingEntry.ClaimCheckBy
                                                            LEFT JOIN M_GeneralMaster d ON d.id = T_ClaimTrackingEntry.CreditNotestatus
                                                            LEFT JOIN M_PriceList ON M_PriceList.id=T_ClaimTrackingEntry.ClaimTrade
                                                            WHERE T_ClaimTrackingEntry.Date between %s and %s'''
                # CustomPrint(ClaimTrackingquery)
                if Party == "":
                    ClaimTrackingquery += " "
                    if Employee == 0:
                            ClaimTrackingquery += " "
                    else:
                            ClaimTrackingquery += " and X.id in %s"
                else:
                        ClaimTrackingquery += " and X.id=%s"

                if Party == "":
                        
                        if Employee == 0:
                            
                            ClaimTrackingqueryresults = T_ClaimTrackingEntry.objects.raw(ClaimTrackingquery, [FromDate, ToDate])
                        else:
                            
                            ClaimTrackingqueryresults = T_ClaimTrackingEntry.objects.raw(ClaimTrackingquery, [FromDate, ToDate, PartyIDs])
                else:
                    
                    ClaimTrackingqueryresults = T_ClaimTrackingEntry.objects.raw(ClaimTrackingquery,[FromDate,ToDate,Party])
                if  ClaimTrackingqueryresults: 
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    # ClaimTrackingdata = ClaimTrackingSerializerSecond(ClaimTrackingquery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ClaimTrackingdata})
                    ClaimTrackingList = list()
                    
                    for a in ClaimTrackingqueryresults:
                        dd = str(a.CreditNoteUpload)
                        month_name = a.Month.lower()  
                        
                        if month_name.isdigit() and int(month_name) in range(1, 13):
                           month_name = calendar.month_name[int(month_name)]
                        else:
                            month_name = "Unknown"
                            
                        ClaimTrackingList.append({
                            "id":a.id,
                            "Cluster": a.Cluster,
                            "SubCluster":a.SubCluster,
                            "Party": a.Party_id,
                            "PartyName": a.PartyName,
                            "FullClaimNo": a.FullClaimNo,
                            "ClaimID": a.Claim_id,
                            "Date": a.Date,
                            "Month": month_name,
                            "Year": a.Year,
                            "TypeName": a.TypeName,
                            "TypeOfClaimName": a.TypeOfClaimName,
                            "ClaimTradeName": a.ClaimTradeName,
                            "ClaimAmount": a.ClaimAmount,
                            "CreditNoteStatus": a.CreditNoteStatus,
                            "CreditNoteNo": a.CreditNoteNo,
                            "CreditNoteDate": a.CreditNoteDate,
                            "CreditNoteAmount": a.CreditNoteAmount,
                            "ClaimSummaryDate": a.ClaimSummaryDate,
                            "CreditNoteUpload": dd,
                            "ClaimReceivedSource": a.ClaimReceivedSource,
                            "Remark":a.Remark,
                            "IsRecordDeleted":a.IsDeleted

                        })
                    log_entry = create_transaction_logNew(request, ClaimTrackingList,a.Party_id,'',257,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ClaimTrackingList})
                log_entry = create_transaction_logNew(request, ClaimTrackingdata,0,'ClaimTrackingList Not available',257,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Claim Tracking Entry Not available ', 'Data': []})
        except T_ClaimTrackingEntry.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'ClaimTrackingList Not available',257,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Claim Tracking Entry Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, ClaimTrackingdata,0,'ClaimTrackingList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ClaimTrackingEntryView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser,MultiPartParser,FormParser]

    @transaction.atomic()
    def post(self, request,format=None):
        # Claimtracking_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
               
                Claimtracking_data = {
                    "Date" : request.POST.get('Date'),
                    "Month" : request.POST.get('Month'),
                    "Year" : request.POST.get('Year'),
                    "ClaimReceivedSource" : request.POST.get('ClaimReceivedSource'),
                    "Type" : request.POST.get('Type'),
                    "ClaimTrade" : request.POST.get('ClaimTrade'),
                    "TypeOfClaim" : request.POST.get('TypeOfClaim'),
                    "ClaimAmount" : request.POST.get('ClaimAmount'),
                    "Remark" : request.POST.get('Remark'),
                    "ClaimCheckBy" : request.POST.get('ClaimCheckBy'),
                    "CreditNotestatus" : request.POST.get('CreditNotestatus'),
                    "CreditNoteNo" : request.POST.get('CreditNoteNo'),
                    "CreditNoteDate" : request.POST.get('CreditNoteDate'),
                    "CreditNoteAmount" : request.POST.get('CreditNoteAmount'),
                    "ClaimSummaryDate" : request.POST.get('ClaimSummaryDate'),
                    "CreditNoteUpload" : request.POST.get('CreditNoteUpload'),
                    "Claim" : request.POST.get('Claim'),
                    "Party" : request.POST.get('Party'),
                    "FullClaimNo" : request.POST.get('FullClaimNo'),  
                }
                '''Image Upload Code End''' 
                avatar = request.FILES.getlist('CreditNoteUpload')
                for file in avatar:
                    Claimtracking_data['CreditNoteUpload']=file
                '''Image Upload Code End'''
                Claimtracking_Serializer = ClaimTrackingSerializer(
                    data=Claimtracking_data)
                if Claimtracking_Serializer.is_valid():
                    Claimtracking_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Claim Tracking Entry Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Claimtracking_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ClaimTrackingEntryViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    parser_classes = [JSONParser,MultiPartParser,FormParser]
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                ClaimTrackingquery = T_ClaimTrackingEntry.objects.raw('''SELECT T_ClaimTrackingEntry.id, T_ClaimTrackingEntry.Date, T_ClaimTrackingEntry.Month, T_ClaimTrackingEntry.Year, ClaimReceivedSource, T_ClaimTrackingEntry.Type,a.Name TypeName, ClaimTrade,M_PriceList.Name ClaimTradeName,TypeOfClaim,b.Name TypeOfClaimName, ClaimAmount, Remark, ClaimCheckBy,c.Name As ClaimCheckByName,CreditNotestatus, d.Name As CreditNotestatusName, CreditNoteNo, CreditNoteDate, CreditNoteAmount, ClaimSummaryDate, CreditNoteUpload,  CreditNoteUpload as FileName, Claim_id, T_ClaimTrackingEntry.Party_id, P.Name PartyName,T_ClaimTrackingEntry.FullClaimNo,T_ClaimTrackingEntry.PartyType_id,M_PartyType.Name PartyTypeName, M_Cluster.Name Cluster , M_SubCluster.Name SubCluster
FROM T_ClaimTrackingEntry
LEFT JOIN M_PartyType ON M_PartyType.id = T_ClaimTrackingEntry.PartyType_id 
JOIN M_Parties P ON P.id=T_ClaimTrackingEntry.Party_id
JOIN M_GeneralMaster a ON a.id = T_ClaimTrackingEntry.Type
LEFT JOIN M_GeneralMaster b ON b.id = T_ClaimTrackingEntry.TypeOfClaim
JOIN M_GeneralMaster c ON c.id = T_ClaimTrackingEntry.ClaimCheckBy
JOIN M_GeneralMaster d ON d.id = T_ClaimTrackingEntry.CreditNotestatus
JOIN M_PriceList ON M_PriceList.id=T_ClaimTrackingEntry.ClaimTrade 
LEFT JOIN M_PartyDetails X on X.Supplier_id = P.id and X.Group_id IS NULL
LEFT JOIN M_Cluster On X.Cluster_id=M_Cluster.id 
LEFT JOIN M_SubCluster on X.SubCluster_id=M_SubCluster.Id 
WHERE T_ClaimTrackingEntry.id=%s ''', ([id]))
                # CustomPrint(ClaimTrackingquery.query)
                if ClaimTrackingquery:
                    ClaimTrackingdata = ClaimTrackingSerializerSecond(
                        ClaimTrackingquery, many=True).data
                    ClaimTrackingList = list()
                    for a in ClaimTrackingdata:
                        ClaimTrackingList.append({
                            "id": a['id'],
                            "Date": a['Date'],
                            "Month": a['Month'],
                            "Year": a['Year'],
                            "ClaimReceivedSource": a['ClaimReceivedSource'],
                            "Type": a['Type'],
                            "TypeName": a['TypeName'],
                            "ClaimTrade": a['ClaimTrade'],
                            "ClaimTradeName": a['ClaimTradeName'],
                            "TypeOfClaim": a['TypeOfClaim'],
                            "TypeOfClaimName": a['TypeOfClaimName'],
                            "ClaimAmount": a['ClaimAmount'],
                            "Remark": a['Remark'],
                            "ClaimCheckBy": a['ClaimCheckBy'],
                            "ClaimCheckByName": a['ClaimCheckByName'],
                            "CreditNotestatus": a['CreditNotestatus'],
                            "CreditNotestatusName": a['CreditNotestatusName'],
                            "CreditNoteNo": a['CreditNoteNo'],
                            "CreditNoteDate": a['CreditNoteDate'],
                            "CreditNoteAmount": a['CreditNoteAmount'],
                            "ClaimSummaryDate": a['ClaimSummaryDate'],
                            "CreditNoteUpload": a['CreditNoteUpload'],
                            "FileName" : a['FileName'],
                            "Claim": a['Claim_id'],
                            "Party": a['Party_id'],
                            "PartyName": a['PartyName'],
                            "FullClaimNo": a['FullClaimNo'],
                            "PartyType": a['PartyType_id'],
                            "PartyTypeName": a['PartyTypeName'],
                            "Cluster":a['Cluster'],
                            "SubCluster":a['SubCluster']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': ClaimTrackingList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Claim Tracking Entry Not available ', 'Data': []})
        except T_ClaimTrackingEntry.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Claim Tracking Entry Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                # Claimtrackingdata = JSONParser().parse(request)
                Claimtrackingdata = {
                    "Date" : request.POST.get('Date'),
                    "Month" : request.POST.get('Month'),
                    "Year" : request.POST.get('Year'),
                    "ClaimReceivedSource" : request.POST.get('ClaimReceivedSource'),
                    "Type" : request.POST.get('Type'),
                    "ClaimTrade" : request.POST.get('ClaimTrade'),
                    "TypeOfClaim" : request.POST.get('TypeOfClaim'),
                    "ClaimAmount" : request.POST.get('ClaimAmount'),
                    "Remark" : request.POST.get('Remark'),
                    "ClaimCheckBy" : request.POST.get('ClaimCheckBy'),
                    "CreditNotestatus" : request.POST.get('CreditNotestatus'),
                    "CreditNoteNo" : request.POST.get('CreditNoteNo'),
                    "CreditNoteDate" : request.POST.get('CreditNoteDate'),
                    "CreditNoteAmount" : request.POST.get('CreditNoteAmount'),
                    "ClaimSummaryDate" : request.POST.get('ClaimSummaryDate'),
                    "CreditNoteUpload" : request.POST.get('CreditNoteUpload'),
                    "Claim" : request.POST.get('Claim'),
                    "Party" : request.POST.get('Party'),
                    "FullClaimNo" : request.POST.get('FullClaimNo'),  
                }
                '''Image Upload Code End''' 
                avatar = request.FILES.getlist('CreditNoteUpload')
                for file in avatar:
                    Claimtrackingdata['CreditNoteUpload']=file
                '''Image Upload Code End'''

                ClaimtrackingdataByID = T_ClaimTrackingEntry.objects.get(id=id)
                Claimtrackingdata_Serializer = ClaimTrackingSerializer(
                    ClaimtrackingdataByID, data=Claimtrackingdata)
                if Claimtrackingdata_Serializer.is_valid():
                    Claimtrackingdata_Serializer.save()
                    # log_entry = create_transaction_logNew(request, Claimtrackingdata,0,'',262,id)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Claim Tracking Entry Updated Successfully', 'Data': []})
                else:
                    # log_entry = create_transaction_logNew(request, Claimtrackingdata,0,'ClaimTrackingEdit:'+str(Claimtrackingdata_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Claimtrackingdata_Serializer.errors, 'Data': []})
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0,0,'ClaimTrackingEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Claimtrackingdata = T_ClaimTrackingEntry.objects.filter(id=id).update(IsDeleted=1)
                log_entry = create_transaction_logNew(request, 0,0,'ClaimTrackingEntryDeleted:'+str(id),263,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Claim Tracking Entry Deleted Successfully', 'Data': []})
        except T_ClaimTrackingEntry.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Claim Tracking Entry Does Not Exist',263,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Claim Tracking Entry Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'ClaimTrackingEntryDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
