
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Items import ItemReportSerializer
from SweetPOS.models import *
from ..Serializer.S_Parties import M_PartiesSerializerSecond
from ..Views.V_CommFunction import *
from ..Views.V_CommFunction import GetOpeningBalance, UnitwiseQuantityConversion, RateCalculationFunction
from ..Serializer.S_Invoices import InvoiceSerializerSecond

from ..Serializer.S_Reports import *
from ..models import *
from datetime import datetime, timedelta

class PartyLedgerReportView(CreateAPIView):  
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Party = Orderdata['Party']

                query = T_Invoices.objects.raw('''SELECT
    1 id,InvoiceDate,BillNo,BankName,BranchName,ChequeDate,DocumentNo,ReceiptMode,InvoiceAmount,TotalTCS,
    ReceiptAmt,CashReceiptAmt,DebitNote,CreditNote,Flag,BasicAmount,BA5,BA12,BA18,GA5,GA12,GA18,Description
FROM
    (
        (   
            SELECT InvoiceDate,BillNo,BankName,BranchName,ChequeDate,DocumentNo,ReceiptMode,InvoiceAmount,
            TotalTCS,ReceiptAmt,CashReceiptAmt,Flag,DebitNote,CreditNote,ifnull(BasicAmount,0) AS BasicAmount,
            ifnull(BA5,0) AS BA5,ifnull(BA12,0) AS BA12,ifnull(BA18,0) AS BA18,ifnull(GA5,0) AS GA5,
            ifnull(GA12,0) AS GA12,ifnull(GA18,0) AS GA18,Description
            
            FROM
                (SELECT InvoiceDate,T_Invoices.id,FullInvoiceNumber BillNo,"" AS BankName,"" AS BranchName,
                "" AS ChequeDate,"" AS DocumentNo,"" AS ReceiptMode,GrandTotal InvoiceAmount,TCSAmount TotalTCS,
                0 AS ReceiptAmt,0 AS CashReceiptAmt,1 AS Flag,0 AS DebitNote,0 AS CreditNote,"" AS Description
                FROM T_Invoices WHERE InvoiceDate BETWEEN %s AND %s AND Party_id = %s AND Customer_id = %s) a
                
                LEFT JOIN 
                
                (SELECT Invoice_id,SUM(BasicAmount) AS BasicAmount,
                SUM(CASE WHEN GSTPercentage = 5 THEN BasicAmount ELSE 0 END) AS BA5,
                SUM(CASE WHEN GSTPercentage = 12 THEN BasicAmount ELSE 0 END) AS BA12,
                SUM(CASE WHEN GSTPercentage = 18 THEN BasicAmount ELSE 0 END) AS BA18,
                SUM(CASE WHEN GSTPercentage = 5 THEN GSTAmount ELSE 0 END) AS GA5,
                SUM(CASE WHEN GSTPercentage = 12 THEN GSTAmount ELSE 0 END) AS GA12,
                SUM(CASE WHEN GSTPercentage = 18 THEN GSTAmount ELSE 0 END) AS GA18
                FROM TC_InvoiceItems GROUP BY Invoice_id) b 
            
            ON a.id = b.Invoice_id
        )

        UNION
            SELECT ReceiptDate InvoiceDate,FullReceiptNumber BillNo,M_Bank.Name AS BankName,MC_PartyBanks.BranchName AS BranchName,
            ChequeDate ChequeDate,DocumentNo DocumentNo,M_GeneralMaster.Name AS ReceiptMode,0 AS InvoiceAmount,0 as TotalTCS,
            CASE WHEN ReceiptMode_id = 31 THEN 0 ELSE AmountPaid END ReceiptAmt,
            CASE WHEN ReceiptMode_id = 31 THEN AmountPaid ELSE 0 END CashReceiptAmt,
            2 AS Flag,0 AS DebitNote,0 AS CreditNote,0 AS BasicAmount,0 AS BA5,0 AS BA12,0 AS BA18,0 AS GA5,0 AS GA12,
            0 AS GA18,Description
            FROM T_Receipts
            LEFT JOIN MC_PartyBanks ON MC_PartyBanks.id = T_Receipts.Bank_id
            LEFT JOIN M_Bank ON M_Bank.id = MC_PartyBanks.Bank_id
            INNER JOIN M_GeneralMaster ON M_GeneralMaster.id = T_Receipts.ReceiptMode_id
            WHERE ReceiptDate BETWEEN %s AND %s
            AND T_Receipts.Party_id = %s
            AND T_Receipts.Customer_id = %s

        UNION
            SELECT CRDRNoteDate InvoiceDate,FullNoteNumber BillNo,"" AS BankName,"" AS BranchName,"" AS ChequeDate,
            "" AS DocumentNo,"" AS ReceiptMode,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 or T_CreditDebitNotes.NoteType_id = 40 THEN T_CreditDebitNotes.GrandTotal ELSE 0 END) AS InvoiceAmount,
            0 AS TotalTCS,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 or T_CreditDebitNotes.NoteType_id = 40 THEN 0 ELSE T_CreditDebitNotes.GrandTotal END) ReceiptAmt,
            0 AS CashReceiptAmt,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 or T_CreditDebitNotes.NoteType_id = 40 THEN 3 ELSE 4 END) AS Flag,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38  OR T_CreditDebitNotes.NoteType_id =40 THEN T_CreditDebitNotes.GrandTotal ELSE 0 END) AS DebitNote,
            (CASE WHEN T_CreditDebitNotes.NoteType_id = 38 OR T_CreditDebitNotes.NoteType_id =40 THEN 0 ELSE T_CreditDebitNotes.GrandTotal END) CreditNote,
            0 AS BasicAmount,0 AS BA5, 0 AS BA12, 0 AS BA18, 0 AS GA5, 0 AS GA12, 0 AS GA18, "" AS Description
            FROM T_CreditDebitNotes
            WHERE
             T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND Party_id = %s
            AND Customer_id = %s and IsDeleted=0

        UNION
            SELECT Date InvoiceDate,"" BillNo,"" AS BankName,"" AS BranchName,"" AS ChequeDate,
            "" AS DocumentNo,"" AS ReceiptMode,
            OpeningBalanceAmount AS InvoiceAmount,0 AS TotalTCS,
            0 AS ReceiptAmt,0 AS CashReceiptAmt,
            0 AS Flag,
            0 AS DebitNote,
            0 AS CreditNote,
            0 AS BasicAmount,0 AS BA5, 0 AS BA12, 0 AS BA18, 0 AS GA5, 0 AS GA12, 0 AS GA18, "OpeningBalance" AS Description
            FROM MC_PartySubPartyOpeningBalance
            WHERE
             MC_PartySubPartyOpeningBalance.Date BETWEEN %s AND %s AND Party_id = %s
            AND SubParty_id = %s   

    ) q
            ORDER BY InvoiceDate , Flag , BillNo ''', [FromDate, ToDate, Party, Customer, FromDate, ToDate, Party, Customer, FromDate, ToDate, Party, Customer,FromDate, ToDate, Party, Customer])

                if not query:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'Report Not Found', 206, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PartyLedgerSerializedata = PartyLedgerReportSerializer(
                        query, many=True).data
                    PartyLedgerData = list()
                    PartyLedgerItemDetails = list()
                    date_format = "%Y-%m-%d"

                    # Convert the string to a date object
                    date_object = datetime.strptime(FromDate, date_format).date()
                    previous_date = date_object - timedelta(days=1)
                    Opening = GetOpeningBalance(Party, Customer, previous_date)
                    Closing = GetOpeningBalance(Party, Customer, ToDate)
                    temp = 0
                    TaxFreeSale = 0
                    TotalTaxableSale = 0
                    TaxableSale5 = 0
                    TaxableSale12 = 0
                    TaxableSale18 = 0
                    GSTAmount5 = 0
                    GSTAmount12 = 0
                    GSTAmount18 = 0
                    TotalCreditNote = 0
                    TotalDebitNote = 0
                    TotalTCS = 0
                    for a in PartyLedgerSerializedata:
                        Openingba=Opening
                        if a['Flag'] == 0 :
                            temp=0
                            Openingba= 0
                        if temp == 0:
                            temp = (float(Openingba) + float(a['InvoiceAmount'])) - (
                                float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        else:
                            temp = (temp + float(a['InvoiceAmount'])) - \
                                (float(a['ReceiptAmt']) +
                                 float(a['CashReceiptAmt']))

                        TaxFreeSale = 0.0
                        TotalTaxableSale = TotalTaxableSale + \
                            float(a["BasicAmount"])
                        TaxableSale5 = TaxableSale5 + float(a["BA5"])
                        TaxableSale12 = TaxableSale12 + float(a["BA12"])
                        TaxableSale18 = TaxableSale18 + float(a["BA18"])
                        GSTAmount5 = GSTAmount5 + float(a["GA5"])
                        GSTAmount12 = GSTAmount12 + float(a["GA12"])
                        GSTAmount18 = GSTAmount18 + float(a["GA18"])
                        TotalCreditNote = TotalCreditNote + \
                            float(a["CreditNote"])
                        TotalDebitNote = TotalDebitNote + float(a["DebitNote"])
                        TotalTCS = TotalTCS + float(a["TotalTCS"])
                        if a['BankName'] is None:
                            BankName = ''
                        else:
                            BankName = str(a['BankName'])
                        if a['BranchName'] is None:
                            BranchName = ''
                        else:
                            BranchName = str(a['BranchName'])
                        if a['DocumentNo'] is None:
                            DocumentNo = ''
                        else:
                            DocumentNo = str(a['DocumentNo'])
                        if a['ReceiptMode'] is None:
                            ReceiptMode = ''
                        else:
                            ReceiptMode = str(a['ReceiptMode'])

                        if a['Description'] is None or not a['Description']:

                            Description = ''
                        else:

                            Description = '(' + str(a['Description']) + ')'

                        PartyLedgerItemDetails.append({
                            "Date": a['InvoiceDate'],
                            "DocumentNO": a['BillNo'],
                            "Particular": BankName+''+BranchName+''+DocumentNo+''+ReceiptMode + '' + Description,
                            "Amount": a['InvoiceAmount'],
                            "RecieptAmount": float(a['ReceiptAmt']) + float(a['CashReceiptAmt']),
                            "Cash": 0,
                            "Balance": float(temp),

                        })
                    q1 = M_Parties.objects.filter(
                        id=Party).values("Name", "PAN", "GSTIN")
                    q2 = M_Parties.objects.filter(
                        id=Customer).values("Name", "PAN", "GSTIN")
                    PartyLedgerData.append({
                        "FormDate": FromDate,
                        "ToDate": ToDate,
                        "Distributor": q1[0]['Name'],
                        "DistributorGSTIN": q1[0]["GSTIN"],
                        "DistributorPAN": q1[0]['PAN'],
                        "CustomerName": q2[0]['Name'],
                        "CustomerGSTIN":  q2[0]["GSTIN"],
                        "CustomerPAN": q2[0]["PAN"],
                        "Open": Opening,
                        "Close": Closing,
                        "TaxFreeSale": TaxFreeSale,
                        "TotalTaxableSale": TotalTaxableSale,
                        "TaxableSale5": TaxableSale5,
                        "TaxableSale12": TaxableSale12,
                        "TaxableSale18": TaxableSale18,
                        "GSTAmount5": GSTAmount5,
                        "GSTAmount12": GSTAmount12,
                        "GSTAmount18": GSTAmount18,
                        "TotalCreditNote": TotalCreditNote,
                        "TotalDebitNote": TotalDebitNote,
                        "TotalTCS": TotalTCS,
                        "InvoiceItems": PartyLedgerItemDetails
                    })
                log_entry = create_transaction_logNew(request, Orderdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 206, 0, FromDate, ToDate, Customer)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyLedgerData})
        except Exception as e:
            log_entry = create_transaction_logNew( request, Orderdata, 0, 'PartyLedgerReport'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class GenericSaleView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Genericdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Genericdata['FromDate']
                ToDate = Genericdata['ToDate']
                Party = Genericdata['Party']
                Party_list = Party.split(",")

                Genericdataquery = T_Invoices.objects.raw('''SELECT TC_InvoiceItems.id, A.SAPPartyCode SAPPartyID, T_Invoices.Party_id AS PartyID,A.Name PartyName, X.Name PartyType, T_Invoices.ImportFromExcel,  T_Invoices.FullInvoiceNumber,
T_Invoices.InvoiceDate,T_Invoices.Customer_id AS CustomerID,B.Name CustomerName, Y.Name CustomeType, M_Drivers.Name DriverName,
M_Vehicles.VehicleNumber VehicleNo,TC_InvoiceItems.Item_id AS ItemID,M_Items.Name ItemName,C_Companies.Name CompanyName,
M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,ROUND(TC_InvoiceItems.QtyInNo, 2) AS QtyInNo,ROUND(TC_InvoiceItems.QtyInKg, 2) AS QtyInKg,ROUND(TC_InvoiceItems.QtyInBox, 2) AS QtyInBox,
TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate + ((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage) / 100)) WithGSTRate,
M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType,TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,
TC_InvoiceItems.BasicAmount AS TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,
TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,
TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Orders.FullOrderNumber,T_Orders.OrderDate,T_Invoices.TCSAmount,
T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,M_Group.Name AS `Group`, MC_SubGroup.Name AS SubGroup, 
M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster, TC_InvoiceItems.BatchCode AS BatchNo , TC_InvoiceItems.BatchDate, M_Items.SAPItemCode SAPItemID 
FROM TC_InvoiceItems 
JOIN T_Invoices ON T_Invoices.id = TC_InvoiceItems.Invoice_id 
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = T_Invoices.Customer_id and MC_PartySubParty.Party_id=T_Invoices.Party_id
left JOIN TC_InvoicesReferences ON TC_InvoicesReferences.Invoice_id = T_Invoices.id 
left JOIN T_Orders ON T_Orders.id = TC_InvoicesReferences.Order_id
 JOIN M_Parties A ON A.id = T_Invoices.Party_id 
 JOIN M_Parties B ON B.id = T_Invoices.Customer_id 
 JOIN M_PartyType X on A.PartyType_id = X.id 
 JOIN M_PartyType Y on B.PartyType_id = Y.id 
 JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id 
 JOIN C_Companies ON C_Companies.id = M_Items.Company_id 
 left JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TC_InvoiceItems.GST_id 
 JOIN MC_ItemUnits ON MC_ItemUnits.id = TC_InvoiceItems.Unit_id 
 JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id 

 LEFT JOIN M_Drivers ON M_Drivers.id = T_Invoices.Driver_id 
 LEFT JOIN M_Vehicles ON M_Vehicles.id = T_Invoices.Vehicle_id 
 left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id  and MC_ItemGroupDetails.GroupType_id=1
 LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
 LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
 LEFT JOIN M_PartyDetails on  A.id=M_PartyDetails.Party_id AND M_PartyDetails.Group_id is null
 LEFT JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id 
 LEFT JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id 
 WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Party_id IN %s''',([FromDate,ToDate,Party_list]))
                if Genericdataquery:
                    GenericSaleData = list()
                    GenericSaleSerializer = GenericSaleReportSerializer(
                        Genericdataquery, many=True).data

                    # GenericSaleData.append({"GenericSaleDetails" : GenericSaleSerializer})
                    log_entry = create_transaction_logNew(request, Genericdata, 0, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 207, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': GenericSaleSerializer})
                else:
                    log_entry = create_transaction_logNew(request, Genericdata, 0, 'Report Not available', 207, 0,  FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Genericdata, 0, 'GenericSale:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class RetailerDataView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Retailerdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = Retailerdata['Party']
                if(Party == 0):
                    query = M_Parties.objects.raw('''SELECT M_Parties.id, Supplier.Name SupplierName,M_Parties.Name, M_Parties.isActive, MC_PartySubParty.CreatedOn AS PartyCreation, M_Parties.Email, M_Parties.MobileNo, M_Parties.AlternateContactNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_Parties.GSTIN, M_Parties.PAN,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Routes.Name RouteName,C_Companies.Name CompanyName,M_PartyType.Name PartyTypeName, M_PriceList.Name PriceListName, M_Parties.Latitude, M_Parties.Longitude,M_Parties.SAPPartyCode,M_Routes.id Routeid,Supplier.id Supplierid,  M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
FROM MC_PartySubParty
JOIN M_Parties Supplier  ON Supplier.id= MC_PartySubParty.Party_id
JOIN M_Parties  ON M_Parties.id= MC_PartySubParty.SubParty_id
JOIN MC_PartyAddress ON MC_PartyAddress.Party_id =M_Parties.id AND  MC_PartyAddress.IsDefault=1
JOIN M_PartyType ON M_PartyType.id = M_Parties.PartyType_id AND M_PartyType.IsRetailer=1
JOIN M_States ON M_States.id = M_Parties.State_id
JOIN M_Districts ON M_Districts.id = M_Parties.District_id
LEFT JOIN M_Cities ON M_Cities.id=M_Parties.City_id
LEFT JOIN M_PriceList ON M_PriceList.id = M_Parties.PriceList_id
LEFT JOIN C_Companies ON C_Companies.id = M_Parties.Company_id
Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN M_PartyDetails on  Supplier.Id=M_PartyDetails.Party_id
JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id
JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
''')
                else:
                    query = M_Parties.objects.raw('''SELECT M_Parties.id, Supplier.Name SupplierName,M_Parties.Name, M_Parties.isActive, MC_PartySubParty.CreatedOn AS PartyCreation, M_Parties.Email, M_Parties.MobileNo, M_Parties.AlternateContactNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,MC_PartyAddress.FSSAINo,MC_PartyAddress.FSSAIExipry,M_Parties.GSTIN, M_Parties.PAN,M_States.Name StateName,M_Districts.Name DistrictName,M_Cities.Name CityName,M_Routes.Name RouteName,C_Companies.Name CompanyName,M_PartyType.Name PartyTypeName, M_PriceList.Name PriceListName, M_Parties.Latitude, M_Parties.Longitude,M_Parties.SAPPartyCode,M_Routes.id Routeid,Supplier.id Supplierid,  M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
FROM MC_PartySubParty
JOIN M_Parties Supplier  ON Supplier.id= MC_PartySubParty.Party_id
JOIN M_Parties  ON M_Parties.id= MC_PartySubParty.SubParty_id
JOIN MC_PartyAddress ON MC_PartyAddress.Party_id =M_Parties.id AND  MC_PartyAddress.IsDefault=1
JOIN M_PartyType ON M_PartyType.id = M_Parties.PartyType_id AND M_PartyType.IsRetailer=1
JOIN M_States ON M_States.id = M_Parties.State_id
JOIN M_Districts ON M_Districts.id = M_Parties.District_id
LEFT JOIN M_Cities ON M_Cities.id=M_Parties.City_id
LEFT JOIN M_PriceList ON M_PriceList.id = M_Parties.PriceList_id
LEFT JOIN C_Companies ON C_Companies.id = M_Parties.Company_id
Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN M_PartyDetails on  Supplier.Id=M_PartyDetails.Party_id
JOIN M_Cluster On M_PartyDetails.Cluster_id=M_Cluster.id
JOIN M_SubCluster on M_PartyDetails.SubCluster_id=M_SubCluster.Id
WHERE MC_PartySubParty.Party_id=%s''', [Party])

                if query:
                    RetailerExportData = list()
                    RetailerExportSerializer = RetailerDataExportSerializer(
                        query, many=True).data
                    for retailer in RetailerExportSerializer:
                        PartyDateTime =datetime.strptime(retailer['PartyCreation'], "%Y-%m-%d %H:%M:%S")
                        PartyCreation = PartyDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        retailer['PartyCreation'] = PartyCreation
                        
                    RetailerExportData.append(
                        {"ReportExportSerializerDetails": RetailerExportSerializer})
                    log_entry = create_transaction_logNew(
                        request, Retailerdata, Party, '', 208, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': RetailerExportData[0]})
                else:
                    log_entry = create_transaction_logNew(
                        request, Retailerdata, Party, 'Report Not available ', 208, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Retailerdata, 0, 'RetailerData:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

# ================================Stock Processing ================================


class StockProcessingView(CreateAPIView):
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
                    # CustomPrint(Date)
                    # StockDeleteQuery  = O_DateWiseLiveStock.objects.raw('''DELETE FROM O_DateWiseLiveStock WHERE StockDate=%s AND Party_id=%s''',([Date],[Party]))
                    StockDeleteQuery = O_DateWiseLiveStock.objects.filter(
                        Party_id=Party, StockDate=Date)
                    StockDeleteQuery.delete()
                    # CustomPrint(StockDeleteQuery.query)
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
WHERE ReturnDate = %s AND Customer_id = %s and ((TC_PurchaseReturnItems.ItemReason_id IN (SELECT DefaultValue FROM M_Settings WHERE id = 14) and T_PurchaseReturn.Mode =3) OR(T_PurchaseReturn.Mode =2)) GROUP BY Item_id)PurchesReturn
on I.Item_id=PurchesReturn.Item_id

Left join (Select Item_id,SUM(BaseUnitQuantity)StockEntry  from T_Stock where IsDeleted=0 and  IsStockAdjustment=0 and StockDate= DATE_SUB(  %s, INTERVAL 1 DAY ) AND Party_id=%s GROUP BY Item_id)StockEntry 
ON I.Item_id=StockEntry.Item_id

left join (SELECT Item_id,sum(Difference)StockAdjustmentQTY FROM T_Stock where IsDeleted=0 and IsStockAdjustment=1 and StockDate = %s and Party_id= %s group by Item_id)StockAdjustment 
on I.Item_id=StockAdjustment.Item_id

left join (SELECT Item_id,sum(BaseUnitQuantity)ActualStock FROM T_Stock where IsDeleted=0 and IsStockAdjustment=0 and StockDate = %s and Party_id= %s group by Item_id)ActualStock
on I.Item_id=ActualStock.Item_id

)R
where 
OpeningBalance!=0 OR GRN!=0 OR Sale!=0 OR PurchaseReturn != 0 OR SalesReturn !=0 OR StockAdjustment!=0 ''',
                                                                        ([Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party], [Date], [Party]))

                    # CustomPrint(StockProcessQuery)
                    serializer = StockProcessingReportSerializer(
                        StockProcessQuery, many=True).data
                    # CustomPrint(serializer)
                    for a in serializer:

                        stock = O_DateWiseLiveStock(StockDate=Date, OpeningBalance=a["OpeningBalance"], GRN=a["GRN"], Sale=a["Sale"], PurchaseReturn=a["PurchaseReturn"], SalesReturn=a["SalesReturn"], ClosingBalance=a[
                                                    "ClosingBalance"], ActualStock=0, StockAdjustment=a["StockAdjustment"], Item_id=a["ItemID"], Unit_id=a["UnitID"], Party_id=Party, CreatedBy=0,  IsAdjusted=0, MRPValue=0)
                        stock.save()
                    current_date += timedelta(days=1)
                log_entry = create_transaction_logNew(request, Orderdata, Party, 'Stock Process Successfully', 209, 0, start_date_str, end_date_str, 0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Stock Process Successfully', 'Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew( request, Orderdata, 0, 'StockProcessing:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

# ======================================STOCK REPORT=================================


class StockReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Orderdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Unit = Orderdata['Unit']
                Party = Orderdata['Party']
                PartyNameQ = M_Parties.objects.filter(id=Party).values("Name")
                UnitName = M_Units.objects.filter(id=Unit).values("Name")
                unitname = UnitName[0]['Name']
                StockreportQuery = O_DateWiseLiveStock.objects.raw('''SELECT  1 as id,A.Item_id,A.Unit_id,
UnitwiseQuantityConversion(A.Item_id,ifnull(OpeningBalance,0),0,A.Unit_id,0,%s,0)OpeningBalance, 
UnitwiseQuantityConversion(A.Item_id,GRNInward,0,A.Unit_id,0,%s,0)GRNInward, 
UnitwiseQuantityConversion(A.Item_id,Sale,0,A.Unit_id,0,%s,0)Sale, 
UnitwiseQuantityConversion(A.Item_id,ClosingBalance,0,A.Unit_id,0,%s,0)ClosingBalance, 
UnitwiseQuantityConversion(A.Item_id,ActualStock,0,A.Unit_id,0,%s,0)ActualStock,
A.ItemName,
D.QuantityInBaseUnit,
UnitwiseQuantityConversion(A.Item_id,PurchaseReturn,0,A.Unit_id,0,%s,0)PurchaseReturn,
UnitwiseQuantityConversion(A.Item_id,SalesReturn,0,A.Unit_id,0,%s,0)SalesReturn,
UnitwiseQuantityConversion(A.Item_id,StockAdjustment,0,A.Unit_id,0,%s,0)StockAdjustment
,GroupTypeName,GroupName,SubGroupName,%s UnitName
FROM 
	
	( SELECT M_Items.id Item_id, M_Items.Name ItemName ,Unit_id,M_Units.Name UnitName ,SUM(GRN) GRNInward, SUM(Sale) Sale, SUM(PurchaseReturn)PurchaseReturn,SUM(SalesReturn)SalesReturn,SUM(StockAdjustment)StockAdjustment,
    ifnull(M_GroupType.Name,'') GroupTypeName,ifnull(M_Group.Name,'') GroupName,ifnull(MC_SubGroup.Name,'') SubGroupName
	 FROM O_DateWiseLiveStock
	
	    JOIN M_Items ON M_Items.id=O_DateWiseLiveStock.Item_id 
        join M_Units on M_Units.id=O_DateWiseLiveStock.Unit_id
        left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id  and MC_ItemGroupDetails.GroupType_id=1
		left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
		left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
		left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id 
		 
		 WHERE StockDate BETWEEN %s AND %s AND Party_id=%s GROUP BY Item_id,M_GroupType.id,M_Group.id,MC_SubGroup.id) A 
		
		left JOIN (SELECT O_DateWiseLiveStock.Item_id, OpeningBalance FROM O_DateWiseLiveStock WHERE O_DateWiseLiveStock.StockDate = %s AND O_DateWiseLiveStock.Party_id=%s) B
		
		 ON A.Item_id = B.Item_id 
		
		 left JOIN (SELECT Item_id, ClosingBalance, ActualStock FROM O_DateWiseLiveStock WHERE StockDate = %s AND Party_id=%s) C
		 
		  ON A.Item_id = C.Item_id  
		
		LEFT JOIN (SELECT Item_id, SUM(BaseunitQuantity) QuantityInBaseUnit 
		FROM T_Stock 
		WHERE Party_id =%s AND StockDate BETWEEN %s AND %s 
		GROUP BY Item_id) D 		
		ON A.Item_id = D.Item_id ''', ([Unit], [Unit], [Unit], [Unit], [Unit], [Unit], [Unit], [Unit], [unitname], [FromDate], [ToDate], [Party], [FromDate], [Party], [ToDate], [Party], [Party], [FromDate], [ToDate]))
                serializer = StockReportSerializer(
                    StockreportQuery, many=True).data

                StockData = list()
                StockData.append({

                    "FromDate": FromDate,
                    "ToDate": ToDate,
                    "PartyName": PartyNameQ[0]["Name"],
                    "StockDetails": serializer

                })

                if StockreportQuery:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 210, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': StockData})
                else:
                    log_entry = create_transaction_logNew(request, Orderdata, Party, 'Recort Not Found', 210, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Orderdata, 0, 'StockReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


# select I.Item_id,I.ItemName,InvoiveQuantity,InvoiceMRP,GRNQuantity,GRNMRP,StockQuantity,StockMRP,SalesReturnQuantity,SalesReturnMRP,PurchesReturnQuantity,PurchesReturnMRP from

# (Select Item_id ,M_Items.Name ItemName from MC_PartyItems join M_Items on M_Items.id=MC_PartyItems.Item_id where Party_id=14)I

# left join
# (SELECT
#     Item_id,
#     MRPValue GRNMRP,
#     SUM(BaseUnitQuantity) GRNQuantity,
#     SUM(Amount) GRNValue
# FROM
#     T_GRNs
#         JOIN
#     TC_GRNItems ON TC_GRNItems.GRN_id = T_GRNs.id
# WHERE
#     GRNDate = '2023-07-21' AND Customer_id = 14
# GROUP BY Item_id,MRPValue)b


# on I.Item_id=b.Item_id

# left join
# (SELECT
#     Item_id,
#     MRPValue InvoiceMRP,
#     SUM(BaseUnitQuantity) InvoiveQuantity,
#     SUM(Amount) SaleValue
# FROM
#     T_Invoices
#         JOIN
#     TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
# WHERE
#     InvoiceDate = '2023-07-21'AND Party_id = 14
# GROUP BY Item_id,MRPValue)a
# on I.Item_id=a.Item_id  and b.GRNMRP=a.InvoiceMRP
# left join


# (SELECT
#     Item_id,
#     MRPValue StockMRP,
#     SUM(BaseUnitQuantity) StockQuantity
# FROM
#     T_Stock
# WHERE
#     StockDate = '2023-07-21' AND Party_id = 14
# GROUP BY Item_id,MRPValue)c

# on I.Item_id=c.Item_id and b.GRNMRP=c.StockMRP
# left join

# (SELECT
#     Item_id,
#     MRPValue SalesReturnMRP,
#     SUM(BaseUnitQuantity) SalesReturnQuantity,
#     sum(Amount) SalesReturnValue
# FROM
#     T_PurchaseReturn
#     join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
# WHERE
#     ReturnDate = '2023-07-21' AND Party_id = 14
# GROUP BY Item_id,MRPValue)d

# on I.Item_id=d.Item_id and b.GRNMRP=d.SalesReturnMRP
# left join
# (SELECT
#     Item_id,
#     MRPValue PurchesReturnMRP,
#     SUM(BaseUnitQuantity) PurchesReturnQuantity,
#     sum(Amount) PurchesReturnValue
# FROM
#     T_PurchaseReturn
#     join TC_PurchaseReturnItems on TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
# WHERE
#     ReturnDate = '2023-07-21' AND Customer_id = 14
# GROUP BY Item_id,MRPValue)e
# on I.Item_id=e.Item_id and b.GRNMRP=e.PurchesReturnMRP

class PurchaseGSTReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Customer = Reportdata['Party']
                GSTRatewise = Reportdata['GSTRatewise']

                if GSTRatewise == 1:

                    query = TC_GRNReferences.objects.raw(
                        '''SELECT 1 As id, GSTPercentage,  SUM(BasicAmount) TaxableValue, SUM(CGST) CGST, SUM( SGST) SGST, SUM( IGST) IGST, SUM(GSTAmount) GSTAmount, SUM(Amount) TotalValue   FROM TC_GRNReferences JOIN T_Invoices ON T_Invoices.id =TC_GRNReferences.Invoice_id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Customer_id= %s and DeletedFromSAP=0 GROUP BY TC_InvoiceItems.GSTPercentage''', ([FromDate], [ToDate], [Customer]))
                    if query:
                        PurchaseGSTRateWiseData = list()
                        PurchaseGSTRateWiseSerializer = PurchaseGSTRateWiseReportSerializer(
                            query, many=True).data
                        PurchaseGSTRateWiseData.append(
                            {"PurchaseGSTRateWiseDetails": PurchaseGSTRateWiseSerializer})
                        log_entry = create_transaction_logNew(request, Reportdata, Customer, 'From:'+str(
                            FromDate)+'To:'+str(ToDate), 211, 0, FromDate, ToDate, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PurchaseGSTRateWiseData[0]})
                    else:
                        log_entry = create_transaction_logNew(
                            request, Reportdata, Customer, 'Report Not available', 211, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
                else:
                    query = TC_GRNReferences.objects.raw(
                        '''SELECT 1 AS id,M_Parties.Name,InvoiceNumber,FullInvoiceNumber,InvoiceDate,SUM(CGSTPercentage + SGSTPercentage + IGSTPercentage) GSTRate,GSTPercentage,SUM(BasicAmount) TaxableValue,SUM(CGST) CGST,SUM(SGST) SGST,SUM(IGST) IGST,SUM(GSTAmount) GSTAmount,SUM(TC_InvoiceItems.DiscountAmount) DiscountAmount,SUM(Amount) TotalValue FROM TC_GRNReferences JOIN T_Invoices ON T_Invoices.id = TC_GRNReferences.Invoice_id JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id JOIN M_Parties ON T_Invoices.Party_id = M_Parties.id WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.Customer_id =%s and DeletedFromSAP=0 GROUP BY M_Parties.id, T_Invoices.InvoiceNumber, T_Invoices.FullInvoiceNumber, T_Invoices.InvoiceDate, TC_InvoiceItems.GSTPercentage''', ([FromDate], [ToDate], [Customer]))
                    if query:
                        PurchaseGSTSerializer = PurchaseGSTReportSerializer(
                            query, many=True).data
                        # CustomPrint(PurchaseGSTSerializer)
                        PurchaseGSTData = list()
                        PurchaseGSTData.append(
                            {"PurchaseGSTDetails": PurchaseGSTSerializer})
                        log_entry = create_transaction_logNew(request, Reportdata, Customer, 'From:'+str(
                            FromDate)+'To:'+str(ToDate), 211, 0, FromDate, ToDate, 0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PurchaseGSTData[0]})
                    else:
                        log_entry = create_transaction_logNew(request, Reportdata, Customer, '', 211, 0)
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'PurchaseGSTReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class InvoiceDateExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Customer = Reportdata['Customer']
                Employee = Reportdata['Employee']
                Mode = Reportdata['Mode']
                if Employee > 0:
                    EmpPartys = MC_EmployeeParties.objects.raw(
                        '''select EmployeeParties(%s) id''', [Employee])
                    for row in EmpPartys:
                        p = row.id
                    PartyIDs = p.split(",")

                if (Mode == 1):

                    Invoicequery ='''SELECT TC_InvoiceItems.id,T_Invoices.Party_id AS SupplierID,A.Name SupplierName,T_Invoices.FullInvoiceNumber As InvoiceNumber,T_Invoices.InvoiceDate,T_Invoices.Customer_id As CustomerID,B.Name CustomerName,TC_InvoiceItems.Item_id AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,TC_InvoiceItems.QtyInNo,TC_InvoiceItems.QtyInKg,TC_InvoiceItems.QtyInBox,TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate +((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType, TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,TC_InvoiceItems.BasicAmount As TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Invoices.TCSAmount,T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,'' AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_InvoiceUploads.Irn, TC_InvoiceUploads.AckNo,TC_InvoiceUploads.EwayBillNo, M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName
                                            FROM TC_InvoiceItems
                                            JOIN T_Invoices ON T_Invoices.id =TC_InvoiceItems.Invoice_id
                                            LEFT JOIN TC_InvoicesReferences ON TC_InvoicesReferences.Invoice_id=T_Invoices.id
                                            LEFT JOIN T_Orders ON T_Orders.id = TC_InvoicesReferences.Order_id
                                            
                                            JOIN M_Parties A ON A.id= T_Invoices.Party_id
                                            JOIN M_Parties B ON B.id = T_Invoices.Customer_id
                                            JOIN M_States ON M_States.id = B.State_id
                                            JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
                                            JOIN C_Companies ON C_Companies.id = M_Items.Company_id
                                            JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                                            JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
                                            JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
                                            JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_Invoices.Customer_id 
                                            LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
                                            LEFT JOIN TC_InvoiceUploads on TC_InvoiceUploads.Invoice_id = T_Invoices.id
                                            left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
                                            LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                                            LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
                                            WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s '''

                    if Party == 0:
                        if Employee == 0:
                            Invoicequery += " "
                        else:
                            Invoicequery += "and MC_PartySubParty.Party_id in %s"
                    else:
                        Invoicequery += " and MC_PartySubParty.Party_id=%s"

                    if Party == 0:
                        if Employee == 0:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate])
                        else:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate, PartyIDs])
                    else:

                        InvoiceQueryresults = T_Invoices.objects.raw(Invoicequery,[FromDate,ToDate,Party])      
                else: 
                    Invoicequery= '''SELECT TC_InvoiceItems.id,T_Invoices.Party_id AS SupplierID,A.Name SupplierName,T_Invoices.FullInvoiceNumber As InvoiceNumber,T_Invoices.InvoiceDate,T_Invoices.Customer_id As CustomerID,B.Name CustomerName,TC_InvoiceItems.Item_id AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_InvoiceItems.MRPValue AS MRP,TC_InvoiceItems.QtyInNo,TC_InvoiceItems.QtyInKg,TC_InvoiceItems.QtyInBox,TC_InvoiceItems.Rate AS BasicRate,(TC_InvoiceItems.Rate +((TC_InvoiceItems.Rate * TC_InvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_InvoiceItems.DiscountType, TC_InvoiceItems.Discount,TC_InvoiceItems.DiscountAmount,TC_InvoiceItems.BasicAmount As TaxableValue,TC_InvoiceItems.CGST,TC_InvoiceItems.CGSTPercentage,TC_InvoiceItems.SGST,TC_InvoiceItems.SGSTPercentage,TC_InvoiceItems.IGST,TC_InvoiceItems.IGSTPercentage,TC_InvoiceItems.GSTPercentage,TC_InvoiceItems.GSTAmount,TC_InvoiceItems.Amount AS TotalValue,T_Invoices.TCSAmount,T_Invoices.RoundOffAmount,T_Invoices.GrandTotal,'' AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_InvoiceUploads.Irn, TC_InvoiceUploads.AckNo,TC_InvoiceUploads.EwayBillNo, M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName
    FROM TC_InvoiceItems
    JOIN T_Invoices ON T_Invoices.id =TC_InvoiceItems.Invoice_id
    join TC_GRNReferences on TC_GRNReferences.Invoice_id = T_Invoices.id
    JOIN M_Parties A ON A.id= T_Invoices.Party_id
    JOIN M_Parties B ON B.id = T_Invoices.Customer_id
    JOIN M_States ON M_States.id = B.State_id
    JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
    JOIN C_Companies ON C_Companies.id = M_Items.Company_id
    JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
    JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
    JOIN M_GSTHSNCode ON M_GSTHSNCode.Item_id=TC_InvoiceItems.Item_id and M_GSTHSNCode.IsDeleted=0
    LEFT JOIN TC_InvoiceUploads on TC_InvoiceUploads.Invoice_id = T_Invoices.id
    left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
    LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
    LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
    WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s'''
                    
                    if Customer == 0:
                        if Employee == 0:
                            Invoicequery += " "
                        else:
                            Invoicequery += "AND  T_Invoices.Customer_id in %s"
                    else:
                        Invoicequery += " AND  T_Invoices.Customer_id=%s"

                    if Customer == 0:
                        if Employee == 0:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate])
                        else:
                            InvoiceQueryresults = T_Invoices.objects.raw(
                                Invoicequery, [FromDate, ToDate, PartyIDs])
                            
                    else:

                        InvoiceQueryresults = T_Invoices.objects.raw(Invoicequery,[FromDate,ToDate,Customer])
                        
                       
                if InvoiceQueryresults:

                    InvoiceExportData = list()
                    InvoiceExportSerializer = InvoiceDataExportSerializer(
                        InvoiceQueryresults, many=True).data
                    for b in InvoiceExportSerializer:

                        qur2 = M_Parties.objects.filter(id=b['CustomerID']).values('PriceList').distinct()
                        
                        query = M_PriceList.objects.values('id').filter(id__in=qur2)

                        Rate = RateCalculationFunction(0, b['FE2MaterialID'], 0, 0, 1, 0, query[0]['id']).RateWithGST()
                        
                        NoRate = float(Rate[0]['NoRatewithOutGST'])
                        InvoiceExportData.append({

                            
                            "SupplierID":b['SupplierID'],
                            "SupplierName":b['SupplierName'],
                            "InvoiceNumber":b['InvoiceNumber'],
                            "InvoiceDate":b['InvoiceDate'],
                            "CustomerID":b['CustomerID'],
                            "CustomerName":b['CustomerName'],
                            "FE2MaterialID":b['FE2MaterialID'],
                            "MaterialName":b['MaterialName'],
                            "CompanyName":b['CompanyName'],
                            "HSNCode":b['HSNCode'],
                            "MRP":b['MRP'],
                            "QtyInNo":b['QtyInNo'],
                            "QtyInKg":b['QtyInKg'],
                            "QtyInBox":b['QtyInBox'],
                            "BasicRate":b['BasicRate'],
                            "WithGSTRate":b['WithGSTRate'],
                            "NoRate":NoRate,
                            "UnitName":b['UnitName'],
                            "DiscountType":b['DiscountType'],
                            "Discount":b['Discount'],
                            "DiscountAmount":b['DiscountAmount'],
                            "TaxableValue":b['TaxableValue'],
                            "CGST":b['CGST'],
                            "CGSTPercentage":b['CGSTPercentage'],
                            "SGST":b['SGST'],
                            "SGSTPercentage":b['SGSTPercentage'],
                            "IGST":b['IGST'],
                            "IGSTPercentage":b['IGSTPercentage'],
                            "GSTPercentage":b['GSTPercentage'],
                            "GSTAmount":b['GSTAmount'],
                            "TotalValue":b['TotalValue'],
                            "TCSAmount":b['TCSAmount'],
                            "RoundOffAmount":b['RoundOffAmount'],
                            "GrandTotal":b['GrandTotal'],
                            "RouteName":b['RouteName'],
                            "StateName":b['StateName'],
                            "GSTIN":b['GSTIN'],
                            "Irn":b['Irn'],
                            "AckNo":b['AckNo'],
                            "EwayBillNo":b['EwayBillNo'],
                            "GroupName": b['GroupName'],
                            "SubGroupName" :b['SubGroupName'],

                        })
                    # InvoiceExportData.append({"InvoiceExportSerializerDetails" : InvoiceExportSerializer})
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 212, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceExportData})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'Report Not available', 212, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'InvoiceDateExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class DeletedInvoiceDateExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                query = T_DeletedInvoices.objects.raw('''SELECT TC_DeletedInvoiceItems.id,T_DeletedInvoices.Party AS SupplierID,A.Name SupplierName,T_DeletedInvoices.FullInvoiceNumber As InvoiceNumber,T_DeletedInvoices.InvoiceDate,T_DeletedInvoices.Customer As CustomerID,B.Name CustomerName,TC_DeletedInvoiceItems.Item AS FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_DeletedInvoiceItems.MRPValue AS MRP,TC_DeletedInvoiceItems.QtyInNo,TC_DeletedInvoiceItems.QtyInKg,TC_DeletedInvoiceItems.QtyInBox,TC_DeletedInvoiceItems.Rate AS BasicRate,(TC_DeletedInvoiceItems.Rate +((TC_DeletedInvoiceItems.Rate * TC_DeletedInvoiceItems.GSTPercentage)/100))WithGSTRate, M_Units.Name AS UnitName,TC_DeletedInvoiceItems.DiscountType, TC_DeletedInvoiceItems.Discount,TC_DeletedInvoiceItems.DiscountAmount,TC_DeletedInvoiceItems.BasicAmount As TaxableValue,TC_DeletedInvoiceItems.CGST,TC_DeletedInvoiceItems.CGSTPercentage,TC_DeletedInvoiceItems.SGST,TC_DeletedInvoiceItems.SGSTPercentage,TC_DeletedInvoiceItems.IGST,TC_DeletedInvoiceItems.IGSTPercentage,TC_DeletedInvoiceItems.GSTPercentage,TC_DeletedInvoiceItems.GSTAmount,TC_DeletedInvoiceItems.Amount AS TotalValue,T_DeletedInvoices.TCSAmount,T_DeletedInvoices.RoundOffAmount,T_DeletedInvoices.GrandTotal,M_Routes.Name AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_DeletedInvoiceUploads.Irn, TC_DeletedInvoiceUploads.AckNo,TC_DeletedInvoiceUploads.EwayBillNo,
 M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName
FROM TC_DeletedInvoiceItems
JOIN T_DeletedInvoices ON T_DeletedInvoices.Invoice =TC_DeletedInvoiceItems.Invoice
JOIN M_Parties A ON A.id= T_DeletedInvoices.Party
JOIN M_Parties B ON B.id = T_DeletedInvoices.Customer
JOIN M_States ON M_States.id = B.State_id
JOIN M_Items ON M_Items.id = TC_DeletedInvoiceItems.Item
JOIN C_Companies ON C_Companies.id = M_Items.Company_id
JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_DeletedInvoiceItems.GST
JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_DeletedInvoiceItems.Unit
JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_DeletedInvoices.Customer AND MC_PartySubParty.Party_id=%s
LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN TC_DeletedInvoiceUploads on TC_DeletedInvoiceUploads.Invoice= T_DeletedInvoices.id
left JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id and MC_ItemGroupDetails.GroupType_id=1
LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id

WHERE T_DeletedInvoices.InvoiceDate BETWEEN %s AND %s AND  T_DeletedInvoices.Party=%s ''', ([Party], [FromDate], [ToDate], [Party]))

                if query:
                    DeletedInvoiceExportData = list()
                    DeletedInvoiceExportSerializer = InvoiceDataExportSerializer(query, many=True).data
                    DeletedInvoiceExportData.append(
                        {"DeletedInvoiceExportSerializerDetails": DeletedInvoiceExportSerializer})
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+'To:'+str(ToDate), 213, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DeletedInvoiceExportData[0]})
                else:
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'Report Not available', 213, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'DeletedInvoiceDateExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class StockDamageReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        Damagedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Damagedata['FromDate']
                ToDate = Damagedata['ToDate']
                PartyID = Damagedata['PartyID']
                ConversionUnit = Damagedata['Unit']

                query1 = M_Units.objects.filter(
                    id=ConversionUnit).values('Name')
                query = O_BatchWiseLiveStock.objects.raw(
                    '''SELECT M_Items.id, M_Items.Name ItemName, SUM(BaseUnitQuantity) Qty,M_Units.id UnitID,O_LiveBatches.MRPValue FROM O_BatchWiseLiveStock JOIN M_Items ON M_Items.id=O_BatchWiseLiveStock.Item_id JOIN M_Units ON M_Units.id=M_Items.BaseUnitID_id JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id WHERE O_BatchWiseLiveStock.Party_id=%s AND O_BatchWiseLiveStock.IsDamagePieces=1 AND O_BatchWiseLiveStock.BaseUnitQuantity>0  GROUP BY O_BatchWiseLiveStock.Item_id,O_LiveBatches.MRPValue''', ([PartyID]))
                if query:
                    DamageStockData = list()
                    DamageItemStocktSerializer = DamageStocktSerializer(
                        query, many=True).data
                    for a in DamageItemStocktSerializer:
                        ConversionUnitQty = UnitwiseQuantityConversion(
                            a['id'], a['Qty'], 0, a['UnitID'], 0, ConversionUnit, 0).ConvertintoSelectedUnit()
                        DamageStockData.append({
                            "Item": a['id'],
                            "ItemName": a['ItemName'],
                            "ActualQty": ConversionUnitQty,
                            "Unit": query1[0]['Name'],
                            "MRP": a['MRPValue']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DamageStockData})
                else:
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ReturnReportDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Party_list = Party.split(",")
                query = T_PurchaseReturn.objects.raw('''SELECT T_PurchaseReturn.id, T_PurchaseReturn.ReturnDate,B.Name CustomerName,D.Name CustomerType,C_Companies.Name CompanyName, M_Group.Name Product,MC_SubGroup.Name SubProduct, M_Items.id AS ERPItemCode, M_Items.SAPItemCode, M_Items.Name MaterialName,TC_PurchaseReturnItems.Quantity ReturnQtyNos,TC_PurchaseReturnItems.MRPValue,TC_PurchaseReturnItems.Rate, TC_PurchaseReturnItems.BasicAmount,TC_PurchaseReturnItems.GSTPercentage, TC_PurchaseReturnItems.GSTAmount, TC_PurchaseReturnItems.Amount,TC_PurchaseReturnItems.Discount,TC_PurchaseReturnItems.DiscountAmount,TC_PurchaseReturnItems.DiscountType,TC_PurchaseReturnItems.BatchDate, TC_PurchaseReturnItems.BatchCode,M_GeneralMaster.Name ReasonForReturn,TC_PurchaseReturnItems.ApprovedQuantity ApprovedQuantityInNo,MC_PartyAddress.Address,MC_PartyAddress.PIN,M_Routes.Name RouteName,A.Name SupplierName,C.Name SupplierType,T_PurchaseReturn.FullReturnNumber,ApprovedByCompany,FinalApprovalDate,ApprovedRate,ApprovedBasicAmount,ApprovedGSTPercentage,ApprovedCGST,ApprovedIGST,ApprovedSGST,ApprovedCGSTPercentage,ApprovedSGSTPercentage,ApprovedIGSTPercentage,ApprovedGSTAmount,ApprovedAmount,ApprovedDiscountAmount FROM TC_PurchaseReturnItems JOIN T_PurchaseReturn ON T_PurchaseReturn.id =TC_PurchaseReturnItems.PurchaseReturn_id JOIN M_Parties A ON A.id= T_PurchaseReturn.Party_id JOIN M_Parties B ON B.id = T_PurchaseReturn.Customer_id JOIN M_PartyType C  ON C.id= A.PartyType_id JOIN M_PartyType D ON D.id= B.PartyType_id Left JOIN MC_PartyAddress ON MC_PartyAddress.Party_id=B.id AND MC_PartyAddress.IsDefault=1 JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id = B.id  Left JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id JOIN M_Items ON M_Items.id = TC_PurchaseReturnItems.Item_id LEFT JOIN MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1 LEFT JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id JOIN M_GeneralMaster ON M_GeneralMaster.id = TC_PurchaseReturnItems.ItemReason_id JOIN C_Companies ON C_Companies.id = M_Items.Company_id WHERE T_PurchaseReturn.ReturnDate BETWEEN %s AND %s AND  (T_PurchaseReturn.Party_id IN %s OR T_PurchaseReturn.Customer_id IN %s)  Order by T_PurchaseReturn.ReturnDate,T_PurchaseReturn.Customer_id  ''', ([
                                                      FromDate, ToDate, Party_list,Party_list]))
                # CustomPrint(query.query)
                if query:
                    ReturnSerializer = ReturnReportSerializer(
                        query, many=True).data
                    log_entry = create_transaction_logNew(request, Reportdata, 0, 'From:'+str(
                        FromDate)+','+'To:'+str(ToDate), 214, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReturnSerializer})
                else:
                    log_entry = create_transaction_logNew(
                        request, Reportdata, 0, 'Report Not available', 214, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'ReturnReportDownload:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class MaterialRegisterDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Item = Reportdata['Item']
                Unit = Reportdata['Unit']

                q1 = M_Items.objects.filter(id=Item).values('BaseUnitID_id')
                BaseUnitID = q1[0]['BaseUnitID_id']
                q2 = M_Settings.objects.filter(id=14).values('DefaultValue')
                DefaultValues = q2[0]['DefaultValue']

                query = T_PurchaseReturn.objects.raw('''SELECT 1 as id,a.* from (SELECT 1 Sequence, T_GRNs.GRNDate TransactionDate,T_GRNs.CreatedOn,T_GRNs.FullGRNNumber TransactionNumber,M_Parties.Name,QtyInBox,QtyInKg,QtyInNo FROM T_GRNs 
JOIN TC_GRNItems ON TC_GRNItems.GRN_id=T_GRNs.id
JOIN M_Parties ON M_Parties.id = T_GRNs.Party_id
WHERE GRNDate Between %s AND %s AND Customer_id=%s and TC_GRNItems.Item_id=%s

UNION ALL

SELECT 2 Sequence, T_PurchaseReturn.ReturnDate TransactionDate,T_PurchaseReturn.CreatedOn ,T_PurchaseReturn.FullReturnNumber TransactionNumber,M_Parties.Name,UnitwiseQuantityConversion(%s,Quantity,0,1,0,4,0)QtyInBox,UnitwiseQuantityConversion(%s,Quantity,0,1,0,2,0)QtyInKg,UnitwiseQuantityConversion(%s,Quantity,0,1,0,1,0)QtyInNo   FROM T_PurchaseReturn 
JOIN TC_PurchaseReturnItems ON TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
JOIN M_Parties ON M_Parties.id = T_PurchaseReturn.Customer_id
WHERE ReturnDate Between %s AND  %s AND Party_id=%s AND TC_PurchaseReturnItems.Item_id=%s AND TC_PurchaseReturnItems.ItemReason_id IN (%s)

UNION ALL

SELECT 3 Sequence, StockDate TransactionDate,CreatedOn, FullReturnNumber TransactionNumber, Name, UnitwiseQuantityConversion(%s,QStock,0,%s,0,4,0)QtyInBox,UnitwiseQuantityConversion(%s,QStock,0,%s,0,2,0)QtyInKg,UnitwiseQuantityConversion(%s,QStock,0,%s,0,1,0)QtyInNo 
FROM (SELECT 3 Sequence,T_Stock.StockDate,T_Stock.CreatedOn ,'STOCK' FullReturnNumber,M_Parties.Name, '' QtyInBox,'' QtyInKg,''QtyInNo, SUM(T_Stock.BaseUnitQuantity) QStock 
From T_Stock
 JOIN M_Parties ON M_Parties.id=T_Stock.Party_id  
 WHERE StockDate Between %s AND %s AND Party_id=%s  AND  T_Stock.Item_id=%s and IsStockAdjustment=0 GROUP BY 3 ,T_Stock.StockDate, FullReturnNumber,M_Parties.Name, QtyInBox, QtyInKg,QtyInNo)AA

UNION ALL

SELECT 6 Sequence, StockDate TransactionDate,CreatedOn, FullReturnNumber TransactionNumber, Name, UnitwiseQuantityConversion(%s,QStock,0,%s,0,4,0)QtyInBox,UnitwiseQuantityConversion(%s,QStock,0,%s,0,2,0)QtyInKg,UnitwiseQuantityConversion(%s,QStock,0,%s,0,1,0)QtyInNo 
FROM (SELECT 3 Sequence,T_Stock.StockDate,T_Stock.CreatedOn ,'Stock Adjustment' FullReturnNumber,M_Parties.Name, '' QtyInBox,'' QtyInKg,''QtyInNo, SUM(T_Stock.Difference) QStock 
From T_Stock
 JOIN M_Parties ON M_Parties.id=T_Stock.Party_id  
 WHERE StockDate Between %s AND %s AND Party_id=%s  AND  T_Stock.Item_id=%s and IsStockAdjustment =1 GROUP BY 3 ,T_Stock.StockDate, FullReturnNumber,M_Parties.Name, QtyInBox, QtyInKg,QtyInNo)AA

UNION ALL

SELECT 4 Sequence, T_Invoices.InvoiceDate TransactionDate,T_Invoices.CreatedOn,T_Invoices.FullInvoiceNumber TransactionNumber,M_Parties.Name,QtyInBox,QtyInKg,QtyInNo FROM T_Invoices 
JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
WHERE InvoiceDate Between %s AND %s AND Party_id=%s AND  TC_InvoiceItems.Item_id=%s

UNION ALL

SELECT 5 Sequence, T_PurchaseReturn.ReturnDate TransactionDate,T_PurchaseReturn.CreatedOn,T_PurchaseReturn.FullReturnNumber TransactionNumber,M_Parties.Name,UnitwiseQuantityConversion(%s,Quantity,0,1,0,4,0)QtyInBox,UnitwiseQuantityConversion(%s,Quantity,0,1,0,2,0)QtyInKg,UnitwiseQuantityConversion(%s,Quantity,0,1,0,1,0)QtyInNo  FROM T_PurchaseReturn 
JOIN TC_PurchaseReturnItems ON TC_PurchaseReturnItems.PurchaseReturn_id=T_PurchaseReturn.id
JOIN M_Parties ON M_Parties.id = T_PurchaseReturn.Party_id
WHERE ReturnDate Between %s AND %s AND Customer_id=%s AND TC_PurchaseReturnItems.Item_id=%s and ((TC_PurchaseReturnItems.ItemReason_id IN (SELECT DefaultValue FROM M_Settings WHERE id = 14) and T_PurchaseReturn.Mode =3) OR(T_PurchaseReturn.Mode =2)))a order by TransactionDate, CreatedOn ''', ([FromDate, ToDate, Party, Item, Item, Item, Item, FromDate, ToDate, Party, Item, DefaultValues, Item, BaseUnitID, Item, BaseUnitID, Item, BaseUnitID, FromDate, ToDate, Party, Item, Item, BaseUnitID, Item, BaseUnitID, Item, BaseUnitID, FromDate, ToDate, Party, Item, FromDate, ToDate, Party, Item, Item, Item, Item, FromDate, ToDate, Party, Item]))
                # CustomPrint(query)
                if query:
                    MaterialRegisterList = MaterialRegisterSerializerView(
                        query, many=True).data
                    query2 = O_DateWiseLiveStock.objects.filter(
                        StockDate=FromDate, Party=Party, Item=Item).values('OpeningBalance', 'Unit_id')

                    if query2:

                        # if int(query2[0]['OpeningBalance']) > 0:
                        OpeningBalance = UnitwiseQuantityConversion(
                            Item, query2[0]['OpeningBalance'], 0, query2[0]['Unit_id'], 0, Unit, 0).ConvertintoSelectedUnit()
                    else:

                        OpeningBalance = 0.00

                    query3 = O_DateWiseLiveStock.objects.filter(
                        StockDate=ToDate, Party=Party, Item=Item).values('ClosingBalance', 'Unit_id')

                    if query3:

                        ClosingBalance = UnitwiseQuantityConversion(
                            Item, query3[0]['ClosingBalance'], 0, query3[0]['Unit_id'], 0, Unit, 0).ConvertintoSelectedUnit()

                    else:
                        ClosingBalance = 0.00
                        # log_entry = create_transaction_logNew(request,Reportdata,Party,'Stock Processing Needed',215,0,FromDate,ToDate,0)
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':'Stock Processing Needed', 'Data': []})
                    MaterialRegisterList.append(
                        {"OpeningBalance": OpeningBalance, "ClosingBalance": ClosingBalance})
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+','+'To:'+str(ToDate), 215, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MaterialRegisterList})
                else:
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'Records Not available', 215, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'MaterialRegister:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class CreditDebitExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']
                Customer = Reportdata['Customer']
                NoteTypeIDs = Reportdata['NoteTypeIDs']
                NoteType_list = NoteTypeIDs.split(",")

                if(Party) > 0:
                    query = TC_CreditDebitNoteItems.objects.raw('''SELECT TC_CreditDebitNoteItems.id,T_CreditDebitNotes.Party_id AS SupplierID,A.Name SupplierName,T_CreditDebitNotes.FullNoteNumber AS InvoiceNumber,T_CreditDebitNotes.CRDRNoteDate AS InvoiceDate,T_CreditDebitNotes.Narration,C.Name As NoteTypeName , D.Name As NoteReasonName,T_CreditDebitNotes.Customer_id As CustomerID,B.Name CustomerName,TC_CreditDebitNoteItems.Item_id As FE2MaterialID,M_Items.Name As MaterialName,C_Companies.Name CompanyName,M_GSTHSNCode.HSNCode,TC_CreditDebitNoteItems.MRPValue , TC_CreditDebitNoteItems.QtyInNo, TC_CreditDebitNoteItems.QtyInKg,TC_CreditDebitNoteItems.QtyInBox, "" AS RatePerPiece,TC_CreditDebitNoteItems.Rate AS BasicRate, (TC_CreditDebitNoteItems.Rate +((TC_CreditDebitNoteItems.Rate * TC_CreditDebitNoteItems.GSTPercentage)/100))WithGSTRate,M_Units.Name AS UnitName,TC_CreditDebitNoteItems.DiscountType, TC_CreditDebitNoteItems.Discount, TC_CreditDebitNoteItems.DiscountAmount,TC_CreditDebitNoteItems.BasicAmount AS TaxableValue, TC_CreditDebitNoteItems.CGSTPercentage, TC_CreditDebitNoteItems.CGST,TC_CreditDebitNoteItems.SGSTPercentage, TC_CreditDebitNoteItems.SGST,TC_CreditDebitNoteItems.IGSTPercentage,TC_CreditDebitNoteItems.IGST,TC_CreditDebitNoteItems.GSTPercentage, TC_CreditDebitNoteItems.Amount AS TotalValue, T_CreditDebitNotes.RoundOffAmount,T_CreditDebitNotes.GrandTotal,M_Routes.Name AS RouteName,M_States.Name AS StateName,B.GSTIN,TC_CreditDebitNoteUploads.Irn, TC_CreditDebitNoteUploads.AckNo,TC_CreditDebitNoteUploads.EwayBillNo
FROM TC_CreditDebitNoteItems
JOIN T_CreditDebitNotes ON T_CreditDebitNotes.id=TC_CreditDebitNoteItems.CRDRNote_id
JOIN M_Parties A ON A.id= T_CreditDebitNotes.Party_id
JOIN M_Parties B ON B.id = T_CreditDebitNotes.Customer_id
JOIN M_States ON M_States.id = B.State_id
JOIN M_Items ON M_Items.id = TC_CreditDebitNoteItems.Item_id
JOIN C_Companies ON C_Companies.id = M_Items.Company_id
JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_CreditDebitNoteItems.Unit_id
JOIN M_Units ON M_Units.id = MC_ItemUnits.UnitID_id
JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_CreditDebitNoteItems.GST_id
JOIN MC_PartySubParty ON MC_PartySubParty.SubParty_id=T_CreditDebitNotes.Customer_id AND MC_PartySubParty.Party_id=%s
LEFT JOIN M_Routes ON M_Routes.id=MC_PartySubParty.Route_id
LEFT JOIN TC_CreditDebitNoteUploads ON TC_CreditDebitNoteUploads.CRDRNote_id=T_CreditDebitNotes.id
JOIN M_GeneralMaster C ON C.id = T_CreditDebitNotes.NoteType_id
LEFT JOIN M_GeneralMaster D ON D.id = T_CreditDebitNotes.NoteReason_id

WHERE T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND T_CreditDebitNotes.Party_id=%s AND T_CreditDebitNotes.IsDeleted=0 AND NoteType_id IN %s ''', ([Party], [FromDate], [ToDate], [Party], NoteType_list))
                # CustomPrint(query.query)
                if query:
                    InvoiceExportData = list()
                    InvoiceExportSerializer = CreditDebitDataExportSerializer(
                        query, many=True).data
                    for b in InvoiceExportSerializer:

                        qur2 = M_Parties.objects.filter(
                            id=b['CustomerID']).values('PriceList').distinct()
                        query = M_PriceList.objects.values(
                            'id').filter(id__in=qur2)
                        Rate = RateCalculationFunction(
                            0, b['FE2MaterialID'], 0, 0, 1, 0, query[0]['id']).RateWithGST()
                        NoRate = float(Rate[0]['NoRatewithOutGST'])
                        InvoiceExportData.append({

                            "SupplierID": b['SupplierID'],
                            "SupplierName": b['SupplierName'],
                            "InvoiceNumber": b['InvoiceNumber'],
                            "InvoiceDate": b['InvoiceDate'],
                            "Narration": b['Narration'],
                            "NoteType": b['NoteTypeName'],
                            "NoteReason": b['NoteReasonName'],
                            "CustomerID": b['CustomerID'],
                            "CustomerName": b['CustomerName'],
                            "FE2MaterialID": b['FE2MaterialID'],
                            "MaterialName": b['MaterialName'],
                            "CompanyName": b['CompanyName'],
                            "HSNCode": b['HSNCode'],
                            "MRP": b['MRPValue'],
                            "QtyInNo": b['QtyInNo'],
                            "QtyInKg": b['QtyInKg'],
                            "QtyInBox": b['QtyInBox'],
                            "BasicRate": b['BasicRate'],
                            "WithGSTRate": b['WithGSTRate'],
                            "NoRate": NoRate,
                            "UnitName": b['UnitName'],
                            "DiscountType": b['DiscountType'],
                            "Discount": b['Discount'],
                            "DiscountAmount": b['DiscountAmount'],
                            "TaxableValue": b['TaxableValue'],
                            "CGST": b['CGST'],
                            "CGSTPercentage": b['CGSTPercentage'],
                            "SGST": b['SGST'],
                            "SGSTPercentage": b['SGSTPercentage'],
                            "IGST": b['IGST'],
                            "IGSTPercentage": b['IGSTPercentage'],
                            "GSTPercentage": b['GSTPercentage'],
                            "GSTAmount": b['GSTAmount'],
                            "TotalValue": b['TotalValue'],
                            # "TCSAmount":b['TCSAmount'],
                            "RoundOffAmount": b['RoundOffAmount'],
                            "GrandTotal": b['GrandTotal'],
                            "RouteName": b['RouteName'],
                            "StateName": b['StateName'],
                            "GSTIN": b['GSTIN'],
                            "Irn": b['Irn'],
                            "AckNo": b['AckNo'],
                            "EwayBillNo": b['EwayBillNo'],
                        })
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'From:'+str(FromDate)+'To:'+str(ToDate), 216, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceExportData})
                else:
                    log_entry = create_transaction_logNew(
                        request, Reportdata, 0, 'Report Not available', 216, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'CreditDebitExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ReceiptDataExportReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        Reportdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Reportdata['FromDate']
                ToDate = Reportdata['ToDate']
                Party = Reportdata['Party']

                if(Party) > 0:
                    query = T_Receipts.objects.raw(
                        '''SELECT T_Receipts.id, T_Receipts.Party_id AS SupplierID, A.Name SupplierName, T_Receipts.FullReceiptNumber AS ReceiptNumber, T_Receipts.ReceiptDate, T_Receipts.Customer_id AS CustomerID,B.Name CustomerName,C.Name As ReceiptTypeName,D.Name As ReceiptModeName,E.Name As BankName,F.Name As DepositorBankName,AmountPaid,T_Receipts.Description,ChequeDate,DocumentNo FROM T_Receipts JOIN  M_GeneralMaster C ON C.id=T_Receipts.ReceiptType_id JOIN  M_GeneralMaster D ON D.id=T_Receipts.ReceiptMode_id LEFT JOIN M_Bank E ON E.id=T_Receipts.Bank_id LEFT JOIN M_Bank F ON F.id=T_Receipts.DepositorBank_id JOIN M_Parties A on A.id= T_Receipts.Party_id JOIN M_Parties B on B.id = T_Receipts.Customer_id WHERE T_Receipts.ReceiptDate BETWEEN %s AND %s AND T_Receipts.Party_id=%s Order By id desc''', ([FromDate], [ToDate], [Party]))
                # CustomPrint(query.query)
                if query:
                    ReceiptExportData = list()
                    ReceiptExportSerializer = ReceiptDataExportSerializer(
                        query, many=True).data
                    for b in ReceiptExportSerializer:
                        ReceiptExportData.append({
                            "id": b['id'],
                            "SupplierID": b['SupplierID'],
                            "SupplierName": b['SupplierName'],
                            "ReceiptNumber": b['ReceiptNumber'],
                            "ReceiptDate": b['ReceiptDate'],
                            "CustomerID": b['CustomerID'],
                            "CustomerName": b['CustomerName'],
                            "ReceiptType": b['ReceiptTypeName'],
                            "ReceiptMode": b['ReceiptModeName'],
                            "BankName": b['BankName'],
                            "DepositorBankName": b['DepositorBankName'],
                            "AmountPaid": b['AmountPaid'],
                            "Description": b['Description'],
                            "ChequeDate": b['ChequeDate'],
                            "DocumentNo": b['DocumentNo']
                        })
                    log_entry = create_transaction_logNew(request, Reportdata, Party, 'From:'+str(
                        FromDate)+','+'To:'+str(ToDate), 217, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReceiptExportData})
                else:
                    log_entry = create_transaction_logNew(
                        request, Reportdata, Party, 'Report Not available', 217, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Reportdata, 0, 'ReceiptDataExportReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


class OutStandingBalanceView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        Balance_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = Balance_Data['PartyID']
                Route = Balance_Data['RouteID']
                ToDate = Balance_Data['Date']

                if Route == '':
                    query = MC_PartySubParty.objects.raw('''SELECT M_Parties.id, M_Parties.Name AS PartyName, M_Routes.Name AS RouteName
FROM MC_PartySubParty
JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id
LEFT JOIN M_Routes ON M_Routes.id = MC_PartySubParty.Route_id WHERE MC_PartySubParty.Party_id = %s''', ([Party]))

                else:
                    query = MC_PartySubParty.objects.raw('''SELECT M_Parties.id, M_Parties.Name AS PartyName, M_Routes.Name AS RouteName
FROM MC_PartySubParty
JOIN M_Parties ON M_Parties.id = MC_PartySubParty.SubParty_id
LEFT JOIN M_Routes ON M_Routes.id = MC_PartySubParty.Route_id WHERE MC_PartySubParty.Party_id = %s AND MC_PartySubParty.Route_id = %s''', ([Party], [Route]))
                if query:
                    Balance_Serializer = BalanceSerializer(
                        query, many=True).data
                    BalanceList = list()

                    for a in Balance_Serializer:
                        BalanceList.append({
                            "PartyID": a['id'],
                            "PartyName": a['PartyName'],
                            "RouteName": a['RouteName'],
                            "OutStandingBalance": round(float(GetOpeningBalance(Party, a['id'], ToDate)), 2)
                        })
                    log_entry = create_transaction_logNew(
                        request, Balance_Data, Party, 'To:'+str(ToDate), 218, 0, 0, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BalanceList})
                log_entry = create_transaction_logNew(
                    request, Balance_Data, Party, 'Report Not Found', 218, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Balance_Data, 0, 'OutStandingBalanceReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ManPowerReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = MC_PartySubParty.objects.raw('''SELECT  MC_PartySubParty.id,A.SAPPartyCode AS SAPCode, A.id AS FEParty_id, A.NAME AS PartyName,  A.isActive AS PartyActive, A.CreatedOn AS PartyCreation,
M_PartyType.Name AS PartyType, A.Email, A.PAN, MC_PartySubParty.Party_id AS SS_id, B.NAME AS SSName, M_Users.LoginName AS LoginID, "India" AS country,
 C.Address, M_States.Name AS State, M_Districts.Name AS District,
M_Cities.Name AS City, C.PIN AS PIN, A.MobileNo AS Mobile, M_Employees.Name AS OwnerName,
A.Latitude, A.Longitude, C.FSSAINo AS FSSAINo,
C.FSSAIExipry AS FSSAIExpiry, A.GSTIN AS GSTIN, M_Employees_GM.Name AS GM, M_Employees_NH.Name AS NSM,
 M_Employees_RH.Name AS RSM, M_Employees_ASM.Name AS ASM,M_Employees_SE.Name AS SE,M_Employees_SO.Name AS SO, M_Employees_SR.Name AS SR, M_Employees_MT.Name AS MT,  M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster
FROM MC_PartySubParty 
LEFT JOIN M_Parties A ON A.id = MC_PartySubParty.SubParty_id
LEFT JOIN M_Parties B ON B.id = MC_PartySubParty.Party_id
LEFT JOIN M_PartyType ON M_PartyType.id = A.PartyType_id
LEFT JOIN MC_PartyAddress  C ON C.Party_id = A.id
LEFT JOIN M_States ON M_States.id = A.State_id
LEFT JOIN M_Districts ON M_Districts.id = A.District_id
LEFT JOIN M_Cities ON M_Cities.id = A.City_id
LEFT JOIN MC_EmployeeParties ON MC_EmployeeParties.Party_id = A.id
LEFT JOIN M_Employees On M_Employees.id = MC_EmployeeParties.Employee_id
LEFT JOIN M_Users On M_Users.Employee_id = M_Employees.id
LEFT JOIN M_PartyDetails X On  A.id=X.Party_id AND X.Group_id is null
LEFT JOIN M_Cluster On X.Cluster_id=M_Cluster.id
LEFT JOIN M_SubCluster On X.SubCluster_id=M_SubCluster.id
LEFT JOIN M_Employees M_Employees_GM ON M_Employees_GM.id = X.GM
LEFT JOIN M_Employees  M_Employees_NH ON M_Employees_NH.id = X.NH
LEFT JOIN M_Employees  M_Employees_RH ON M_Employees_RH.id = X.RH
LEFT JOIN M_Employees M_Employees_ASM ON M_Employees_ASM.id = X.ASM
LEFT JOIN M_Employees M_Employees_SE ON M_Employees_SE.id = X.SE
LEFT JOIN M_Employees M_Employees_SO ON M_Employees_SO.id = X.SO
LEFT JOIN M_Employees M_Employees_SR ON M_Employees_SR.id = X.SR
LEFT JOIN M_Employees M_Employees_MT ON M_Employees_MT.id = X.MT
                                                     
WHERE M_PartyType.id IN(9,10,15,17,19) AND C.IsDefault = 1 ''')
               

                if query:
                    ManPower_Serializer = ManPowerSerializer(query, many=True).data
                    ManPowerList = list()
                    CustomPrint(query)
                    for a in ManPower_Serializer:
                        PartyDateTime = datetime.strptime(a['PartyCreation'], "%Y-%m-%dT%H:%M:%S.%f")
                        PartyCreation = PartyDateTime.strftime("%Y-%m-%d %H:%M:%S")
                        ManPowerList.append({
                            "SAPCode": a['SAPCode'],
                            "FEParty_id": a['FEParty_id'],
                            "PartyName": a['PartyName'],
                            "PartyActive": a['PartyActive'],
                            "PartyCreation":PartyCreation,
                            "PartyType": a['PartyType'],
                            "Email": a['Email'],
                            "PAN":a['PAN'],
                            "SS_id": a['SS_id'],
                            "SSName": a['SSName'],
                            "LoginID": a['LoginID'],
                            "country": a['country'],
                            "Cluster" : a["Cluster"],
                            "SubCluster": a["SubCluster"],
                            "Address": a['Address'],
                            "State": a['State'],
                            "District": a['District'],
                            "City": a['City'],
                            "PIN": a['PIN'],
                            "Mobile": a['Mobile'],
                            "OwnerName": a['OwnerName'],
                            "Latitude": a['Latitude'],
                            "Longitude": a['Longitude'],
                            "FSSAINo": a['FSSAINo'],
                            "FSSAIExpiry": a['FSSAIExpiry'],
                            "GSTIN": a['GSTIN'],
                            "GM": a['GM'],
                            "NSM": a['NSM'],
                            "RSM": a['RSM'],
                            "ASM": a['ASM'],
                            "SE": a['SE'],
                            "SO": a['SO'],
                            "SR": a['SR'],
                            "MT": a['MT']
                            
                            })
                    log_entry = create_transaction_logNew(
                        request, ManPower_Serializer, 0, '', 219, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ManPowerList})
                log_entry = create_transaction_logNew(
                    request, ManPower_Serializer, 0, 'Report Not Found', 219, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'ManPowerReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class ProductAndMarginReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                today = date.today()
                IsSCM = data['IsSCM']
                PartyID = data['Party']
                PartyTypeID = data['PartyType']
                PriceListID = data['PriceList']
                CompanyID = data['Company']
                GroupID = data['Group'].split(",")
                SubGroupID = data['SubGroup'].split(",")
                ItemID = data['Item'].split(",")
                

                try:
                    PriceListID = int(PriceListID)
                except (ValueError, TypeError):
                    PriceListID = 0

                query =f""" SELECT M_Items.id ,SAPItemCode,BarCode,GSTHsnCodeMaster(M_Items.id,%s,3)HSNCode,C_Companies.Name CompanyName,isActive,
(case when Length ='' then '' else concat(Length,'L X ',Breadth,'B X ',Height,'W - MM') end)BoxSize,StoringCondition
,ifnull(M_Group.Name,'') Product,ifnull(MC_SubGroup.Name,'') SubProduct,M_Items.Name ItemName,ShortName,
round(GetTodaysDateMRP(M_Items.id,%s,2,0,0),0) MRP,round(GSTHsnCodeMaster(M_Items.id,%s,2),2)GST,M_Units.Name BaseUnit,Grammage SKUVol,
MC_ItemShelfLife.Days ShelfLife,PIB.BaseUnitQuantity PcsInBox , PIK.BaseUnitQuantity PcsInKg, PIN.BaseUnitQuantity PcsInNo, ifnull(M_Group.id,'') ProductID,ifnull(MC_SubGroup.id,'') SubProductID
 ,M_Items.BaseUnitID_id
 FROM M_Items
 join C_Companies on C_Companies.id=M_Items.Company_id 
 left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id = 1
 left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id 
 left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
 left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
 join M_Units on M_Units.id=M_Items.BaseUnitID_id
 left join MC_ItemShelfLife on MC_ItemShelfLife.Item_id=M_Items.id and IsDeleted=0
 JOIN MC_ItemUnits PIB on PIB.Item_id=M_Items.id and PIB.UnitID_id=4 and PIB.IsDeleted=0
 JOIN MC_ItemUnits PIK on PIK.Item_id=M_Items.id and PIK.UnitID_id=2 and PIK.IsDeleted=0
 JOIN MC_ItemUnits PIN on PIN.Item_id=M_Items.id and PIN.UnitID_id=1 and PIN.IsDeleted=0
 """
                
                q=C_Companies.objects.filter(id=CompanyID).values('IsSCM')
                if q[0]['IsSCM'] == 1:
                    CompanyIDs=MC_EmployeeParties.objects.raw(f'''select GetAllCompanyIDsFromLoginCompany({CompanyID}) id''')
                    for row in CompanyIDs:
                        p=row.id
                    Party_ID = p.split(",")
                    dd=Party_ID[:-1]
                    C=', '.join(dd)
                    Companycondition = f"where M_Items.Company_id in( {C}) and M_Items.IsSCM=1"
                else:
                    Companycondition = f"where M_Items.Company_id = {CompanyID}"
                
                if IsSCM == '0':
                    query += f"{Companycondition} "
                    # query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence  "
                    ItemQuery = M_Items.objects.raw(query, [today, today, today])
                else:
                    query += f"join MC_PartyItems on MC_PartyItems.Item_id=M_Items.id and MC_PartyItems.Party_id=%s {Companycondition}"
                    # query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence  "
                    ItemQuery = M_Items.objects.raw(query, [today, today, today, PartyID])
                
                if any(ItemID) :    
                    query += " "
                    query += "  AND M_Items.id in %s "
                    query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence  "
                    
                    if IsSCM == '0':
                       
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,ItemID])
                        
                    else:
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,PartyID,ItemID])
                     
                elif any(SubGroupID):
                    query += " "
                    query += "  AND M_Group.id in %s and MC_SubGroup.id in %s"
                    query += " order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence"
                    if IsSCM == '0':
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,GroupID,SubGroupID])
                    else:
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,PartyID,GroupID,SubGroupID])
                elif any(GroupID):
                    query += " "
                    query += "  AND M_Group.id in %s "
                    query += "order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence"
                    if IsSCM == '0':
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,GroupID])
                    else:
                        ItemQuery = M_Items.objects.raw(query, [today, today, today,PartyID,GroupID])
                
               
                
                ItemsList = list()
                if ItemQuery:

                    for row in ItemQuery:
                        
                        if IsSCM == '0':
                            
                            if PriceListID == 0:
                                pricelistquery=M_PriceList.objects.raw('''SELECT id,Name,ShortName FROM M_PriceList order by Sequence''')
                                
                            else:
                               
                                pricelistquery=M_PriceList.objects.raw('''SELECT id,Name,ShortName,CalculationPath FROM M_PriceList where id = %s order by Sequence''',[PriceListID])
                                for i in pricelistquery:
                                    pp=(i.CalculationPath).split(',')
                                    pricelistquery=M_PriceList.objects.raw('''SELECT id,Name,ShortName FROM M_PriceList where id in %s order by Sequence''',[pp])
                             
                        else:
                            if PriceListID == 0:
                               
                                pricelistquery=M_PriceList.objects.raw('''select distinct PriceList_id id,M_PriceList.Name,M_PriceList.CalculationPath,ShortName from M_Parties 
join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id 
join M_PriceList on M_PriceList.id=M_Parties.PriceList_id
where  M_Parties.id=%s or MC_PartySubParty.Party_id=%s ''',(PartyID,PartyID))
                            else:
                                
                                pricelistquery=M_PriceList.objects.raw('''select distinct PriceList_id id,M_PriceList.Name,M_PriceList.CalculationPath,ShortName from M_Parties 
join MC_PartySubParty on MC_PartySubParty.SubParty_id=M_Parties.id 
join M_PriceList on M_PriceList.id=M_Parties.PriceList_id
where  M_Parties.id=%s or MC_PartySubParty.Party_id=%s and M_PriceList.id=%s ''',(PartyID,PartyID,PriceListID))
                                for i in pricelistquery:
                                    
                                    pp=(i.CalculationPath).split(',')
                                    pricelistquery=M_PriceList.objects.raw('''SELECT id,Name,ShortName FROM M_PriceList where id in %s order by Sequence''',[pp])
                         

                        ItemMargins = list()
                        RateList = list()
                        ItemImage = list()

                        for x in pricelistquery:
                            query2 = M_MarginMaster.objects.raw('''select 1 as id, GetTodaysDateMargin(%s,%s,%s,0,0)Margin,RateCalculationFunction1(0, %s, 0, 1, 0, %s, 0, 0)RatewithoutGST,RateCalculationFunction1(0, %s, 0, 1, 0, %s, 0, 1)RatewithGST,RateCalculationFunction1(0, %s, 0, %s, 0, %s, 0, 0)BaseUnitRatewithoutGST''', (
                                row.id, today, x.id, row.id, x.id, row.id, x.id,row.id, row.BaseUnitID_id,x.id))

                           
                            
                            for a in query2:
                                # string1 = x['Name']
                                # string2 = x['ShortName'].replace(" ","")
                                string2 = (x.Name).replace(" ", "")
                                ItemMargins.append({
                                    string2+'Margin': str(float(a.Margin)) + '%'
                                })
                                RateList.append({

                                    string2+'RateWithGST': float(a.RatewithGST),
                                    string2+'RateWithOutGST': float(a.RatewithoutGST),
                                    string2+'BaseUnitRateWithOutGST': float(a.BaseUnitRatewithoutGST),
                                    "PriceListID" : x.id

                                })

                        ww = ItemMargins+RateList
                        query3 = MC_ItemImages.objects.raw(
                            '''select %s as id,M_ImageTypes.name ImageTypeName,M_ImageTypes.id ImageTypeid,ifnull(MC_ItemImages.Item_pic,' ')Item_pic from MC_ItemImages right join M_ImageTypes on M_ImageTypes.id=MC_ItemImages.ImageType_id and MC_ItemImages.Item_id=%s''', (row.id, row.id))
                        for b in query3:
                            ItemImage.append({
                                b.ImageTypeName: str(b.Item_pic)

                            })
                        ItemsList.append({

                            "FE2ItemID": row.id,
                            "SAPCode": row.SAPItemCode,
                            "Barcode": row.BarCode,
                            "HSNCode": row.HSNCode,
                            "Company": row.CompanyName,
                            "SKUStatus(T,F)": row.isActive,
                            "BoxSize": row.BoxSize,
                            "StoringCondition": row.StoringCondition,
                            "Product": row.Product,
                            "SubProduct": row.SubProduct,
                            "SKUName": row.ItemName,
                            "SKUShortName": row.ShortName,
                            "MRP": row.MRP,
                            "GST%": str(row.GST) +'%',
                            "BaseUnit": row.BaseUnit,
                            "SKUVol": row.SKUVol,
                            "ShelfLife": row.ShelfLife,
                            "PcsInBox": row.PcsInBox,
                            "PcsInKG": row.PcsInKg,
                            "PcsInNo": row.PcsInNo,
                            "ProductID" : row.ProductID,
                            "SubProductID" :row.SubProductID,
                            "ItemMargins": ww,
                            "ItemImage": ItemImage

                        })
                    log_entry = create_transaction_logNew(request, ItemsList, 0, '', 106, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ItemsList})
                log_entry = create_transaction_logNew(request, ItemsList, 0, "Report Not Available", 106, 0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Item Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, data, 0, 'ProductAndMarginReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


#             SELECT M_Items.id FE2ItemID,SAPItemCode,BarCode,GSTHsnCodeMaster(M_Items.id,'2023-12-05',3)HSNCode,C_Companies.Name Company,isActive,
# (case when Length ='' then '' else concat(Length,'L X ',Breadth,'B X ',Height,'W - MM') end)BoxSize,StoringCondition
# ,ifnull(M_Group.Name,'') Product,ifnull(MC_SubGroup.Name,'') SubProduct,M_Items.Name ItemName,ShortName,
# round(GetTodaysDateMRP(M_Items.id,'2023-12-05',2,0,0),0) MRP,concat(round(GSTHsnCodeMaster(M_Items.id,'2023-12-05',2),2),'%')GST,M_Units.Name BaseUnit,Grammage SKUVol,
# MC_ItemShelfLife.Days ShelfLife,PIB.BaseUnitQuantity PcsInBox , PIK.BaseUnitQuantity PcsInKg
#  FROM M_Items
#  join C_Companies on C_Companies.id=M_Items.Company_id
#  left join MC_ItemGroupDetails on MC_ItemGroupDetails.Item_id=M_Items.id
#  left JOIN M_GroupType ON M_GroupType.id = MC_ItemGroupDetails.GroupType_id
#  left JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id
#  left JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id
#  join M_Units on M_Units.id=M_Items.BaseUnitID_id
#  left join MC_ItemShelfLife on MC_ItemShelfLife.Item_id=M_Items.id
#  join MC_ItemUnits PIB on PIB.Item_id=M_Items.id and PIB.UnitID_id=4 and PIB.IsDeleted=0
#  join MC_ItemUnits PIK on PIK.Item_id=M_Items.id and PIK.UnitID_id=2 and PIK.IsDeleted=0

#  where MC_ItemGroupDetails.GroupType_id=1 order by M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence
#  limit 50;


class TCSAmountReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        TCSAmountData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = TCSAmountData['FromDate']
                ToDate = TCSAmountData['ToDate']
                Party = TCSAmountData['Party']

                if Party == "":
                    query = T_Invoices.objects.raw('''Select T_Invoices.id, T_Invoices.InvoiceDate, T_Invoices.InvoiceNumber, T_Invoices.TCSAmount AS TCSTaxAmount, T_Invoices.GrandTotal AS Total , M_Parties.id AS PartyID, M_Parties.Name AS PartyName From T_Invoices
Join M_Parties on T_Invoices.Party_id = M_Parties.id
WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.TCSAmount > 0''',(FromDate,ToDate))
                    log_entry = create_transaction_logNew(request, TCSAmountData, 0, '',266, 0)

                else:                                   
                    query = T_Invoices.objects.raw('''Select T_Invoices.id, T_Invoices.InvoiceDate, T_Invoices.InvoiceNumber, T_Invoices.TCSAmount AS TCSTaxAmount, T_Invoices.GrandTotal AS Total , M_Parties.id AS PartyID, M_Parties.Name AS PartyName
From T_Invoices
Join M_Parties on T_Invoices.Party_id = M_Parties.id
WHERE T_Invoices.InvoiceDate BETWEEN %s AND %s AND T_Invoices.TCSAmount > 0 AND T_Invoices.Party_id =%s''',(FromDate,ToDate,Party))
                    log_entry = create_transaction_logNew(request, TCSAmountData, Party, '',266, 0)
                    
                TSCAMountList = list()
                TCSAmountSerializer = TCSAmountReportSerializer(query,many=True).data         

                for a in TCSAmountSerializer:
                    GrandTotal = float(a['Total']) - float(a['TCSTaxAmount'])
                    TSCAMountList.append({
                        "InvoiceDate": a['InvoiceDate'],
                        "InvoiceNumber": a['InvoiceNumber'],
                        "GrandTotal": GrandTotal,
                        "TCSTaxAmount": a['TCSTaxAmount'],
                        "Total": a['Total'],
                        "PartyID":a['PartyID'],
                        "PartyName":a['PartyName']
                    })
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TSCAMountList})
        except Exception as e:
            log_entry = create_transaction_logNew(request, TCSAmountData, 0,'TCSAmountReport:'+str(e),33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

class CxDDDiffReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data['Party']
                InvoiceData=list()
                
                query='''select M_Parties.id,M_Parties.Name CXName,M_Items.Name ItemName,TC_InvoiceItems.MRPValue,sum(TC_InvoiceItems.Quantity)Quantity,M_Units.Name UnitName,TC_InvoiceItems.Rate,
RateCalculationFunction1(0, TC_InvoiceItems.Item_id, 0, M_Units.id, 0, 2, TC_InvoiceItems.MRPValue, 0)DDRate,S.Name SupplierName
from T_Invoices 
join TC_InvoiceItems on T_Invoices.id=TC_InvoiceItems.Invoice_id
join M_Parties on M_Parties.id=T_Invoices.Customer_id and M_Parties.PartyType_id=15
join M_Parties S on S.id=T_Invoices.Party_id 
join M_Items on M_Items.id=TC_InvoiceItems.Item_id
join MC_ItemUnits on MC_ItemUnits.id=TC_InvoiceItems.Unit_id
join M_Units on M_Units.id =MC_ItemUnits.UnitID_id
where T_Invoices.InvoiceDate between %s and %s 
 '''
                
                if Party > 0:
                    query += " and Party_id=%s"

                query += " group by M_Parties.id,TC_InvoiceItems.Item_id ,TC_InvoiceItems.MRPValue,TC_InvoiceItems.Unit_id,TC_InvoiceItems.Rate "   
          
                if Party > 0:
                    RateDiffQuery= T_Invoices.objects.raw(query, [FromDate,ToDate,Party])
                else:
                    RateDiffQuery= T_Invoices.objects.raw(query, [FromDate,ToDate])
                
                # CustomPrint(RateDiffQuery.query)
                if RateDiffQuery:
                    for row in RateDiffQuery:
                        diff=row.Rate-row.DDRate
                        InvoiceData.append({
                            "XpressName" : row.CXName,
                            "ItemName" : row.ItemName,
                            "MRP" : row.MRPValue,
                            "Quantity" : row.Quantity,
                            "Unit" :row.UnitName,
                            "CXRate" : row.Rate,
                            "DDRate" :row.DDRate,
                            "Diff" : round(diff,2),
                            "SumofDiff" : round(diff*row.Quantity,2),
                            "SupplierName" : row.SupplierName
                        })
                        log_entry = create_transaction_logNew(request, Data, Party, '', 366, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceData})
                else:
                    log_entry = create_transaction_logNew(request, Data, 0, "Report Not Available", 366, 0, FromDate, ToDate, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []})      
        except Exception as e:
            log_entry = create_transaction_logNew(request, Data, 0, 'CxDDDiffReport:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class FranchiseSecondarySaleReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def post(self, request):
        Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = Data['FromDate']
                ToDate = Data['ToDate']
                Party = Data['Party']
                Item = Data['Item']

                # Invoicequery = '''Select T_Invoices.id, M_Parties.Name FranchiseName, M_Parties.SAPPartyCode SAPCode, M_Parties.Name SAPName, T_Invoices.InvoiceDate SaleDate, 
                #         0 ClientID, M_Items.CItemID CItemID, T_Invoices.FullInvoiceNumber BillNumber, M_Items.Name ItemName, A.Quantity, M_Units.Name UnitName,
                #         A.Rate, A.Amount,  M_Parties.MobileNo, M_Items.SAPItemCode MaterialSAPCode,M_Items.IsCBMItem
                #         from T_Invoices
                #         join TC_InvoiceItems A on A.Invoice_id = T_Invoices.id 
                #         join M_Parties on M_Parties.id = T_Invoices.Party_id
                #         join M_Items  on M_Items.id = A.Item_id
                #         join MC_ItemUnits on MC_ItemUnits.id = A.Unit_id
                #         join M_Units on M_Units.id = MC_ItemUnits.UnitID_id
                #         where T_Invoices.InvoiceDate between %s and %s '''
                
                SPOSInvoicequery ='''Select X.id, M_Parties.Name FranchiseName, M_Parties.SAPPartyCode SAPCode, M_Parties.Name SAPName, X.InvoiceDate SaleDate, 
                        X.ClientID, M_Items.CItemID , X.FullInvoiceNumber BillNumber, M_Items.Name ItemName, Y.Quantity, M_Units.Name UnitName, Y.MRPValue Rate, Y.Amount, M_Items.IsCBMItem, M_Parties.MobileNo, M_Items.SAPItemCode MaterialSAPCode
                        from SweetPOS.T_SPOSInvoices X
                        join SweetPOS.TC_SPOSInvoiceItems Y on Y.Invoice_id = X.id 
                        join FoodERP.M_Parties on M_Parties.id = X.Party
                        join FoodERP.M_Items  on M_Items.id = Y.Item 
                        join FoodERP.MC_ItemUnits on MC_ItemUnits.id = Y.Unit
                        join FoodERP.M_Units on M_Units.id = MC_ItemUnits.UnitID_id
                        where X.InvoiceDate between %s and %s '''
                
                parameters = [FromDate,ToDate]
                if int(Party) > 0 and int(Item) > 0: 
                    # Invoicequery += ' AND T_Invoices.Party_id = %s AND A.Item_id = %s'
                    SPOSInvoicequery += ' AND X.Party = %s AND Y.Item = %s'
                    parameters.extend([Party, Item])

                elif int(Party) == 0:
                    # Invoicequery += ' AND A.Item_id = %s'
                    SPOSInvoicequery += ' AND Y.Item = %s'
                    parameters.append(Item)

                elif int(Item) == 0:
                    # Invoicequery += 'AND T_Invoices.Party_id = %s'
                    SPOSInvoicequery += 'AND X.Party = %s'
                    parameters.append(Party)

                    
                # q1 = T_Invoices.objects.raw(Invoicequery,parameters)
                q2 = T_SPOSInvoices.objects.using('sweetpos_db').raw(SPOSInvoicequery,parameters)

                # combined_sale = list(q1) + list(q2)
                combined_sale =  list(q2)

                if combined_sale:
                    
                    ReportdataList = []
                    for a in combined_sale:      
                        if a.IsCBMItem == 1:
                            aa="Yes"
                        else:
                            aa= "No"
                        ReportdataList.append({
                        "id":a.id,
                        "FranchiseName": a.FranchiseName,
                        "SAPCode": a.SAPCode,
                        "SAPName": a.SAPName,
                        "SaleDate": a.SaleDate,
                        "ClientID": a.ClientID,
                        "CItemID": a.CItemID,
                        "BillNumber": a.BillNumber,
                        "ItemName": a.ItemName,
                        "Quantity": a.Quantity,
                        "UnitName": a.UnitName,
                        "Rate": a.Rate,
                        "Amount": a.Amount,
                        "IsCBMItem": aa,
                        "MobileNo": a.MobileNo,
                        "MaterialSAPCode": a.MaterialSAPCode
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': ReportdataList})  
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':  'Data Not Available', 'Data': []}) 
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

