from datetime import datetime, timedelta
from django.http import JsonResponse
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Views.V_CommFunction import *
from ..Serializer.S_Reports import *
from ..models import *

def AutoStockProcess(FromDate,ToDate,Party):
    

    try:
        with transaction.atomic():
            
            Date=date.today()
            start_date_str = Date
            end_date_str = Date
            Party = 14
            print(start_date_str,start_date_str,Party)
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

            date_range = []
            current_date = start_date
            while current_date <= end_date:
                Date = current_date.strftime("%Y-%m-%d")
                # print(Date)
                # StockDeleteQuery  = O_DateWiseLiveStock.objects.raw('''DELETE FROM O_DateWiseLiveStock WHERE StockDate=%s AND Party_id=%s''',([Date],[Party]))
                StockDeleteQuery = O_DateWiseLiveStock.objects.filter(
                    Party_id=Party, StockDate=Date)
                StockDeleteQuery.delete()
                # print(StockDeleteQuery.query)
                StockProcessQuery = O_DateWiseLiveStock.objects.raw('''select id,ItemID,UnitID,
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

(Select Item_id,M_Items.BaseUnitID_id UnitID  from MC_PartyItems join M_Items on M_Items.id=MC_PartyItems.Item_id where Party_id=%s)I

left join (SELECT IFNULL(Item_id,0) ItemID, sum(ClosingBalance)ClosingBalance FROM O_DateWiseLiveStock WHERE StockDate = DATE_SUB(  %s, INTERVAL 1 
                DAY ) AND Party_id =%s GROUP BY ItemID)CB
                
on I.Item_id=CB.ItemID

left join (SELECT Item_id,SUM(BaseUnitQuantity) GRNQuantity,SUM(Amount) GRNValue
FROM T_GRNs JOIN TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
WHERE GRNDate = %s AND Customer_id = %s GROUP BY Item_id)GRN

on I.Item_id=GRN.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) InvoiveQuantity,SUM(Amount) SaleValue
FROM T_Invoices JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
WHERE InvoiceDate = %s AND Party_id = %s GROUP BY Item_id)Invoice

on I.Item_id=Invoice.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) SalesReturnQuantity,sum(Amount) SalesReturnValue
FROM T_PurchaseReturn join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id      
WHERE ReturnDate = %s AND Party_id = %s and TC_PurchaseReturnItems.ItemReason_id in(SELECT DefaultValue FROM M_Settings where id=14) GROUP BY Item_id)SalesReturn

on I.Item_id=SalesReturn.Item_id

left join (SELECT Item_id,SUM(BaseUnitQuantity) PurchesReturnQuantity,sum(Amount) PurchesReturnValue   
FROM T_PurchaseReturn join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id      
WHERE ReturnDate = %s AND Customer_id = %s  GROUP BY Item_id)PurchesReturn
on I.Item_id=PurchesReturn.Item_id

Left join (Select Item_id,SUM(BaseUnitQuantity)StockEntry  from T_Stock where IsStockAdjustment=0 and StockDate= DATE_SUB(  %s, INTERVAL 1 DAY ) AND Party_id=%s GROUP BY Item_id)StockEntry 
ON I.Item_id=StockEntry.Item_id

left join (SELECT Item_id,sum(Difference)StockAdjustmentQTY FROM T_Stock where IsStockAdjustment=1 and StockDate = %s and Party_id= %s group by Item_id)StockAdjustment 
on I.Item_id=StockAdjustment.Item_id

left join (SELECT Item_id,sum(BaseUnitQuantity)ActualStock FROM T_Stock where IsStockAdjustment=0 and StockDate = %s and Party_id= %s group by Item_id)ActualStock
on I.Item_id=ActualStock.Item_id

)R
where 
OpeningBalance!=0 OR GRN!=0 OR Sale!=0 OR PurchaseReturn != 0 OR SalesReturn !=0 OR StockAdjustment!=0 ''',
                                                                    ([Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party]))

                # print(StockProcessQuery)
                serializer = StockProcessingReportSerializer(
                    StockProcessQuery, many=True).data
                # print(serializer)
                for a in serializer:

                    stock = O_DateWiseLiveStock(StockDate=Date, OpeningBalance=a["OpeningBalance"], GRN=a["GRN"], Sale=a["Sale"], PurchaseReturn=a["PurchaseReturn"], SalesReturn=a["SalesReturn"], ClosingBalance=a[
                                                "ClosingBalance"], ActualStock=0, StockAdjustment=a["StockAdjustment"], Item_id=a["ItemID"], Unit_id=a["UnitID"], Party_id=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                    stock.save()
                current_date += timedelta(days=1)
            # log_entry = create_transaction_logNew(request, Orderdata, Party, '', 209, 0, start_date_str, end_date_str, 0)
            # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Process Successfully', 'Data': []})

    except Exception as e:
        pass
        # log_entry = create_transaction_logNew(request, 0, 0, 'StockProcessing:'+str(Exception(e)), 33, 0)
        # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})