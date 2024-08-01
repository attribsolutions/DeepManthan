from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew
from FoodERPApp.models import CustomPrint
from ..models import *
from datetime import datetime, timedelta


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

(Select Item_id,M_Items.BaseUnitID_id UnitID  from FoodERP.MC_PartyItems join FoodERP.M_Items on M_Items.id=MC_PartyItems.Item_id where Party_id=%s)I

left join (SELECT IFNULL(Item,0) ItemID, sum(ClosingBalance)ClosingBalance FROM SweetPOS.O_SPOSDateWiseLiveStock WHERE StockDate = DATE_SUB(  %s, 
INTERVAL 1
                                        DAY ) AND Party =%s GROUP BY ItemID)CB

on I.Item_id=CB.ItemID

left join (SELECT Item_id,SUM(BaseUnitQuantity) GRNQuantity,SUM(Amount) GRNValue
FROM FoodERP.T_GRNs JOIN FoodERP.TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
WHERE GRNDate = %s AND Customer_id = %s GROUP BY Item_id)GRN

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
                            stock = O_SPOSDateWiseLiveStock(StockDate=Date, OpeningBalance=a.OpeningBalance, GRN=a.GRN, Sale=a.Sale, PurchaseReturn=a.PurchaseReturn, SalesReturn=a.SalesReturn, ClosingBalance=a.ClosingBalance, ActualStock=0, StockAdjustment=a.StockAdjustment, Item=a.ItemID, Unit=a.UnitID, Party=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                            stock.save()
                        if(a.ClosingBalance == 0) :
                            stockout = T_SPOSStockOut(StockDate=Date, Item=a.ItemID, Party=Party, CreatedBy=0)
                            stockout.save()    
                    
                    current_date += timedelta(days=1)
                log_entry = create_transaction_logNew(request, Orderdata, Party, 'Stock Process Successfully', 209, 0, start_date_str, end_date_str, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Process Successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
