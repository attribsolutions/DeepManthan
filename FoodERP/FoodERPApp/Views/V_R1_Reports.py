from decimal import Decimal
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_R1_Reports import *
 
from ..models import  *
import io

from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment
import pandas as pd

class GSTR1ExcelDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        try:
            with transaction.atomic():
                Orderdata = JSONParser().parse(request)
                FromDate = Orderdata['FromDate']
                ToDate = Orderdata['ToDate']
                Party = Orderdata['Party']
                
                # Create a new workbook
                wb = Workbook()
                ws = wb.active
                ws.title = 'B2B'
                B2Bquery = T_Invoices.objects.raw('''SELECT T_Invoices.id, M_Parties.GSTIN , M_Parties.Name,T_Invoices.FullInvoiceNumber,T_Invoices.InvoiceDate,(T_Invoices.GrandTotal+T_Invoices.TCSAmount)GrandTotal,
        concat(M_States.StateCode,'-',M_States.Name)aa, 'N' ReverseCharge,'' ApplicableofTaxRate ,'Reguler' InvoiceType,'' ECommerceGSTIN,TC_InvoiceItems.GSTPercentage Rate,sum(TC_InvoiceItems.BasicAmount) TaxableValue ,'0' CessAmount
        FROM T_Invoices 
        JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
        JOIN M_Parties ON M_Parties.id=T_Invoices.Customer_id
        JOIN M_States ON M_States.id=M_Parties.State_id
        WHERE Party_id=%s and InvoiceDate BETWEEN %s AND %s and M_Parties.GSTIN !=''
        Group by M_Parties.GSTIN,M_Parties.Name,T_Invoices.id,T_Invoices.InvoiceDate,M_States.id,M_States.Name,TC_InvoiceItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
                B2Bdata = B2BSerializer(B2Bquery, many=True).data
                df=pd.DataFrame(B2Bdata)
                # print (df)

                specific_column_names = {
                'GSTIN':'GSTIN/UIN of Recipient', 
                'Name':'Receiver Name',
                'FullInvoiceNumber':'Invoice Number',
                'InvoiceDate':'Invoice date',
                'GrandTotal':'Invoice Value',
                'aa':'Place Of Supply',
                'ReverseCharge':'Reverse Charge',
                'ApplicableofTaxRate':'Applicable %'+'of TaxRate',
                'InvoiceType' :'Invoice Type',
                'ECommerceGSTIN':'E-Commerce GSTIN',
                'Rate':'Rate',
                'TaxableValue' :'Taxable Value',
                'CessAmount':'Cess Amount',
                }
                
                # Define which columns header Font bold
                for col_idx, header in enumerate(df.columns, start=1):
                    
                    cell = ws.cell(row=4, column=col_idx, value=specific_column_names.get(header, header))
                    bold_font = Font(bold=True)
                    cell.font = bold_font
                    

                # Write the data
                for col_idx, header in enumerate(df.columns, start=1):
                    for row_idx, value in enumerate(df[header], start=5):
                        ws.cell(row=row_idx, column=col_idx, value=value)
                    
                max_cols = len(df.columns)

                # Merge cells and add the hardcoded text
                ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_cols)
                merged_cell = ws.cell(row=1, column=1, value="Summary For B2B(4)")
                bold_font = Font(bold=True)
                merged_cell.font = bold_font
                merged_cell.alignment = Alignment(horizontal='center')  # Align text to center
                
                
                B2Bquery2 = T_Invoices.objects.raw('''SELECT 1 as id, count(DISTINCT Customer_id) NoofRecipients,count(*)NoOfInvoices,sum(T_Invoices.GrandTotal+T_Invoices.TCSAmount) TotalInvoiceValue FROM T_Invoices JOIN M_Parties ON M_Parties.id=T_Invoices.Customer_id WHERE T_Invoices.Party_id=%s AND InvoiceDate BETWEEN %s AND %s and M_Parties.GSTIN !='' ''',([Party],[FromDate],[ToDate]))
                B2Bdata2 = B2BSerializer2(B2Bquery2, many=True).data
                B2Bdf2=pd.DataFrame(B2Bdata2)
                # print(B2Bdf2)
                
                specific_column_names = {
                'NoofRecipients':'No.of Recipients', 
                'NoOfInvoices':'No.of Invoices',
                'TotalInvoiceValue':'Total Invoice Value',
                }
                
                for col_idx, header in enumerate(B2Bdf2.columns, start=1):
                    ws.cell(row=2, column=col_idx, value=specific_column_names.get(header, header))
                    bold_font = Font(bold=True)
                    ws.cell(row=2, column=col_idx).font = bold_font

                
                        
                # Example data for the four sheet CDNR        
                CDNRquery = T_CreditDebitNotes.objects.raw('''SELECT T_CreditDebitNotes.id, M_Parties.GSTIN,M_Parties.Name,T_CreditDebitNotes.FullNoteNumber,T_CreditDebitNotes.CRDRNoteDate,(CASE WHEN T_CreditDebitNotes.NoteType_id = 37 THEN 'C' ELSE 'D' END) NoteType,CONCAT(M_States.StateCode, '-', M_States.Name) aa,'N' ReverseCharge,'Regular' NoteSupplyType,(T_CreditDebitNotes.GrandTotal) GrandTotal,'' ApplicableofTaxRate,TC_CreditDebitNoteItems.GSTPercentage Rate,SUM(TC_CreditDebitNoteItems.BasicAmount) TaxableValue,'' CessAmount FROM T_CreditDebitNotes
                JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id = T_CreditDebitNotes.id
                JOIN M_Parties ON M_Parties.id = T_CreditDebitNotes.Customer_id
                JOIN M_States ON M_States.id = M_Parties.State_id 
                WHERE T_CreditDebitNotes.Party_id = %s AND T_CreditDebitNotes.CRDRNoteDate BETWEEN %s AND %s AND M_Parties.GSTIN != '' 
                GROUP BY M_Parties.GSTIN , M_Parties.Name , T_CreditDebitNotes.FullNoteNumber , T_CreditDebitNotes.CRDRNoteDate, T_CreditDebitNotes.NoteType_id , M_States.id , M_States.Name , TC_CreditDebitNoteItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
                CDNRdata = CDNRSerializer(CDNRquery, many=True).data
                df4=pd.DataFrame(CDNRdata)


                ws8 = wb.create_sheet(title="Docs")
                
                specific_column_names = {
                'a':'Nature of Document', 
                'MINID':'Sr. No. From',
                'MAXID':'Sr. No. To',
                'cnt':'Total Number',
                'Cancelledcnt':'Cancelled'
                }
                
                for col_idx, header in enumerate(df8.columns, start=1):
                    cell = ws8.cell(row=2, column=col_idx, value=specific_column_names.get(header, header))
                    bold_font = Font(bold=True)
                    cell.font = bold_font
                
                # Write the data on the second worksheet
                for col_idx, header in enumerate(df8.columns, start=1):
                    for row_idx, value in enumerate(df8[header], start=3):
                        ws8.cell(row=row_idx, column=col_idx, value=value)                
                        
                ws8.merge_cells(start_row=1, start_column=1, end_row=1, end_column=max_cols)
                merged_cell = ws8.cell(row=1, column=1, value="Summary of documents issued during the tax period (13)")
                bold_font = Font(bold=True)
                merged_cell.font = bold_font
                merged_cell.alignment = Alignment(horizontal='center')  # Align text to center        
                        
        #         # Populate worksheet with data
        #         # ws['A1'] = 'Header 1'
        #         # ws['B1'] = 'Header 2'
        #         # ws['A2'] = 'Data 1'
        #         # ws['B2'] = 'Data 2'

                output = io.BytesIO()
                wb.save(output)
                output.seek(0)

                response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=example.xlsx'

                return response
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

