from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Views.V_CommFunction import *
from ..Serializer.S_R1_Reports import *
from django.db.models import Sum
from ..models import *
from django.http import HttpResponse

import io



from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font,Alignment
import pandas as pd

class ExcelDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    def post(self, request):
        Orderdata = JSONParser().parse(request)
        FromDate = Orderdata['FromDate']
        ToDate = Orderdata['ToDate']
        Party = Orderdata['Party']
        
        # Create a new workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'B2B'
        query = T_Invoices.objects.raw('''SELECT T_Invoices.id, M_Parties.GSTIN , M_Parties.Name,T_Invoices.FullInvoiceNumber,T_Invoices.InvoiceDate,(T_Invoices.GrandTotal+T_Invoices.TCSAmount)GrandTotal,
concat(M_States.StateCode,'-',M_States.Name)aa, 'N' ReverseCharge,'' ApplicableofTaxRate ,'Reguler' InvoiceType,'' ECommerceGSTIN,TC_InvoiceItems.GSTPercentage Rate,sum(TC_InvoiceItems.BasicAmount) TaxableValue ,'0' CessAmount
FROM T_Invoices 
JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
JOIN M_Parties ON M_Parties.id=T_Invoices.Customer_id
JOIN M_States ON M_States.id=M_Parties.State_id
WHERE Party_id=%s and InvoiceDate BETWEEN %s AND %s and M_Parties.GSTIN !=''
Group by M_Parties.GSTIN,M_Parties.Name,T_Invoices.id,T_Invoices.InvoiceDate,M_States.id,M_States.Name,TC_InvoiceItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
        orderdata = B2BSerializer(query, many=True).data
        df=pd.DataFrame(orderdata)
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
            cell = ws.cell(row=1, column=col_idx, value=specific_column_names.get(header, header))
            bold_font = Font(bold=True)
            cell.font = bold_font
            

        # Write the data
        for col_idx, header in enumerate(df.columns, start=1):
            for row_idx, value in enumerate(df[header], start=2):
                ws.cell(row=row_idx, column=col_idx, value=value)
                # if isinstance(value, DecimalField):
                # cell.alignment = Alignment(horizontal='right')
                
        

        # Example data for the second sheet B2CL
        B2CLquery = T_Invoices.objects.raw('''SELECT T_Invoices.id,T_Invoices.FullInvoiceNumber,T_Invoices.InvoiceDate,(T_Invoices.GrandTotal)GrandTotal,concat(M_States.StateCode,'-',M_States.Name)aa, '' ApplicableofTaxRate ,TC_InvoiceItems.GSTPercentage Rate,sum(TC_InvoiceItems.BasicAmount) TaxableValue ,'0' CessAmount,'' ECommerceGSTIN
FROM T_Invoices 
JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
JOIN M_Parties a ON a.id=T_Invoices.Party_id
JOIN M_Parties b ON b.id=T_Invoices.Customer_id
JOIN M_States ON M_States.id=b.State_id
where Party_id=%s and InvoiceDate BETWEEN %s AND %s and b.GSTIN !='' and b.State_id != a.State_id and T_Invoices.GrandTotal > 250000
group by T_Invoices.id,T_Invoices.InvoiceDate,M_States.id,M_States.Name, TC_InvoiceItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
        B2CLdata = B2CLSerializer(B2CLquery, many=True).data
        df2=pd.DataFrame(B2CLdata)

        ws2 = wb.create_sheet(title="B2CL")
        
        specific_column_names = {
        'FullInvoiceNumber':'Invoice Number',
        'InvoiceDate':'Invoice date',
        'GrandTotal':'Invoice Value',
        'aa':'Place Of Supply',
        'ApplicableofTaxRate':'Applicable %'+'of TaxRate',
        'ECommerceGSTIN':'E-Commerce GSTIN',
        'Rate':'Rate',
        'TaxableValue' :'Taxable Value',
        'CessAmount':'Cess Amount',
        }
        
        for col_idx, header in enumerate(df2.columns, start=1):
            cell = ws2.cell(row=1, column=col_idx, value=specific_column_names.get(header, header))
            bold_font = Font(bold=True)
            cell.font = bold_font
        
        # Write the data on the second worksheet
        for col_idx, header in enumerate(df2.columns, start=1):
            for row_idx, value in enumerate(df2[header], start=2):
                ws2.cell(row=row_idx, column=col_idx, value=value)
                
                
                
        B2CSquery = T_Invoices.objects.raw('''SELECT T_Invoices.id, 'OE' Type,concat(M_States.StateCode,'-',M_States.Name)aa, '' ApplicableofTaxRate ,TC_InvoiceItems.GSTPercentage Rate,sum(TC_InvoiceItems.BasicAmount) TaxableValue ,'0' CessAmount,'' ECommerceGSTIN
from T_Invoices 
JOIN TC_InvoiceItems ON TC_InvoiceItems.Invoice_id=T_Invoices.id
JOIN M_Parties a ON a.id=T_Invoices.Party_id
JOIN M_Parties b ON b.id=T_Invoices.Customer_id
JOIN M_States ON M_States.id=b.State_id
where Party_id=%s and InvoiceDate BETWEEN %s AND %s and  b.GSTIN =''
 and ((a.State_id = b.State_id) OR (a.State_id != b.State_id and T_Invoices.GrandTotal <= 250000))
 group  by M_States.id,M_States.Name,TC_InvoiceItems.GSTPercentage''',([Party],[FromDate],[ToDate]))
        B2CSdata = B2CSSerializer(B2CSquery, many=True).data
        df3=pd.DataFrame(B2CSdata)

        ws3 = wb.create_sheet(title="B2CS")
        
        specific_column_names = {
        'Type':'Type',
        'aa':'Place Of Supply',
        'ApplicableofTaxRate':'Applicable %'+'of TaxRate',
        'ECommerceGSTIN':'E-Commerce GSTIN',
        'Rate':'Rate',
        'TaxableValue' :'Taxable Value',
        'CessAmount':'Cess Amount',
        }
        
        for col_idx, header in enumerate(df3.columns, start=1):
            cell = ws3.cell(row=1, column=col_idx, value=specific_column_names.get(header, header))
            bold_font = Font(bold=True)
            cell.font = bold_font
        
        # Write the data on the second worksheet
        for col_idx, header in enumerate(df3.columns, start=1):
            for row_idx, value in enumerate(df3[header], start=2):
                ws3.cell(row=row_idx, column=col_idx, value=value)        
                
                
                
                
                
        # Populate worksheet with data
        # ws['A1'] = 'Header 1'
        # ws['B1'] = 'Header 2'
        # ws['A2'] = 'Data 1'
        # ws['B2'] = 'Data 2'

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=example.xlsx'

        return response


