from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew
from FoodERPApp.models import CustomPrint, M_Items, M_Parties
from SweetPOS.Views.SweetPOSCommonFunction import BasicAuthenticationfunction
from ..models import *
from rest_framework.authentication import BasicAuthentication
from datetime import datetime
from datetime import date
from datetime import timedelta



class SPOSStockProcessingView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                start_date_str = Orderdata['FromDate']
                end_date_str = Orderdata['ToDate']
                Party = Orderdata['Party']

                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

                date_range = []
                current_date = start_date
                while current_date <= end_date:
                    Date = current_date.strftime("%Y-%m-%d")
                    # print(Date)
                    
                    StockDeleteQuery = O_SPOSDateWiseLiveStock.objects.filter(
                        Party=Party, StockDate=Date)
                    StockDeleteQuery.delete()
                    # CustomPrint(StockDeleteQuery.query)
                    StockProcessQuery = O_SPOSDateWiseLiveStock.objects.raw('''select id,ItemID,UnitID,
                    round(OpeningBalance,3) OpeningBalance,
                    round(GRN,3) GRN,
                    round(SalesReturn,3) SalesReturn,
                    round(Sale,3) Sale,
                    round(PurchaseReturn,3) PurchaseReturn,
                    round(((OpeningBalance+GRN+SalesReturn+StockAdjustment)-(Sale+PurchaseReturn)),3) ClosingBalance,
                    StockAdjustment,ActualStock
 from

(select 1 as id,I.Item_id ItemID,I.UnitID,

(CASE WHEN StockEntry >= 0  THEN IFNULL(StockEntry,0)  ELSE IFNULL(ClosingBalance,0) END )OpeningBalance,
IFNULL(InvoiveQuantity,0)Sale,
IFNULL(GRNQuantity,0)GRN,
IFNULL(SalesReturnQuantity,0)SalesReturn,
IFNULL(PurchesReturnQuantity,0)PurchaseReturn,
IFNULL(StockAdjustmentQTY,0)StockAdjustment,
IFNULL(ActualStock,0)ActualStock

from

(Select MC_PartyItems.Item_id,IU.id UnitID  from FoodERP.MC_PartyItems 
        join FoodERP.M_Items on M_Items.id=MC_PartyItems.Item_id and M_Items.IsStockProcessItem=1 
        JOIN FoodERP.MC_ItemUnits IU  ON IU.UnitID_Id=M_Items.BaseUnitID_id and IU.Item_id=M_Items.id 
        where Party_id=%s)I

left join (SELECT IFNULL(Item,0) ItemID, sum(ClosingBalance)ClosingBalance FROM SweetPOS.O_SPOSDateWiseLiveStock WHERE StockDate = DATE_SUB(  %s, 
INTERVAL 1
                                        DAY ) AND Party =%s GROUP BY ItemID)CB

on I.Item_id=CB.ItemID

left join (SELECT Item_id,SUM(BaseUnitQuantity) GRNQuantity,SUM(Amount) GRNValue
FROM FoodERP.T_GRNs JOIN FoodERP.TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
WHERE InvoiceDate = %s AND Customer_id = %s GROUP BY Item_id)GRN

on I.Item_id=GRN.Item_id

left join (SELECT 1 as id, Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
FROM FoodERP.T_Invoices JOIN FoodERP.TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
WHERE InvoiceDate = %s AND Party_id = %s GROUP BY Item_id
union
SELECT 2 as id, Item Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
FROM SweetPOS.T_SPOSInvoices T_Invoices JOIN SweetPOS.TC_SPOSInvoiceItems TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
WHERE  T_Invoices.InvoiceDate = %s AND T_Invoices.Party =%s and T_Invoices.IsDeleted=0 GROUP BY Item)Invoice

on I.Item_id=Invoice.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) SalesReturnQuantity,sum(Amount) SalesReturnValue
FROM FoodERP.T_PurchaseReturn join FoodERP.TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
WHERE ReturnDate = %s AND Party_id = %s and TC_PurchaseReturnItems.ItemReason_id in(SELECT DefaultValue FROM FoodERP.M_Settings where id=14) GROUP BY Item_id)SalesReturn

on I.Item_id=SalesReturn.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) PurchesReturnQuantity,sum(Amount) PurchesReturnValue
FROM FoodERP.T_PurchaseReturn join FoodERP.TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
WHERE ReturnDate = %s AND Customer_id = %s and ((TC_PurchaseReturnItems.ItemReason_id IN (SELECT DefaultValue FROM FoodERP.M_Settings WHERE id = 14) and T_PurchaseReturn.Mode =3) OR(T_PurchaseReturn.Mode =2)) GROUP BY Item_id)PurchesReturn
on I.Item_id=PurchesReturn.Item_id

Left join (Select Item,SUM(BaseUnitQuantity)StockEntry  from SweetPOS.T_SPOSStock where   IsStockAdjustment=0 and StockDate= DATE_SUB(  %s, INTERVAL 1 DAY ) AND Party=%s GROUP BY Item)StockEntry
ON I.Item_id=StockEntry.Item

left join (SELECT Item,sum(Difference)StockAdjustmentQTY FROM SweetPOS.T_SPOSStock where  IsStockAdjustment=1 and StockDate = %s and Party= %s group by Item)StockAdjustment
on I.Item_id=StockAdjustment.Item

left join (SELECT Item,sum(BaseUnitQuantity)ActualStock FROM SweetPOS.T_SPOSStock where  IsStockAdjustment=0 and StockDate = %s and Party= %s group by Item)ActualStock
on I.Item_id=ActualStock.Item

)R
''',([Party], [Date],[Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party]))
# where
# OpeningBalance!=0 OR GRN!=0 OR Sale!=0 OR PurchaseReturn != 0 OR SalesReturn !=0 OR StockAdjustment!=0
                 
                    # serializer = StockProcessingReportSerializer(StockProcessQuery, many=True).data
                    # CustomPrint(serializer)
                    # print(StockProcessQuery)
                    for a in StockProcessQuery:
                       
                        if(a.OpeningBalance!=0 or a.GRN!=0 or a.Sale!=0 or a.PurchaseReturn != 0 or a.SalesReturn !=0 or a.StockAdjustment!=0):
                            # print('kkkkkkkkkkkkkkkkkkkkkkkkkk')
                            stock = O_SPOSDateWiseLiveStock(StockDate=Date, OpeningBalance=a.OpeningBalance, GRN=a.GRN, Sale=a.Sale, PurchaseReturn=a.PurchaseReturn, SalesReturn=a.SalesReturn, ClosingBalance=a.ClosingBalance, ActualStock=a.ActualStock, StockAdjustment=a.StockAdjustment, Item=a.ItemID, Unit=a.UnitID, Party=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                            stock.save()
                       
                        # if(a.ClosingBalance == 0) :
                        #     stockout = T_SPOSStockOut(StockDate=Date, Item=a.ItemID, Party=Party, CreatedBy=0)
                        #     stockout.save()    
                    
                    current_date += timedelta(days=1)
                log_entry = create_transaction_logNew(request, Orderdata, Party, 'Stock Process Successfully', 209, 0, start_date_str, end_date_str, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Process Successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class SPOSStockProcessingthoughtcronjobView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            # print("stock processsing started.")
            with transaction.atomic():
                
                user = BasicAuthenticationfunction(request)
                if user is not None:
                    today = date.today()
                    
                    # Querying the database to count the number of records for today's date in O_SPOSDateWiseLiveStock
                    query0 = O_SPOSDateWiseLiveStock.objects.filter(StockDate=today).count()

                    # If there are records found for today's date (i.e., query0 > 0), then...
                    if query0 > 0:
                        # Calculate yesterday's date by subtracting 1 day from today's date
                        yesterday = today - timedelta(days=1)
                    else:
                        # If no records were found for today, set yesterday to be the first day of the current month
#                         updateIsStockProcessItem= M_Items.objects.raw(''' update M_Items set IsStockProcessItem =1 where id in(  
# SELECT DISTINCT Item_id FROM T_Invoices JOIN TC_InvoiceItems ON Invoice_id = T_Invoices.id 
# WHERE InvoiceDate >= DATE_SUB(CURDATE(), INTERVAL 100 DAY) AND Party_id NOT IN (SELECT DefaultValue FROM M_Settings WHERE id=56))''')
                        yesterday = today.replace(day=1)    
                    
                    start_date_str = yesterday
                    end_date_str = today
                    Partys = M_Parties.objects.filter(PartyType=19,isActive=1).values('id')
                                        

                    log_entry = create_transaction_logNew(request, Orderdata, 0, 'Stock Process start', 209, 0, start_date_str, end_date_str, 0)
                    for Party in Partys:
                        print(Party['id'] ,"start time  : ",datetime.now())
                        # start_date = start_date_str.strptime( "%Y-%m-%d")
                        # end_date = end_date_str.strptime( "%Y-%m-%d")
                        Party=Party['id']
                        start_date = start_date_str
                        end_date = end_date_str
                        date_range = []
                        current_date = start_date
                        while current_date <= end_date:
                            Date = current_date.strftime("%Y-%m-%d")
                            # print(Date)
                            
                            StockDeleteQuery = O_SPOSDateWiseLiveStock.objects.filter(Party=Party, StockDate=Date)
                            StockDeleteQuery.delete()
                            # CustomPrint(StockDeleteQuery.query)
                            StockProcessQuery = O_SPOSDateWiseLiveStock.objects.raw('''select id,ItemID,UnitID,
                            round(OpeningBalance,3) OpeningBalance,
                            round(GRN,3) GRN,
                            round(SalesReturn,3) SalesReturn,
                            round(Sale,3) Sale,
                            round(PurchaseReturn,3) PurchaseReturn,
                            round(((OpeningBalance+GRN+SalesReturn+StockAdjustment)-(Sale+PurchaseReturn)),3) ClosingBalance,
                            StockAdjustment,ActualStock
        from

        (select 1 as id,I.Item_id ItemID,I.UnitID,

        (CASE WHEN StockEntry >= 0  THEN IFNULL(StockEntry,0)  ELSE IFNULL(ClosingBalance,0) END )OpeningBalance,
        IFNULL(InvoiveQuantity,0)Sale,
        IFNULL(GRNQuantity,0)GRN,
        IFNULL(SalesReturnQuantity,0)SalesReturn,
        IFNULL(PurchesReturnQuantity,0)PurchaseReturn,
        IFNULL(StockAdjustmentQTY,0)StockAdjustment,
        IFNULL(ActualStock,0)ActualStock

        from


        (Select MC_PartyItems.Item_id,IU.id UnitID  from FoodERP.MC_PartyItems 
        join FoodERP.M_Items on M_Items.id=MC_PartyItems.Item_id and M_Items.IsStockProcessItem=1 
        JOIN FoodERP.MC_ItemUnits IU  ON IU.UnitID_Id=M_Items.BaseUnitID_id and IU.Item_id=M_Items.id 
        where Party_id=%s)I


        left join (SELECT IFNULL(Item,0) ItemID, sum(ClosingBalance)ClosingBalance FROM SweetPOS.O_SPOSDateWiseLiveStock WHERE StockDate = DATE_SUB(  %s, 
        INTERVAL 1
                                                DAY ) AND Party =%s GROUP BY ItemID)CB

        on I.Item_id=CB.ItemID

        left join (SELECT Item_id,SUM(BaseUnitQuantity) GRNQuantity,SUM(Amount) GRNValue
        FROM FoodERP.T_GRNs JOIN FoodERP.TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
        WHERE InvoiceDate = %s AND Customer_id = %s GROUP BY Item_id)GRN

        on I.Item_id=GRN.Item_id

        left join (SELECT 1 as id, Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
        FROM FoodERP.T_Invoices JOIN FoodERP.TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
        WHERE InvoiceDate = %s AND Party_id = %s GROUP BY Item_id
        union
        SELECT 2 as id, Item Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
        FROM SweetPOS.T_SPOSInvoices T_Invoices JOIN SweetPOS.TC_SPOSInvoiceItems TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
        WHERE  T_Invoices.InvoiceDate = %s AND T_Invoices.Party =%s and T_Invoices.IsDeleted=0 GROUP BY Item)Invoice

        on I.Item_id=Invoice.Item_id

        left join (SELECT Item_id,SUM(BaseUnitQuantity) SalesReturnQuantity,sum(Amount) SalesReturnValue
        FROM FoodERP.T_PurchaseReturn join FoodERP.TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
        WHERE ReturnDate = %s AND Party_id = %s and TC_PurchaseReturnItems.ItemReason_id in(SELECT DefaultValue FROM FoodERP.M_Settings where id=14) GROUP BY Item_id)SalesReturn

        on I.Item_id=SalesReturn.Item_id

        left join (SELECT Item_id,SUM(BaseUnitQuantity) PurchesReturnQuantity,sum(Amount) PurchesReturnValue
        FROM FoodERP.T_PurchaseReturn join FoodERP.TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
        WHERE ReturnDate = %s AND Customer_id = %s and ((TC_PurchaseReturnItems.ItemReason_id IN (SELECT DefaultValue FROM FoodERP.M_Settings WHERE id = 14) and T_PurchaseReturn.Mode =3) OR(T_PurchaseReturn.Mode =2)) GROUP BY Item_id)PurchesReturn
        on I.Item_id=PurchesReturn.Item_id

        Left join (Select Item,SUM(BaseUnitQuantity)StockEntry  from SweetPOS.T_SPOSStock where   IsStockAdjustment=0 and StockDate= DATE_SUB(  %s, INTERVAL 1 DAY ) AND Party=%s GROUP BY Item)StockEntry
        ON I.Item_id=StockEntry.Item

        left join (SELECT Item,sum(Difference)StockAdjustmentQTY FROM SweetPOS.T_SPOSStock where  IsStockAdjustment=1 and StockDate = %s and Party= %s group by Item)StockAdjustment
        on I.Item_id=StockAdjustment.Item

        left join (SELECT Item,sum(BaseUnitQuantity)ActualStock FROM SweetPOS.T_SPOSStock where  IsStockAdjustment=0 and StockDate = %s and Party= %s group by Item)ActualStock
        on I.Item_id=ActualStock.Item

        )R 
        ''',([Party], [Date],[Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party]))
        # where
        # OpeningBalance!=0 OR GRN!=0 OR Sale!=0 OR PurchaseReturn != 0 OR SalesReturn !=0 OR StockAdjustment!=0
                        
                            #  serializer = StockProcessingReportSerializer(StockProcessQuery, many=True).data
                            # CustomPrint(serializer)
                            
                            # print(StockProcessQuery)
                            # print(" mid : ",datetime.now())

                            stocks_to_create = []
                            stockouts_to_create = []
                            for a in StockProcessQuery:
                                if any([a.OpeningBalance, a.GRN, a.Sale, a.PurchaseReturn, a.SalesReturn, a.StockAdjustment]):
                                    stock = O_SPOSDateWiseLiveStock(
                                        StockDate=Date, OpeningBalance=a.OpeningBalance, GRN=a.GRN, Sale=a.Sale,
                                        PurchaseReturn=a.PurchaseReturn, SalesReturn=a.SalesReturn, ClosingBalance=a.ClosingBalance,
                                        ActualStock=a.ActualStock, StockAdjustment=a.StockAdjustment, Item=a.ItemID,
                                        Unit=a.UnitID, Party=Party, CreatedBy=0, IsAdjusted=0, MRPValue=0
                                    )
                                    stocks_to_create.append(stock)

                                if query0 > 0:
                                    processingdate = datetime.strptime(Date, '%Y-%m-%d').date()
                                    if a.ClosingBalance <= 0 and date.today() == processingdate:
                                        if 8 < datetime.now().hour < 22:
                                            stockout = T_SPOSStockOut(
                                                StockDate=Date, Item=a.ItemID, Party=Party, CreatedBy=0, Quantity=a.ClosingBalance
                                            )
                                            stockouts_to_create.append(stockout)
                            # for a in StockProcessQuery:
                            #     # print("Insert start time  : ",datetime.now())
                            #     if(a.OpeningBalance!=0 or a.GRN!=0 or a.Sale!=0 or a.PurchaseReturn != 0 or a.SalesReturn !=0 or a.StockAdjustment!=0):
                            #         # print('kkkkkkkkkkkkkkkkkkkkkkkkkk')
                            #         stock = O_SPOSDateWiseLiveStock(StockDate=Date, OpeningBalance=a.OpeningBalance, GRN=a.GRN, Sale=a.Sale, PurchaseReturn=a.PurchaseReturn, SalesReturn=a.SalesReturn, ClosingBalance=a.ClosingBalance, ActualStock=a.ActualStock, StockAdjustment=a.StockAdjustment, Item=a.ItemID, Unit=a.UnitID, Party=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                            #         stock.save()
                                
                            #     if query0 > 0 :
                            #         processingdate =datetime.strptime(Date, '%Y-%m-%d').date()
                            #         if a.ClosingBalance <= 0 and date.today() == processingdate:
                            #             if ((datetime.now()).hour ) > 8 and ((datetime.now()).hour ) < 22 :
                            #                 stockout = T_SPOSStockOut(StockDate=Date, Item=a.ItemID, Party=Party, CreatedBy=0,Quantity=a.ClosingBalance)
                            #                 stockout.save()    
                                
                            O_SPOSDateWiseLiveStock.objects.bulk_create(stocks_to_create)
                            T_SPOSStockOut.objects.bulk_create(stockouts_to_create)
                            
                            current_date += timedelta(days=1)
                        # print(" end time  : ",datetime.now())
                        log_entry = create_transaction_logNew(request, Orderdata, Party, 'Stock Process Successfully', 209, 0, start_date_str, end_date_str, 0)
                            
                        
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'Stock Process Successfully', 209, 0, start_date_str, end_date_str, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Process Successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
