from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_R1_Reports import *
from ..models import  *
from django.http import HttpResponse

class GSTR1ExcelDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                
                   
                B2Bquery = T_Invoices.objects.raw(f'''SELECT T_Invoices.id, M_Parties.GSTIN AS GSTIN_UINOfRecipient,
                                                  M_Parties.Name AS ReceiverName, T_Invoices.FullInvoiceNumber AS InvoiceNumber,'Regular' AS InvoiceType,
                    T_Invoices.InvoiceDate AS InvoiceDate, Sum(TC_InvoiceItems.BasicAmount+TC_InvoiceItems.IGST+TC_InvoiceItems.CGST+TC_InvoiceItems.SGST) AS InvoiceValue,
                    concat(M_States.StateCode, '-', M_States.Name) AS PlaceOfSupply, 'N' AS ReverseCharge,
                    TC_InvoiceItems.GSTPercentage  AS ApplicableOfTaxRate,  
                     SUM(TC_InvoiceItems.BasicAmount) AS TaxableValue,SUM(TC_InvoiceItems.IGST) AS IGST,SUM(TC_InvoiceItems.CGST) AS CGST,
                      SUM(TC_InvoiceItems.SGST)AS SGST,COALESCE(TC_InvoiceUploads.Irn,'') AS IRN ,COALESCE(TC_InvoiceUploads.EInvoiceCreatedOn,'') AS IRNDate,
                    '0' AS CessAmount
                    FROM T_Invoices 
                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                    JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
                    JOIN M_States ON M_States.id = M_Parties.State_id
                    Left JOIN TC_InvoiceUploads ON TC_InvoiceUploads.Invoice_id=T_Invoices.id
                    WHERE Party_id in({Party}) AND InvoiceDate BETWEEN %s AND %s AND M_Parties.GSTIN <> ''
                    GROUP BY M_Parties.GSTIN, M_Parties.Name, T_Invoices.id, T_Invoices.InvoiceDate,
                    M_States.id, M_States.Name, TC_InvoiceItems.GSTPercentage
                    UNION
                    SELECT X.id, M_Parties.GSTIN AS GSTIN_UINOfRecipient,
                                                  M_Parties.Name AS ReceiverName, X.FullInvoiceNumber AS InvoiceNumber,'Regular' AS InvoiceType, 
                    X.InvoiceDate AS InvoiceDate, Sum(Y.BasicAmount+Y.IGST+Y.CGST+Y.SGST ) AS InvoiceValue,
                    concat(M_States.StateCode, '-', M_States.Name) AS PlaceOfSupply, 'N' AS ReverseCharge,
                    Y.GSTPercentage AS ApplicableOfTaxRate, 
                     SUM(Y.BasicAmount) AS TaxableValue,SUM(Y.IGST)AS IGST,SUM(Y.CGST)AS CGST, SUM(Y.SGST)AS SGST,COALESCE(TC_SPOSInvoiceUploads.Irn,'') AS IRN ,COALESCE(TC_SPOSInvoiceUploads.EInvoiceCreatedOn,'') AS IRNDate,
                    '0' AS CessAmount
                    FROM SweetPOS.T_SPOSInvoices X 
                    JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id
                    JOIN M_Parties ON M_Parties.id = X.Customer
                    JOIN M_States ON M_States.id = M_Parties.State_id
                    Left JOIN SweetPOS.TC_SPOSInvoiceUploads ON SweetPOS.TC_SPOSInvoiceUploads.Invoice_id=X.id
                    WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s AND M_Parties.GSTIN <> ''AND X.IsDeleted=0
                    GROUP BY M_Parties.GSTIN, M_Parties.Name, X.id, X.InvoiceDate,
                    M_States.id, M_States.Name, Y.GSTPercentage''', (FromDate, ToDate,FromDate, ToDate))
                # print(B2Bquery)
                B2B2 = B2B3Serializer1(B2Bquery, many=True).data
               
                B2Bquery1 = T_Invoices.objects.raw(f'''SELECT 1 as id, SUM(NoOfRecipients) AS NoOfRecipients, SUM(NoOfInvoices) AS NoOfInvoices, SUM(TotalInvoiceValue) AS TotalInvoiceValue
                                FROM (SELECT count(DISTINCT Customer_id) AS NoOfRecipients,
                                        count(*) AS NoOfInvoices,
                                        sum(T_Invoices.GrandTotal) AS TotalInvoiceValue
                                    FROM T_Invoices 
                                    JOIN M_Parties ON M_Parties.id = T_Invoices.Customer_id
                                    WHERE T_Invoices.Party_id in ({Party}) AND InvoiceDate BETWEEN %s AND %s AND M_Parties.GSTIN != ''
                                    UNION 
                                    SELECT count(DISTINCT Customer) AS NoOfRecipients,
                                        count(*) AS NoOfInvoices,
                                        sum(X.GrandTotal) AS TotalInvoiceValue
                                    FROM SweetPOS.T_SPOSInvoices X 
                                    JOIN M_Parties ON M_Parties.id = X.Customer

                                    WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s AND M_Parties.GSTIN != ''AND X.IsDeleted=0) A''', (FromDate, ToDate,FromDate, ToDate))
                B2B1 = B2BSerializer2(B2Bquery1, many=True).data               
                
                
                if not B2B1:
                    B2B1 = [{
                             'No Of Recipients': None,
                             'No Of Invoices': None, 
                             'Total Invoice Value': None
                             }]                    
                
                if not B2B2:
                    
                    B2B2 = [{
                             'GSTIN / UIN Of Recipient': None, 
                             'Receiver Name': None,
                             'Invoice Number': None,
                             'Invoice Type':None, 
                             'Invoice Date' : None,

                             'Invoice Value (?)': None, 

                             'Place Of Supply': None, 
                             'Reverse Charge': None, 
                             'Applicable Of TaxRate': None,                           
                             'Taxable Value': None,

                             'Integrated Tax (?)':None,
                             'Central Tax (?)':None,
                             'State Tax (?)':None,
                             'Cess Amount (?)': None,
                             'IRN':None,
                             'IRN date':None,
                             
                             
                             }]
                # Example data for the second sheet B2CL
                B2CLquery = T_Invoices.objects.raw(f'''SELECT T_Invoices.id, b.GSTIN AS GSTIN_UINOfRecipient, T_Invoices.FullInvoiceNumber AS InvoiceNumber,'Regular' AS InvoiceType, T_Invoices.InvoiceDate,
                    (T_Invoices.GrandTotal) AS InvoiceValue, CONCAT(M_States.StateCode, '-', M_States.Name) AS PlaceOfSupply,'N' AS ReverseCharge,
                    TC_InvoiceItems.GSTPercentage  AS ApplicableOfTaxRate,
                    SUM(TC_InvoiceItems.BasicAmount) AS TaxableValue,SUM(TC_InvoiceItems.IGST)IGST,SUM(TC_InvoiceItems.CGST)CGST,
                    SUM(TC_InvoiceItems.SGST)SGST,COALESCE(TC_InvoiceUploads.Irn,'') AS IRN ,COALESCE(TC_InvoiceUploads.EInvoiceCreatedOn,'') AS IRNDate, '0' AS CessAmount 
                    FROM T_Invoices 
                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                    JOIN M_Parties a ON a.id=T_Invoices.Party_id
                    JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                    JOIN M_States ON M_States.id=b.State_id
                    Left JOIN TC_InvoiceUploads ON TC_InvoiceUploads.Invoice_id=T_Invoices.id
                    WHERE Party_id in ({Party}) AND InvoiceDate BETWEEN %s AND %s AND b.GSTIN != '' AND b.State_id != a.State_id
                    AND T_Invoices.GrandTotal > 250000
                    GROUP BY T_Invoices.id, T_Invoices.InvoiceDate, M_States.id, M_States.Name, TC_InvoiceItems.GSTPercentage
                    UNION
                    SELECT X.id, b.GSTIN AS GSTIN_UINOfRecipient,X.FullInvoiceNumber AS InvoiceNumber,'Regular' AS InvoiceType, X.InvoiceDate,
                    (X.GrandTotal) AS InvoiceValue, CONCAT(M_States.StateCode, '-', M_States.Name) AS PlaceOfSupply,'N' AS ReverseCharge,
                     Y.GSTPercentage  AS ApplicableOfTaxRate, 
                    SUM(Y.BasicAmount) AS TaxableValue,SUM(Y.IGST)IGST,SUM(Y.CGST)CGST, SUM(Y.SGST)SGST,COALESCE(TC_SPOSInvoiceUploads.Irn,'') AS IRN ,COALESCE(TC_SPOSInvoiceUploads.EInvoiceCreatedOn,'') AS IRNDate, '0' AS CessAmount
                    FROM SweetPOS.T_SPOSInvoices X 
                    JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                    JOIN M_Parties a ON a.id=X.Party
                    JOIN M_Parties b ON b.id=X.Customer
                    JOIN M_States ON M_States.id=b.State_id
                    Left JOIN SweetPOS.TC_SPOSInvoiceUploads ON SweetPOS.TC_SPOSInvoiceUploads.Invoice_id=X.id
                    WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s AND b.GSTIN != '' AND b.State_id != a.State_id
                    AND X.GrandTotal > 250000 AND X.IsDeleted=0
                    GROUP BY X.id, X.InvoiceDate, M_States.id, M_States.Name, Y.GSTPercentage''',( FromDate, ToDate, FromDate, ToDate))
                
                B2CL2 = B2B3Serializer1(B2CLquery, many=True).data
               
                B2CLquery2 = T_Invoices.objects.raw(f'''SELECT 1 AS id, 
                            SUM(NoOfInvoices) AS NoOfInvoices, 
                            SUM(TotalInvoiceValue) AS TotalInvoiceValue
                        FROM (
                            SELECT COUNT(*) AS NoOfInvoices, 
                                SUM(T_Invoices.GrandTotal) AS TotalInvoiceValue
                            FROM T_Invoices
                            JOIN M_Parties a ON a.id = T_Invoices.Party_id
                            JOIN M_Parties b ON b.id = T_Invoices.Customer_id
                            JOIN M_States ON M_States.id = b.State_id
                            WHERE T_Invoices.Party_id in ({Party}) AND T_Invoices.InvoiceDate BETWEEN %s AND %s AND b.GSTIN != '' AND b.State_id != a.State_id AND T_Invoices.GrandTotal > 250000
                            UNION 
                            SELECT COUNT(*) AS NoOfInvoices, 
                            SUM(X.GrandTotal) AS TotalInvoiceValue
                            FROM SweetPOS.T_SPOSInvoices X
                            JOIN M_Parties a ON a.id = X.Party
                            JOIN M_Parties b ON b.id = X.Customer
                            JOIN M_States ON M_States.id = b.State_id
                            WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s AND b.GSTIN != '' AND b.State_id != a.State_id
                            AND X.GrandTotal > 250000 AND X.IsDeleted=0) A''', (FromDate, ToDate, FromDate, ToDate)) 
                B2CL1 = B2CLSerializer2(B2CLquery2, many=True).data              
                # Check if B2CL is empty
                if not B2CL1:
                    B2CL1 = [{
                                'No. Of Invoices': None, 
                                'Total Invoice Value': None
                                }]  
                if not B2CL2:
                        
                    B2CL2 = [{
                             'GSTIN / UIN Of Recipient': None, 
                             'Receiver Name': None,
                             'Invoice Number': None,
                             'Invoice Type':None, 
                             'Invoice Date' : None,

                             'Invoice Value (?)': None, 

                             'Place Of Supply': None, 
                             'Reverse Charge': None, 
                             'Applicable Of TaxRate': None,
                             'Rate': None, 
                             'Taxable Value': None,

                             'Integrated Tax (?)':None,
                             'Central Tax (?)':None,
                             'State Tax (?)':None,
                             'IRN':None,
                             'IRN date':None,
                             'Cess Amount (?)': None,   

                                                       
                             }]
                    
                # Example data for the third sheet B2CS  
                B2CSquery = T_Invoices.objects.raw(f'''SELECT 1 as id, 'OE' Type,concat(M_States.StateCode,'-',M_States.Name)PlaceOfSupply,T_Invoices.FullInvoiceNumber AS InvoiceNumber, T_Invoices.InvoiceDate AS InvoiceDate,
                sum(TC_InvoiceItems.IGST+TC_InvoiceItems.CGST +TC_InvoiceItems.SGST+TC_InvoiceItems.BasicAmount) AS InvoiceValue,
                TC_InvoiceItems.GSTPercentage AS  ApplicableOfTaxRate , sum(TC_InvoiceItems.BasicAmount) TaxableValue, SUM(TC_InvoiceItems.IGST)AS IGST,SUM(TC_InvoiceItems.CGST)AS CGST,
                SUM(TC_InvoiceItems.SGST)AS SGST,'0' CessAmount from T_Invoices 
                JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                JOIN M_Parties a ON a.id=T_Invoices.Party_id
                JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                JOIN M_States ON M_States.id=b.State_id
                where Party_id in ({Party}) and InvoiceDate BETWEEN %s AND %s and  b.GSTIN =''
                and ((a.State_id = b.State_id) OR (a.State_id != b.State_id and T_Invoices.GrandTotal <= 250000))

                group  by M_States.id,M_States.Name,TC_InvoiceItems.GSTPercentage,InvoiceDate

                UNION
                SELECT 1 as id, 'OE' Type,concat(M_States.StateCode,'-',M_States.Name)PlaceOfSupply,X.FullInvoiceNumber AS InvoiceNumber, X.InvoiceDate AS InvoiceDate, sum(Y.IGST+Y.CGST+Y.SGST+Y.BasicAmount) AS InvoiceValue,
                Y.GSTPercentage AS  ApplicableOfTaxRate ,sum(Y.BasicAmount) TaxableValue ,SUM(Y.IGST) AS IGST,SUM(Y.CGST) AS CGST, SUM(Y.SGST) AS SGST ,'0' CessAmount
                from SweetPOS.T_SPOSInvoices X JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                JOIN M_Parties a ON a.id=X.Party
                JOIN M_Parties b ON b.id=X.Customer
                JOIN M_States ON M_States.id=b.State_id

                where X.Party in ({Party}) and X.InvoiceDate BETWEEN %s AND %s and  b.GSTIN ='' AND X.IsDeleted=0
                and ((a.State_id = b.State_id) OR (a.State_id != b.State_id and X.GrandTotal <= 250000 ))

                group  by M_States.id,M_States.Name,Y.GSTPercentage,X.InvoiceDate''',([FromDate],[ToDate],[FromDate],[ToDate]))                                

                B2CS2 = B2CSSerializer(B2CSquery, many=True).data
                
                B2CSquery2 = T_Invoices.objects.raw(f'''
                                SELECT 1 AS id, 
                                    SUM(TotalTaxableValue) AS TotalTaxableValue, 
                                    SUM(TotalCess) AS TotalCess
                                FROM (
                                    SELECT SUM(TC_InvoiceItems.BasicAmount) AS TotalTaxableValue, 0 AS TotalCess
                                    FROM T_Invoices
                                    JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                                    JOIN M_Parties a ON a.id = T_Invoices.Party_id
                                    JOIN M_Parties b ON b.id = T_Invoices.Customer_id
                                    JOIN M_States ON M_States.id = b.State_id
                                    WHERE T_Invoices.Party_id in ({Party}) AND T_Invoices.InvoiceDate BETWEEN %s AND %s AND b.GSTIN = ''
                                    AND ((a.State_id = b.State_id) OR (a.State_id != b.State_id AND T_Invoices.GrandTotal <= 250000))
                                    UNION 
                                    SELECT SUM(Y.BasicAmount) AS TotalTaxableValue,  0 AS TotalCess
                                    FROM SweetPOS.T_SPOSInvoices X
                                    JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id
                                    JOIN M_Parties a ON a.id = X.Party
                                    JOIN M_Parties b ON b.id = X.Customer
                                    JOIN M_States ON M_States.id = b.State_id
                                    WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s AND b.GSTIN = ''AND X.IsDeleted=0
                                    AND ((a.State_id = b.State_id) OR (a.State_id != b.State_id AND X.GrandTotal <= 250000))) A''',([FromDate],[ToDate],[FromDate],[ToDate]))
                                            
                B2CS1 = B2CSSerializer2(B2CSquery2, many=True).data               
               
                
                if not B2B1:
                    B2B1 = [{
                             'Total Taxable Value': None,
                             'Total Cess': None
                             }]                    
               
                if not B2CS2:
                        
                    B2CS2 = [{
                             'Type': None, 
                             'Place Of Supply': None, 
                             'Invoice Number': None,                              
                             'Invoice Date' : None,

                             'Invoice Value (?)': None, 
                             'Applicable Of TaxRate': None,                             
                             'Taxable Value': None,
                             'Integrated Tax (?)':None,
                             'Central Tax (?)':None,
                             'State Tax (?)':None,                             
                             'Cess Amount (?)': None,

                             
                             }]
                
                # Example data for the four sheet CDNR 
                CDNRquery = T_CreditDebitNotes.objects.raw(f'''SELECT T_CreditDebitNotes.id, M_Parties.GSTIN AS GSTIN_UINOfRecipient,M_Parties.Name AS ReceiverName,
                                T_CreditDebitNotes.FullNoteNumber AS NoteNumber,T_CreditDebitNotes.CRDRNoteDate AS NoteDate,M_GeneralMaster.Name NoteTypeName,
                                T_CreditDebitNotes.NoteType_id AS NoteValue,CONCAT(M_States.StateCode, '-', M_States.Name) PlaceOfSupply,
                                'N' ReverseCharge,'Regular' NoteSupplyType,(T_CreditDebitNotes.GrandTotal) GrandTotal,TC_CreditDebitNoteItems.GSTPercentage AS  ApplicableOfTaxRate,
                                TC_CreditDebitNoteItems.GSTPercentage Rate,SUM(TC_CreditDebitNoteItems.BasicAmount) TaxableValue,'0' AS CessAmount,TC_CreditDebitNoteItems.IGST,
                                TC_CreditDebitNoteItems.CGST,TC_CreditDebitNoteItems.SGST,
                                COALESCE(TC_CreditDebitNoteUploads.Irn, '') AS IRN, 
                                COALESCE(TC_CreditDebitNoteUploads.EINvoiceCreatedON ,'')AS EINvoiceCreatedON  FROM T_CreditDebitNotes
                                JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id = T_CreditDebitNotes.id
                                JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                                JOIN M_States ON M_States.id = M_Parties.State_id
                                JOIN M_GeneralMaster ON  M_GeneralMaster.id = T_CreditDebitNotes.NoteType_id
                                left JOIN TC_CreditDebitNoteUploads ON TC_CreditDebitNoteUploads.CRDRNote_id=T_CreditDebitNotes.id
                                WHERE T_CreditDebitNotes.Party_id in ({Party}) AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND M_Parties.GSTIN != '' 
                                GROUP BY T_CreditDebitNotes.id, M_Parties.GSTIN , M_Parties.Name , T_CreditDebitNotes.FullNoteNumber , T_CreditDebitNotes.CRDRNoteDate,NoteTypeName, T_CreditDebitNotes.NoteType_id , M_States.id , M_States.Name , TC_CreditDebitNoteItems.GSTPercentage''',([FromDate],[ToDate]))
                # print(CDNRquery)
                CDNR2 = CDNRSerializer1(CDNRquery, many=True).data
                
                CDNRquery2= T_CreditDebitNotes.objects.raw(f'''SELECT 1 as id, COUNT(DISTINCT A.Customer_id)NoOfRecipients,COUNT(A.CRDRNote_id) NoOfNotes,SUM(A.GrandTotal) TotalInvoiceValue,SUM(A.TaxbleAmount) TotalTaxableValue, 0 TotalCess
                        FROM (
                        SELECT  T_CreditDebitNotes.Customer_id,TC_CreditDebitNoteItems.CRDRNote_id,T_CreditDebitNotes.GrandTotal,SUM(TC_CreditDebitNoteItems.BasicAmount) TaxbleAmount
                        FROM TC_CreditDebitNoteItems
                        JOIN T_CreditDebitNotes ON T_CreditDebitNotes.id= TC_CreditDebitNoteItems.CRDRNote_id
                        JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                        WHERE Party_id in ({Party}) and T_CreditDebitNotes.CRDRNoteDate BETWEEN  %s  AND %s AND M_Parties.GSTIN != ''  Group by T_CreditDebitNotes.id)A''',([FromDate],[ToDate]))
                                
                CDNR1 = CDNRSerializer2(CDNRquery2, many=True).data               
                
                
                if not CDNR1:
                    CDNR1 = [{
                             'No. Of Recipients': None,
                             'No. Of Notes': None,
                             'Total Invoice Value': None,
                             'Total Taxable Value': None,
                             'Total Cess': None
                             }]    
                    
                    if not CDNR2:
                        CDNR2 = [{
                             'GSTIN / UIN Of Recipient': None, 
                             'Receiver Name': None,
                             'Note Type': None,
                             'Note Number': None, 
                             'Note Date': None, 
                             'Note Value': None,
                             'Place Of Supply': None, 
                             'Reverse Charge': None,
                             'Rate': None,
                            #  'Applicable Of TaxRate': None,                              
                             'Taxable Value': None,

                             'Integrated Tax (?)' : None,
                             'Central Tax (?)':None,
                             'State Tax (?)':None, 

                             'Cess Amount': None,                                                         
                             'IRN':None,
                             'INR Date':None,
                             }]
                
                # Example data for the five sheet CDNUR 
                CDNURquery = T_CreditDebitNotes.objects.raw(f'''SELECT T_CreditDebitNotes.id,'' URType, T_CreditDebitNotes.FullNoteNumber AS NoteNumber,T_CreditDebitNotes.CRDRNoteDate AS NoteDate, 
                                                            (CASE WHEN T_CreditDebitNotes.NoteType_id = 37 THEN 'C' ELSE 'D' END) NoteTypeID,
                                                            CONCAT(M_States.StateCode, '-', M_States.Name) PlaceOfSupply, (T_CreditDebitNotes.GrandTotal) NoteValue,
                                                            '' ApplicableOfTaxRate,TC_CreditDebitNoteItems.GSTPercentage Rate, SUM(TC_CreditDebitNoteItems.BasicAmount) TaxableValue, '' CessAmount
                        FROM T_CreditDebitNotes
                        JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id = T_CreditDebitNotes.id
                        JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                        JOIN M_States ON M_States.id = M_Parties.State_id
                        WHERE T_CreditDebitNotes.Party_id in ({Party}) AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND M_Parties.GSTIN = ''
                        GROUP BY  M_Parties.Name ,T_CreditDebitNotes.CRDRNoteDate,M_States.id ,M_States.Name ,TC_CreditDebitNoteItems.GSTPercentage''',([FromDate],[ToDate]))
                        
                        # CustomPrint(CDNURquery.query)
                CDNUR2 = CDNURSerializer(CDNURquery, many=True).data
                
                CDNURquery2= T_CreditDebitNotes.objects.raw(f'''SELECT 1 as id, COUNT(DISTINCT A.Customer_id)NoOfRecipients,COUNT(A.CRDRNote_id) NoOfNotes,SUM(A.GrandTotal) TotalNoteValue,SUM(A.TaxbleAmount)
                TotalTaxableValue, 0 TotalCess
                FROM (SELECT T_CreditDebitNotes.Customer_id, TC_CreditDebitNoteItems.CRDRNote_id,T_CreditDebitNotes.GrandTotal,
                SUM(TC_CreditDebitNoteItems.BasicAmount) TaxbleAmount 
                FROM TC_CreditDebitNoteItems 
                JOIN T_CreditDebitNotes ON T_CreditDebitNotes.id= TC_CreditDebitNoteItems.CRDRNote_id
                JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id 
                WHERE Party_id in ({Party}) and T_CreditDebitNotes.CRDRNoteDate BETWEEN
                %s AND  %s AND M_Parties.GSTIN = '' Group by T_CreditDebitNotes.id)A''',([FromDate],[ToDate]))
                    
                CDNUR1 = CDNURSerializer2(CDNURquery2, many=True).data
                
                if not CDNUR1:
                    CDNUR1 = [{
                             'No. Of Notes': None,
                             'Total Note Value': None,
                             'Total Taxable Value': None,
                             'Total Cess': None
                             }]
                    
                if not CDNUR2:
                    CDNUR2 = [{
                             'UR Type': None,
                             'Note Number': None, 
                             'Note Date': None, 
                             'Note Type': None, 
                             'Place Of Supply': None, 
                             'Note Value': None,
                             'Applicable Of TaxRate': None,
                             'Rate': None, 
                             'Taxable Value': None,
                             'Cess Amount': None }]
                
                # Example data for the six sheet CDNUR
                EXEMPquery = T_Invoices.objects.raw(f'''SELECT 1 as id , 'Inter-State supplies to registered persons' Descriptionn,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id  
                        WHERE Party_id in ({Party}) and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage= 0  and a.State_id != b.State_id group by id,Descriptionn
                        UNION
                        SELECT 1 as id , 'Inter-State supplies to registered persons' Descriptionn,sum(Y.Amount) Total
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party}) and X.InvoiceDate BETWEEN %s AND %s and b.GSTIN != '' and Y.GSTPercentage= 0  and a.State_id != b.State_id group by id,Descriptionn                                                        
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to registered persons' Descriptionn,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id in ({Party})  and T_Invoices.InvoiceDate BETWEEN  %s AND %s  and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Descriptionn
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to registered persons' Descriptionn,sum(Y.Amount) Total
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party})  and X.InvoiceDate BETWEEN  %s AND %s  and b.GSTIN != '' and Y.GSTPercentage = 0  and a.State_id = b.State_id group by id,Descriptionn                                                       
                        UNION
                        SELECT 1 as id, 'Inter-State supplies to unregistered persons' Descriptionn,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id in ({Party})  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id != b.State_id group by id,Descriptionn
                        UNION
                        SELECT 1 as id, 'Inter-State supplies to unregistered persons' Descriptionn,sum(Y.Amount) Total
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party})  and X.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and Y.GSTPercentage = 0  and a.State_id != b.State_id group by id,Descriptionn     
                        UNION                                                   
                        SELECT 1 as id, 'Intra-State supplies to unregistered persons' Descriptionn,sum(TC_InvoiceItems.Amount) Total
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id in ({Party})  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Descriptionn
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to unregistered persons' Descriptionn,sum(Y.Amount) Total
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party})  and X.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and Y.GSTPercentage = 0  and a.State_id = b.State_id group by id,Descriptionn                                                        
                        ''',([FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate]))
                
                EXEMP2 = EXEMPSerializer(EXEMPquery, many=True).data
                 
                EXEMPquery2= T_Invoices.objects.raw(f''' SELECT 1 as id, '' AA,sum(A.Total) TotalNilRatedSupplies,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                FROM (SELECT 1 as id , 'Inter-State supplies to registered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id  
                        WHERE Party_id in ({Party}) and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage= 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id , 'Inter-State supplies to registered persons' Description,sum(Y.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer  
                        WHERE X.Party in ({Party})and X.InvoiceDate BETWEEN %s AND %s and b.GSTIN != '' and Y.GSTPercentage= 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to registered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id in ({Party}) and T_Invoices.InvoiceDate BETWEEN  %s AND %s  and b.GSTIN != '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to registered persons' Description,sum(Y.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party})  and X.InvoiceDate BETWEEN  %s AND %s  and b.GSTIN != '' and Y.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description                                                        
                        UNION
                        SELECT 1 as id, 'Inter-State supplies to unregistered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id in ({Party})  and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id != b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Inter-State supplies to unregistered persons' Description,sum(Y.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party})and X.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and Y.GSTPercentage = 0  and a.State_id != b.State_id group by id,Description                           
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to unregistered persons' Description,sum(TC_InvoiceItems.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM T_Invoices
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_Parties a ON a.id=T_Invoices.Party_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        WHERE Party_id in ({Party}) and T_Invoices.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and TC_InvoiceItems.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description
                        UNION
                        SELECT 1 as id, 'Intra-State supplies to unregistered persons' Description,sum(Y.Amount) Total,'' TotalExemptedSupplies,'' TotalNonGSTSupplies
                        FROM SweetPOS.T_SPOSInvoices X
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y  ON Y.Invoice_id=X.id
                        JOIN M_Parties a ON a.id=X.Party
                        JOIN M_Parties b ON b.id=X.Customer
                        WHERE X.Party in ({Party}) and X.InvoiceDate BETWEEN %s AND %s and b.GSTIN = '' and Y.GSTPercentage = 0  and a.State_id = b.State_id group by id,Description)A''',([FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate],[FromDate],[ToDate]))
                           
                EXEMP1 = EXEMP2Serializer2(EXEMPquery2, many=True).data
            
                if not EXEMP1:
                    EXEMP1 = [{
                             'Total Nil Rated Supplies': None,
                             'Total Exempted Supplies': None,
                             'Total Non GST Supplies': None
                             }]
                    
                if not EXEMP2:
                    EXEMP2 = [{
                             'Description': None,
                             'Nil Rated Supplies': None,
                             'Exempted Other Than NilRated Non GST Supply': None,
                             'Non GST Supplies': None
                             }]
                
                # Example data for the seven sheet HSN 


                HSNquery = T_Invoices.objects.raw(f'''SELECT 1 as id, M_GSTHSNCode.HSNCode AS HSN, M_Units.EwayBillUnit AS UQC,

                       sum(UnitwiseQuantityConversion(TC_InvoiceItems.item_id,TC_InvoiceItems.QtyInNo,0,1,0,M_Units.id ,0)) TotalQuantity,sum(TC_InvoiceItems.Amount)TotalValue,
                        sum(TC_InvoiceItems.BasicAmount) TaxableValue, sum(TC_InvoiceItems.IGST)IntegratedTaxAmount,
                        sum(TC_InvoiceItems.CGST)CentralTaxAmount,
                        sum(TC_InvoiceItems.SGST)StateUTTaxAmount, '' CessAmount,TC_InvoiceItems.GSTPercentage Rate
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                        WHERE Party_id in ({Party}) and T_Invoices.InvoiceDate BETWEEN %s AND %s  
                        Group by  M_GSTHSNCode.HSNCode,TC_InvoiceItems.GSTPercentage,M_Units.id
                        UNION


                        SELECT 1 as id, Y.HSNCode AS HSN, M_Units.EwayBillUnit AS UQC,

                        sum(UnitwiseQuantityConversion(Y.Item,Y.QtyInNo,0,1,0,M_Units.id,0)) TotalQuantity,sum(Y.Amount)TotalValue,sum(Y.BasicAmount) TaxableValue, 
                        sum(Y.IGST)IntegratedTaxAmount,sum(Y.CGST)CentralTaxAmount,sum(Y.SGST)StateUTTaxAmount, 
                        '' CessAmount,Y.GSTPercentage Rate
                        FROM SweetPOS.T_SPOSInvoices X 
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id                          
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=Y.Unit
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id                      

                        WHERE X.Party in ({Party}) and X.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0 
                        Group by  Y.HSNCode,Y.GSTPercentage,M_Units.id''',([FromDate],[ToDate],[FromDate],[ToDate]))
                
                HSN2 = HSNSerializer1(HSNquery, many=True).data
                # print(HSNquery)
                HSNquery2= T_Invoices.objects.raw(f'''SELECT 1 as id, COUNT(DISTINCT A.HSNCode) AS NoOfHSN,
                            SUM(A.TotalValue) AS TotalValue, SUM(A.TaxableValue) AS TotalTaxableValue,
                    SUM(A.IntegratedTaxAmount) AS TotalIntegratedTaxAmount, SUM(A.CentralTaxAmount) AS TotalCentralTaxAmount,
                            SUM(A.StateUTTaxAmount) AS TotalStateUTTaxAmount, '' AS TotalCessAmount
                        FROM (
                            SELECT 1 as id, M_GSTHSNCode.HSNCode, M_Items.Name AS Description, 'NOS-NUMBERS' AS UQC,
                            SUM(TC_InvoiceItems.QtyInNo) AS TotalQuantity, SUM(TC_InvoiceItems.Amount) AS TotalValue,
                            SUM(TC_InvoiceItems.BasicAmount) AS TaxableValue, SUM(TC_InvoiceItems.IGST) AS IntegratedTaxAmount,
                            SUM(TC_InvoiceItems.CGST) AS CentralTaxAmount, SUM(TC_InvoiceItems.SGST) AS StateUTTaxAmount, '' AS CessAmount
                            FROM T_Invoices 
                                JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                                JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TC_InvoiceItems.GST_id
                                JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
                            WHERE T_Invoices.Party_id in ({Party}) AND T_Invoices.InvoiceDate BETWEEN %s AND %s  
                            GROUP BY id, M_GSTHSNCode.HSNCode, M_Items.Name
                            UNION
                            SELECT 1 as id, Y.HSNCode, M_Items.Name AS Description, 'NOS-NUMBERS' AS UQC,
                            SUM(Y.QtyInNo) AS TotalQuantity, SUM(Y.Amount) AS TotalValue, SUM(Y.BasicAmount) AS TaxableValue,
                            SUM(Y.IGST) AS IntegratedTaxAmount, SUM(Y.CGST) AS CentralTaxAmount, SUM(Y.SGST) AS StateUTTaxAmount, '' AS CessAmount
                            FROM SweetPOS.T_SPOSInvoices X 
                                JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id                               
                                JOIN M_Items ON M_Items.id = Y.Item
                            WHERE X.Party in ({Party})AND X.InvoiceDate BETWEEN %s AND %s  AND X.IsDeleted=0
                            GROUP BY id, Y.HSNCode, M_Items.Name) A''',([FromDate],[ToDate],[FromDate],[ToDate]))
                # print(HSNquery2)                   
                HSN1 = HSN2Serializer2(HSNquery2, many=True).data  
                
                if not HSN1:
                    HSN1 = [{
                             'No. Of HSN': None,
                             'Total Value': None,
                             'Total Invoice Value': None,
                             'Total Integrated Tax Amount': None,
                             'Total Central Tax Amount': None,
                             'Total State UT Tax Amount': None,
                             'Total Cess Amount': None,
                             }]                   
                
                if not HSN2:
                    HSN2 = [{
                            'HSN': None, 
                            'Description': None,
                            'UQC': None, 
                            'Total Quantity': None, 
                            'Rate':None,
                            'Total Value': None, 
                            'Taxable Value': None, 
                            'Integrated Tax Amount': None,
                            'Central Tax Amount': None,
                            'State UT Tax Amount': None,
                            }]
                
                # Example data for the eight sheet Docs  
                Docsquery = T_Invoices.objects.raw(f'''SELECT 1 as id, NatureOfDocument, Sr_No_From,
                            Sr_No_To, TotalNumber,Cancelled, b
                            FROM (SELECT 'Invoices for outward supply' as NatureOfDocument, (SELECT FullInvoiceNumber FROM T_Invoices T WHERE T.InvoiceNumber = MIN(T_Invoices.InvoiceNumber) AND Party_id in({Party}) LIMIT 1) AS Sr_No_From,
(SELECT FullInvoiceNumber FROM T_Invoices T WHERE T.InvoiceNumber = MAX(T_Invoices.InvoiceNumber) AND Party_id in ({Party}) LIMIT 1) AS Sr_No_To, COUNT(*) as TotalNumber, (SELECT COUNT(*) FROM T_DeletedInvoices WHERE Party in({Party}) AND T_DeletedInvoices.InvoiceDate BETWEEN '{FromDate}' AND'{ToDate}') as Cancelled, '1' as b
                            FROM T_Invoices  
                            WHERE Party_id in ({Party}) AND InvoiceDate BETWEEN %s AND %s
                            UNION ALL
                            SELECT 'Invoices for outward supply' as NatureOfDocument, (SELECT FullInvoiceNumber FROM SweetPOS.T_SPOSInvoices TS WHERE TS.InvoiceNumber = MIN(X.InvoiceNumber) AND Party in({Party}) LIMIT 1) AS Sr_No_From,
(SELECT FullInvoiceNumber FROM SweetPOS.T_SPOSInvoices TS WHERE TS.InvoiceNumber = MAX(X.InvoiceNumber) AND Party in({Party}) LIMIT 1) AS Sr_No_To, COUNT(*) as TotalNumber,(SELECT COUNT(*) FROM SweetPOS.T_SPOSDeletedInvoices WHERE Party in({Party}) AND T_SPOSDeletedInvoices.InvoiceDate BETWEEN '{FromDate}' AND'{ToDate}') as Cancelled, '1' as b
                            FROM SweetPOS.T_SPOSInvoices X 
                            JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id
                            JOIN M_GSTHSNCode ON M_GSTHSNCode.id = Y.HSNCode
                            JOIN M_Items ON M_Items.id = Y.Item
                            WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s
                            UNION
                            SELECT 'Credit Note' as NatureOfDocument, MIN(T_CreditDebitNotes.FullNoteNumber) as Sr_No_From,
                            MAX(T_CreditDebitNotes.FullNoteNumber) as Sr_No_To, COUNT(*) as TotalNumber, 0 as Cancelled, '2' as b
                            FROM T_CreditDebitNotes
                            WHERE T_CreditDebitNotes.NoteType_id = 37 AND Party_id in ({Party}) AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
                            UNION
                            SELECT 'Debit Note' as NatureOfDocument, MIN(T_CreditDebitNotes.FullNoteNumber) as Sr_No_From,
                            MAX(T_CreditDebitNotes.FullNoteNumber) as Sr_No_To, COUNT(*) as TotalNumber, 0 as Cancelled, '3' as b
                            FROM T_CreditDebitNotes  
                            WHERE T_CreditDebitNotes.NoteType_id = 38 AND Party_id in ({Party}) AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s) AS subquery 
                            GROUP BY NatureOfDocument, b''', [FromDate, ToDate, FromDate, ToDate, FromDate, ToDate, FromDate, ToDate])
                print(Docsquery)                                         
                Docs2 = DocsSerializer(Docsquery, many=True).data
            
                Docsquery2 = T_Invoices.objects.raw(f'''SELECT 1 as id, '' AA, '' bb, '' cc, SUM(A.cnt) AS TotalNumbers, SUM(A.TotalCancelled) AS TotalCancelled
                                    FROM (SELECT 1 as id, 'Invoices for outward supply' AS a,MIN(T_Invoices.InvoiceNumber) AS MINID,
                                        MAX(T_Invoices.InvoiceNumber) AS MAXID, COUNT(*) AS cnt,
                                        (SELECT COUNT(*) FROM T_DeletedInvoices WHERE Party in ({Party}) AND T_DeletedInvoices.InvoiceDate BETWEEN %s AND %s) AS TotalCancelled, '1' AS b
                                    FROM T_Invoices  
                                    WHERE Party_id in ({Party}) AND T_Invoices.InvoiceDate BETWEEN %s AND %s
                                    UNION 
                                    SELECT 1 as id, 'Credit Note' AS a, MIN(T_CreditDebitNotes.FullNoteNumber) AS MINID,
                                        MAX(T_CreditDebitNotes.FullNoteNumber) AS MAXID, COUNT(*) AS TotalNumbers, '0' AS TotalCancelled, '2' AS b
                                    FROM T_CreditDebitNotes
                                    WHERE T_CreditDebitNotes.NoteType_id = 37 AND Party_id in ({Party}) AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
                                    UNION 
                                    SELECT 1 as id, 'Debit Note' AS a, MIN(T_CreditDebitNotes.FullNoteNumber) AS MINID,
                                        MAX(T_CreditDebitNotes.FullNoteNumber) AS MAXID, COUNT(*) AS TotalNumbers, '0' AS TotalCancelled, '3' AS b
                                    FROM T_CreditDebitNotes  
                                    WHERE T_CreditDebitNotes.NoteType_id = 38 AND Party_id in ({Party}) AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s
                                    UNION
                                    SELECT 1 as id, 'Invoices for outward supply' AS a, MIN(X.InvoiceNumber) AS MINID, MAX(X.InvoiceNumber) AS MAXID,
                                        COUNT(*) AS cnt, (SELECT COUNT(*) FROM SweetPOS.T_SPOSDeletedInvoices WHERE Party in ({Party}) AND T_SPOSDeletedInvoices.InvoiceDate BETWEEN %s AND %s) AS TotalCancelled, '4' AS b
                                    FROM SweetPOS.T_SPOSInvoices X
                                    WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s) A''', [FromDate, ToDate, FromDate, ToDate,FromDate, ToDate, FromDate, ToDate, FromDate, ToDate, FromDate, ToDate])
                # print(Docsquery2)          
                Docs1 = Docs2Serializer2(Docsquery2, many=True).data
                
                if not Docs1:
                    Docs1 = [{
                             'Total Numbers': None,
                             'Total Cancelled': None,
                             }]
                    
                if not Docs2:
                    Docs2 = [{
                             'Nature Of Document': None,
                             'Sr. No. From': None,
                             'Sr. No. To': None,
                             'Total Number': None,
                             'Cancelled': None
                             }]
                # Example data for the nine sheet HSN With GSTIN


                HSNquery3 = T_Invoices.objects.raw(f'''SELECT 1 as id, M_GSTHSNCode.HSNCode AS HSN,M_Items.Name Description,M_Units.EwayBillUnit AS UQC,

                        sum(UnitwiseQuantityConversion(M_Items.id,TC_InvoiceItems.QtyInNo,0,1,0,M_Units.id ,0)) TotalQuantity,sum(TC_InvoiceItems.Amount)TotalValue,
                        sum(TC_InvoiceItems.BasicAmount) TaxableValue, sum(TC_InvoiceItems.IGST)IntegratedTaxAmount,
                        sum(TC_InvoiceItems.CGST)CentralTaxAmount,
                        sum(TC_InvoiceItems.SGST)StateUTTaxAmount,TC_InvoiceItems.GSTPercentage Rate
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                        JOIN M_Items ON M_Items.id=TC_InvoiceItems.Item_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id

                        WHERE Party_id in ({Party})  and T_Invoices.InvoiceDate BETWEEN %s AND %s   AND b.GSTIN!=''
                        Group by M_Items.id, M_GSTHSNCode.HSNCode,TC_InvoiceItems.GSTPercentage,M_Units.id
                        UNION


                        SELECT 1 as id, Y.HSNCode AS HSN, M_Items.Name AS Description,M_Units.EwayBillUnit AS UQC,

                        sum(UnitwiseQuantityConversion(M_Items.id,Y.QtyInNo,0,1,0,M_Units.id,0)) TotalQuantity,sum(Y.Amount)TotalValue,sum(Y.BasicAmount) TaxableValue, 
                        sum(Y.IGST)IntegratedTaxAmount,sum(Y.CGST)CentralTaxAmount,sum(Y.SGST)StateUTTaxAmount, 
                        Y.GSTPercentage Rate
                        FROM SweetPOS.T_SPOSInvoices X 
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id                        

                        JOIN M_Items ON M_Items.id=Y.Item
                        JOIN M_Parties b ON b.id=X.Customer  
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=Y.Unit
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id                     

                        WHERE X.Party in ({Party}) and X.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0  AND b.GSTIN!=''
                        Group by M_Items.id, Y.HSNCode,Y.GSTPercentage,M_Units.EwayBillUnit''',([FromDate],[ToDate],[FromDate],[ToDate]))
                
                HSN3 = HSNSerializerWithDescription(HSNquery3, many=True).data
                
                HSNquery4= T_Invoices.objects.raw(f'''SELECT 1 as id, M_GSTHSNCode.HSNCode AS HSN,M_Items.Name Description,M_Units.EwayBillUnit AS UQC,

                        sum(UnitwiseQuantityConversion(M_Items.id,TC_InvoiceItems.QtyInNo,0,1,0,M_Units.id ,0)) TotalQuantity,sum(TC_InvoiceItems.Amount)TotalValue,
                        sum(TC_InvoiceItems.BasicAmount) TaxableValue, sum(TC_InvoiceItems.IGST)IntegratedTaxAmount,
                        sum(TC_InvoiceItems.CGST)CentralTaxAmount,
                        sum(TC_InvoiceItems.SGST)StateUTTaxAmount,TC_InvoiceItems.GSTPercentage Rate
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                        JOIN M_Items ON M_Items.id=TC_InvoiceItems.Item_id
                        JOIN M_Parties b ON b.id=T_Invoices.Customer_id
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id

                        WHERE Party_id in ({Party}) and T_Invoices.InvoiceDate BETWEEN %s AND %s   AND b.GSTIN=''
                        Group by M_Items.id, M_GSTHSNCode.HSNCode,TC_InvoiceItems.GSTPercentage,M_Units.id
                        UNION


                        SELECT 1 as id, Y.HSNCode AS HSN, M_Items.Name AS Description,M_Units.EwayBillUnit AS UQC,
                        sum(UnitwiseQuantityConversion(M_Items.id,Y.QtyInNo,0,1,0,M_Units.id,0)) TotalQuantity,sum(Y.Amount)TotalValue,sum(Y.BasicAmount) TaxableValue, 
                        sum(Y.IGST)IntegratedTaxAmount,sum(Y.CGST)CentralTaxAmount,sum(Y.SGST)StateUTTaxAmount, 
                        Y.GSTPercentage Rate
                        FROM SweetPOS.T_SPOSInvoices X 
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id                        

                        JOIN M_Items ON M_Items.id=Y.Item
                        JOIN M_Parties b ON b.id=X.Customer  
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=Y.Unit
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id                     

                        WHERE X.Party in ({Party})  and X.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0  AND b.GSTIN=''
                        Group by M_Items.id, Y.HSNCode,Y.GSTPercentage,M_Units.id''',([FromDate],[ToDate],[FromDate],[ToDate]))
                                  
                HSN4 = HSNSerializerWithDescription(HSNquery4, many=True).data  
                
                if not HSN3:
                    HSN3 = [{
                            'HSN': None,                             
                            'UQC': None, 
                            'Total Quantity': None, 
                            'Rate':None,
                            'Total Value': None, 
                            'Taxable Value': None, 
                            'Integrated Tax Amount': None,                            
                            'State UT Tax Amount': None,
                            }]                 
                
                if not HSN4:
                    HSN4 = [{
                            'HSN': None,                             
                            'UQC': None, 
                            'Total Quantity': None, 
                            'Rate':None,
                            'Total Value': None, 
                            'Taxable Value': None, 
                            'Integrated Tax Amount': None,                            
                            'State UT Tax Amount': None,
                            }]
                #HSN with Description 
                HSNquery5 = T_Invoices.objects.raw(f'''SELECT 1 as id, M_GSTHSNCode.HSNCode AS HSN,M_Items.Name Description, M_Units.EwayBillUnit AS UQC,

                       sum(UnitwiseQuantityConversion(TC_InvoiceItems.item_id,TC_InvoiceItems.QtyInNo,0,1,0,M_Units.id ,0)) TotalQuantity,sum(TC_InvoiceItems.Amount)TotalValue,
                        sum(TC_InvoiceItems.BasicAmount) TaxableValue, sum(TC_InvoiceItems.IGST)IntegratedTaxAmount,
                        sum(TC_InvoiceItems.CGST)CentralTaxAmount,
                        sum(TC_InvoiceItems.SGST)StateUTTaxAmount, '' CessAmount,TC_InvoiceItems.GSTPercentage Rate
                        FROM T_Invoices 
                        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
                        JOIN M_GSTHSNCode ON M_GSTHSNCode.id=TC_InvoiceItems.GST_id
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=TC_InvoiceItems.Unit_id
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id
                        JOIN M_Items ON M_Items.id =TC_InvoiceItems.Item_id
                        WHERE Party_id in ({Party})  and T_Invoices.InvoiceDate BETWEEN %s AND %s  
                        Group by  M_GSTHSNCode.HSNCode,TC_InvoiceItems.GSTPercentage,M_Units.id,M_Items.id
                        UNION


                        SELECT 1 as id, Y.HSNCode AS HSN,M_Items.Name Description, M_Units.EwayBillUnit AS UQC,

                        sum(UnitwiseQuantityConversion(Y.Item,Y.QtyInNo,0,1,0,M_Units.id,0)) TotalQuantity,sum(Y.Amount)TotalValue,sum(Y.BasicAmount) TaxableValue, 
                        sum(Y.IGST)IntegratedTaxAmount,sum(Y.CGST)CentralTaxAmount,sum(Y.SGST)StateUTTaxAmount, 
                        '' CessAmount,Y.GSTPercentage Rate
                        FROM SweetPOS.T_SPOSInvoices X 
                        JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id=X.id                          
                        JOIN MC_ItemUnits ON MC_ItemUnits.id=Y.Unit
                        JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id                      
                        JOIN M_Items ON M_Items.id=SweetPOS.Y.Item
                        WHERE X.Party in ({Party})  and X.InvoiceDate BETWEEN %s AND %s AND X.IsDeleted=0 
                        Group by  Y.HSNCode,Y.GSTPercentage,M_Units.id,M_Items.id''',([FromDate],[ToDate],[FromDate],[ToDate]))
                
                HSN5 = HSNSerializerWithDescription(HSNquery5, many=True).data
                
                HSNquery6= T_Invoices.objects.raw(f'''SELECT 1 as id, COUNT(DISTINCT A.HSNCode) AS NoOfHSN,
                            SUM(A.TotalValue) AS TotalValue, SUM(A.TaxableValue) AS TotalTaxableValue,
                    SUM(A.IntegratedTaxAmount) AS TotalIntegratedTaxAmount, SUM(A.CentralTaxAmount) AS TotalCentralTaxAmount,
                            SUM(A.StateUTTaxAmount) AS TotalStateUTTaxAmount, '' AS TotalCessAmount
                        FROM (
                            SELECT 1 as id, M_GSTHSNCode.HSNCode, M_Items.Name AS Description, 'NOS-NUMBERS' AS UQC,
                            SUM(TC_InvoiceItems.QtyInNo) AS TotalQuantity, SUM(TC_InvoiceItems.Amount) AS TotalValue,
                            SUM(TC_InvoiceItems.BasicAmount) AS TaxableValue, SUM(TC_InvoiceItems.IGST) AS IntegratedTaxAmount,
                            SUM(TC_InvoiceItems.CGST) AS CentralTaxAmount, SUM(TC_InvoiceItems.SGST) AS StateUTTaxAmount, '' AS CessAmount
                            FROM T_Invoices 
                                JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id = T_Invoices.id
                                JOIN M_GSTHSNCode ON M_GSTHSNCode.id = TC_InvoiceItems.GST_id
                                JOIN M_Items ON M_Items.id = TC_InvoiceItems.Item_id
                            WHERE T_Invoices.Party_id in ({Party}) AND T_Invoices.InvoiceDate BETWEEN %s AND %s  
                            GROUP BY id, M_GSTHSNCode.HSNCode, M_Items.Name
                            UNION
                            SELECT 1 as id, Y.HSNCode, M_Items.Name AS Description, 'NOS-NUMBERS' AS UQC,
                            SUM(Y.QtyInNo) AS TotalQuantity, SUM(Y.Amount) AS TotalValue, SUM(Y.BasicAmount) AS TaxableValue,
                            SUM(Y.IGST) AS IntegratedTaxAmount, SUM(Y.CGST) AS CentralTaxAmount, SUM(Y.SGST) AS StateUTTaxAmount, '' AS CessAmount
                            FROM SweetPOS.T_SPOSInvoices X 
                                JOIN SweetPOS.TC_SPOSInvoiceItems Y ON Y.Invoice_id = X.id                               
                                JOIN M_Items ON M_Items.id = Y.Item
                            WHERE X.Party in ({Party}) AND X.InvoiceDate BETWEEN %s AND %s  AND X.IsDeleted=0
                            GROUP BY id, Y.HSNCode, M_Items.Name) A''',([FromDate],[ToDate], [FromDate],[ToDate]))
                # print(HSNquery2)                   
                HSN6 = HSN2Serializer2(HSNquery6, many=True).data  
                
                if not HSN5:
                    HSN5 = [{
                             'No. Of HSN': None,                             
                             'Total Value': None,
                             'Total Invoice Value': None,
                             'Total Integrated Tax Amount': None,
                             'Total Central Tax Amount': None,
                             'Total State UT Tax Amount': None,
                             'Total Cess Amount': None,
                             }]                   
                
                if not HSN6:
                    HSN6 = [{
                            'HSN': None, 
                            'Description': None,
                            'UQC': None, 
                            'Total Quantity': None, 
                            'Rate':None,
                            'Total Value': None, 
                            'Taxable Value': None, 
                            'Integrated Tax Amount': None,
                            'Central Tax Amount': None,
                            'State UT Tax Amount': None,
                            }]
                
                response_data = {                    
                    
                    "B2B":  B2B1  + B2B2,
                    "B2CL": B2CL1  + B2CL2,
                    "B2CS":  B2CS1 + B2CS2,
                    "CDNR": CDNR1  + CDNR2,
                    "CDNUR":  CDNUR1 + CDNUR2,
                    "EXEMP": EXEMP1 + EXEMP2,
                    "HSN":  HSN1  + HSN2,
                    "WithGSTIN": HSN3  ,
                    "WithOutGSTIN": HSN4,
                    "Docs": Docs1 + Docs2, 
                    "HSN With Discription" :HSN5  + HSN6,
                    
                }
                
                # CustomPrint( B2B1 + B2B2 )
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': response_data})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
             
