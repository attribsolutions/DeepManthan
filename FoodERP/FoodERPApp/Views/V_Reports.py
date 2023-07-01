from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Views.V_CommFunction import GetOpeningBalance

from ..Serializer.S_Reports import PartyLedgerReportSerializer
from ..models import *


class PartyLedgerReportView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id=0):
        try:
            with transaction.atomic():

                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Customer = Orderdata['Customer']
                Party = Orderdata['Party']

                query=T_Invoices.objects.raw('''select 1 id,InvoiceDate,BillNo,BankName,BranchName,ChequeDate,DocumentNo,ReceiptMode,InvoiceAmount,ReceiptAmt,CashReceiptAmt,Flag from  
                (

SELECT  
            InvoiceDate,
            FullInvoiceNumber BillNo,
            '' AS BankName,
            '' AS BranchName,
            '' AS ChequeDate,
            '' AS DocumentNo,
            '' AS ReceiptMode,
            GrandTotal InvoiceAmount,
            0 AS ReceiptAmt,
            0 AS CashReceiptAmt,
            1 AS Flag 
            FROM T_Invoices where  InvoiceDate between %s and %s 
            and Party_id=%s and Customer_id=%s 

UNION
SELECT  
            ReceiptDate InvoiceDate,
            FullReceiptNumber BillNo,
            M_Bank.Name AS BankName,
            MC_PartyBanks.BranchName AS BranchName,
            ChequeDate ChequeDate,
            DocumentNo DocumentNo,
            M_GeneralMaster.Name AS ReceiptMode,
            0 AS InvoiceAmount,
            CASE
                WHEN ReceiptMode_id = 31 THEN 0
                ELSE AmountPaid
            END ReceiptAmt,
            CASE
                WHEN ReceiptMode_id = 31 THEN AmountPaid
                ELSE 0
            END CashReceiptAmt,
            2 AS Flag 
            from T_Receipts
            LEFT JOIN MC_PartyBanks ON MC_PartyBanks.id = T_Receipts.Bank_id
            LEFT JOIN M_Bank ON M_Bank.id = MC_PartyBanks.Bank_id
            INNER JOIN M_GeneralMaster on M_GeneralMaster.id=T_Receipts.ReceiptMode_id
            where ReceiptDate between %s and %s 
            and T_Receipts.Party_id=%s and T_Receipts.Customer_id=%s
            
UNION
SELECT  
            CRDRNoteDate InvoiceDate,
            FullNoteNumber BillNo,
            '' AS BankName,
            '' AS BranchName,
            '' AS ChequeDate,
            '' AS DocumentNo,
            '' AS ReceiptMode,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN T_CreditDebitNotes.GrandTotal
                ELSE 0
            END) AS InvoiceAmount,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 0
                ELSE T_CreditDebitNotes.GrandTotal
            END) ReceiptAmt,
            0 AS CashReceiptAmt,
            (CASE
                WHEN T_CreditDebitNotes.NoteType_id = 38 THEN 3
                ELSE 4
            END) AS Flag
            from T_CreditDebitNotes
            where T_CreditDebitNotes.CRDRNoteDate between %s and %s 
            and Party_id=%s and Customer_id=%s
)q
ORDER BY InvoiceDate , Flag , BillNo ''',[FromDate,ToDate,Party,Customer,FromDate,ToDate,Party,Customer,FromDate,ToDate,Party,Customer])
                # print(query)
                if not query:
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
                    Opening= GetOpeningBalance(Party,Customer,previous_date)
                    Closing= GetOpeningBalance(Party,Customer,ToDate)
                    temp=0
                    

                    for a in PartyLedgerSerializedata:
                        if temp == 0:
                            temp = (float(Opening) + float(a['InvoiceAmount'])) - (float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        else:
                            temp = (temp + float(a['InvoiceAmount'])) - (float(a['ReceiptAmt'])+float(a['CashReceiptAmt']))
                        
                        PartyLedgerItemDetails.append({
                            "Date": a['InvoiceDate'],
                            "DocumentNO": a['BillNo'],
                            # "Particular": a['BankName']+' '+a['BranchName']+' '+a['DocumentNo']+' '+a['ReceiptMode'],
                            "Particular": '',
                            "Amount": a['InvoiceAmount'],
                            "RecieptAmount": a['ReceiptAmt'],
                            "Cash": a['CashReceiptAmt'],
                            "Balance": temp,
                            
                        })
                    q1=M_Parties.objects.filter(id=Party).values("Name") 
                    q2=M_Parties.objects.filter(id=Customer).values("Name")    
                    PartyLedgerData.append({
                        "FormDate": FromDate,
                        "ToDate" : ToDate,
                        "Distributor": q1[0]['Name'],
                        "CustomerName": q2[0]['Name'],
                        "Open": Opening,
                        "Close": Closing,
                        "InvoiceItems" : PartyLedgerItemDetails
                    })    
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyLedgerData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
