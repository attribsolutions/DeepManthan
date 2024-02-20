from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from rest_framework.parsers import JSONParser

from FoodERP.FoodERPApp.Views.V_CommFunction import UnitwiseQuantityConversion, create_transaction_logNew
from FoodERP.SweetPOS.Serializer.S_SPOSInvoices import SPOSInvoiceSerializer

from ..models import  *

class SPOSInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                mulInvoicedata = JSONParser().parse(request)
                LastIDs=[]
                for Invoicedata in mulInvoicedata['InvoiceData']:
                    Party = Invoicedata['Party']
                    InvoiceDate = Invoicedata['InvoiceDate']
                
                    # ==========================Get Max Invoice Number=====================================================
                    
                    Invoicedata['InvoiceNumber'] = Invoicedata['BillNumber']
                    Invoicedata['InvoiceDate'] = Invoicedata['SaleDate']
                    Invoicedata['FullInvoiceNumber'] = Invoicedata['BillNumber']
                    Invoicedata['Customer'] = 97
                    Invoicedata['Party'] = Invoicedata['DivisionID']
                    Invoicedata['GrandTotal'] =Invoicedata['NetAmount']
                    Invoicedata['RoundOffAmount'] =Invoicedata['NetAmount']
                    #================================================================================================== 
                    InvoiceItems = Invoicedata['SaleItems']
                    
                    for InvoiceItem in InvoiceItems:
                        # print(InvoiceItem['Quantity'])
                        InvoiceItem['Unit'] = InvoiceItem['UnitID']
                        InvoiceItem['GSTPercentage'] = InvoiceItem['GST']
                        InvoiceItem['BasicAmount'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = 0
                        InvoiceItem['MRPValue'] = InvoiceItem['Rate']
                        InvoiceItem['TaxType'] = 'GST'
                        InvoiceItem['GSTAmount'] = 0
                        InvoiceItem['DiscountType'] = 2
                        InvoiceItem['Discount'] = 0
                        InvoiceItem['DiscountAmount'] = 0
                        InvoiceItem['CGSTPercentage'] = InvoiceItem['CGSTRate']
                        InvoiceItem['SGSTPercentage'] = InvoiceItem['SGSTRate']
                        InvoiceItem['IGSTPercentage'] = InvoiceItem['IGSTRate']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                        InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']

                        
                        
                        BaseUnitQuantity=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,0,0).GetBaseUnitQuantity()
                        InvoiceItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                        QtyInNo=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                        InvoiceItem['QtyInNo'] =  float(QtyInNo)
                        QtyInKg=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                        InvoiceItem['QtyInKg'] =  float(QtyInKg)
                        QtyInBox=UnitwiseQuantityConversion(InvoiceItem['Item'],InvoiceItem['Quantity'],InvoiceItem['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                        InvoiceItem['QtyInBox'] = float(QtyInBox)
                        
                        
                    Invoice_serializer = SPOSInvoiceSerializer(data=Invoicedata)
                    
                    if Invoice_serializer.is_valid():
                        Invoice = Invoice_serializer.save()
                        LastInsertId = Invoice.id
                        LastIDs.append(Invoice.id)
                        log_entry = create_transaction_logNew(request, Invoicedata,Party ,'InvoiceDate:'+Invoicedata['InvoiceDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastInsertId),4,LastInsertId,0,0, Invoicedata['Customer'])
                    else:
                        transaction.set_rollback(True)
                        # print(Invoicedata, Party, 'InvoiceSave:'+str(Invoice_serializer.errors),34,0,InvoiceDate,0,Invoicedata['Customer'])
                        # log_entry = create_transaction_logNew(request, Invoicedata, Party, str(Invoice_serializer.errors),34,0,0,0,Invoicedata['Customer'])
                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
                        
                
            return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Save Successfully','TransactionID':LastIDs, 'Data':[]})
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, 0, 0,'InvoiceSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})