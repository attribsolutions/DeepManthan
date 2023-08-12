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

class ExcelDownloadView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    pass
    

    def post(self, request):
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
            cell = ws.cell(row=1, column=col_idx, value=specific_column_names.get(header, header))
            bold_font = Font(bold=True)
            cell.font = bold_font
            

        # Write the data
        for col_idx, header in enumerate(df.columns, start=1):
            for row_idx, value in enumerate(df[header], start=2):
                ws.cell(row=row_idx, column=col_idx, value=value)


        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(output.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=example.xlsx'

        return response