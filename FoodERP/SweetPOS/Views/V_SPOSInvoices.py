from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated

from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication

from FoodERPApp.Views.V_CommFunction import UnitwiseQuantityConversion, create_transaction_logNew
from FoodERPApp.models import *
from SweetPOS.Serializer.S_SPOSInvoices import SPOSInvoiceSerializer

from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction

from ..models import  *

class SPOSInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                mulInvoicedata = JSONParser().parse(request)
                LastIDs=[]
                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                    
                    for Invoicedata in mulInvoicedata:
                       
                        Party = Invoicedata['DivisionID']
                        queryforParty=M_SweetPOSRoleAccess.objects.using('sweetpos_db').filter(DivisionID=Invoicedata['DivisionID']).values('Party')
                        print(queryforParty)
                        if not queryforParty:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'DivisionId is not mapped. Please map it from the SPOSRoleAccess page.', 'Data':[]})
                        else:
                            # ==========================Get Max Invoice Number=====================================================
                            
                            Invoicedata['TCSAmount']=0.0
                            Invoicedata['InvoiceNumber'] = Invoicedata['BillNumber']
                            Invoicedata['InvoiceDate'] = Invoicedata['SaleDate']
                            Invoicedata['FullInvoiceNumber'] = Invoicedata['BillNumber']
                            Invoicedata['Customer'] = 97
                            Invoicedata['Party'] = queryforParty[0]['Party']
                            Invoicedata['GrandTotal'] =Invoicedata['NetAmount']
                            Invoicedata['RoundOffAmount'] =Invoicedata['NetAmount']
                            Invoicedata['Driver'] = 0
                            Invoicedata['Vehicle'] = 0

                            
                            #================================================================================================== 
                            InvoiceItems = Invoicedata['SaleItems']
                            
                            for InvoiceItem in InvoiceItems:
                                queryforItem=M_Items.objects.filter(CItemID=InvoiceItem['ERPItemID']).values('id')
                                if InvoiceItem['UnitID'] == 1:
                                    unit=2
                                else: 
                                    unit=1    
                                # print(queryforItem,unit,'7//7/77777777/')
                                quryforunit=MC_ItemUnits.objects.filter(Item=queryforItem[0]['id'],IsDeleted=0,UnitID=unit).values('id')
                                # printf(quryforunit.query)
                                
                                
                                # print(InvoiceItem['Quantity'])
                                InvoiceItem['Unit'] = quryforunit[0]['id']
                                InvoiceItem['GSTPercentage'] = InvoiceItem['GST']
                                InvoiceItem['BasicAmount'] = InvoiceItem['Amount']
                            
                                InvoiceItem['MRPValue'] = InvoiceItem['Rate']
                                InvoiceItem['TaxType'] = 'GST'
                                InvoiceItem['GSTAmount'] = 0
                                InvoiceItem['DiscountType'] = 2
                                InvoiceItem['Discount'] = 0
                                InvoiceItem['DiscountAmount'] = 0
                                InvoiceItem['CGSTPercentage'] = InvoiceItem['CGSTRate']
                                InvoiceItem['SGSTPercentage'] = InvoiceItem['SGSTRate']
                                InvoiceItem['IGSTPercentage'] = InvoiceItem['IGSTRate']
                                InvoiceItem['Item'] = queryforItem[0]['id']
                                InvoiceItem['IGST'] = InvoiceItem['IGSTRate']
                                InvoiceItem['BatchCode'] = '0'
                                InvoiceItem['POSItemID'] = InvoiceItem['ItemID']
                                # InvoiceItem['Invoice'] = 1
                                # InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                                # InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                                # InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                                # InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                                # InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']
                                # InvoiceItem['BaseUnitQuantity'] = InvoiceItem['Amount']

                                
                                
                                BaseUnitQuantity=UnitwiseQuantityConversion(queryforItem[0]['id'],InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,0,0).GetBaseUnitQuantity()
                                InvoiceItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                                QtyInNo=UnitwiseQuantityConversion(queryforItem[0]['id'],InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,1,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInNo'] =  float(QtyInNo)
                                QtyInKg=UnitwiseQuantityConversion(queryforItem[0]['id'],InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,2,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInKg'] =  float(QtyInKg)
                                QtyInBox=UnitwiseQuantityConversion(queryforItem[0]['id'],InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,4,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInBox'] = float(QtyInBox)
                            print('==========================================================================')    
                            # print(Invoicedata)    
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