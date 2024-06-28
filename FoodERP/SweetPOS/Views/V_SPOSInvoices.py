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
                        # CustomPrint(queryforParty)
                        if not queryforParty:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'DivisionId is not mapped. Please map it from the SPOSRoleAccess page.', 'Data':[]})
                        else:
                            # ==========================Get Max Invoice Number=====================================================
                            
                            Invoicedata['TCSAmount']=0.0
                            Invoicedata['InvoiceNumber'] = Invoicedata['BillNumber']
                            Invoicedata['InvoiceDate'] = Invoicedata['SaleDate']
                            Invoicedata['FullInvoiceNumber'] = Invoicedata['BillNumber']
                            Invoicedata['Customer'] = 97
                            Invoicedata['Party'] = Invoicedata['PartyID']
                            Invoicedata['GrandTotal'] =Invoicedata['NetAmount']
                            Invoicedata['RoundOffAmount'] =Invoicedata['NetAmount']
                            Invoicedata['Driver'] = 0
                            Invoicedata['Vehicle'] = 0
                            Invoicedata['NetAmount'] =Invoicedata['NetAmount']
                            Invoicedata['SaleID'] =0
                             
                            
                            #================================================================================================== 
                            InvoiceItems = Invoicedata['SaleItems']
                            
                            for InvoiceItem in InvoiceItems:
                                
                                queryforItem=M_Items.objects.filter(CItemID=InvoiceItem['ERPItemID']).values('id')
                                
                                    
                                if not queryforItem:
                                    ItemId= 33
                                    # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'ERPItemId is not mapped.', 'Data':[]})
                                else:
                                    ItemId=queryforItem[0]['id']
                                
                                if InvoiceItem['UnitID'] == 1:
                                    unit=2
                                else: 
                                    unit=1    
                                    
                                quryforunit=MC_ItemUnits.objects.filter(Item=ItemId,IsDeleted=0,UnitID=unit).values('id')
                                
                                InvoiceItem['Unit'] = quryforunit[0]['id']
                                
                                InvoiceItem['BasicAmount'] = InvoiceItem['Amount']
                                InvoiceItem['InvoiceDate'] = InvoiceItem['SaleDate']
                                InvoiceItem['MRPValue'] = InvoiceItem['Rate']
                                InvoiceItem['TaxType'] = 'GST'
                                InvoiceItem['GSTPercentage'] = InvoiceItem['GSTRate']
                                InvoiceItem['GSTAmount'] = InvoiceItem['GSTAmount']
                                InvoiceItem['DiscountType'] = InvoiceItem['DiscountType']
                                InvoiceItem['Discount'] = InvoiceItem['DiscountValue']
                                InvoiceItem['DiscountAmount'] = InvoiceItem['DiscountAmount']
                                InvoiceItem['CGSTPercentage'] = InvoiceItem['CGSTRate']
                                InvoiceItem['CGST'] = InvoiceItem['CGSTAmount']
                                InvoiceItem['SGSTPercentage'] = InvoiceItem['SGSTRate']
                                InvoiceItem['SGST'] = InvoiceItem['SGSTAmount']
                                InvoiceItem['IGSTPercentage'] = InvoiceItem['IGSTRate']
                                InvoiceItem['Item'] = ItemId
                                InvoiceItem['IGST'] = InvoiceItem['IGSTAmount']
                                InvoiceItem['BatchCode'] = '0'
                                InvoiceItem['POSItemID'] = InvoiceItem['ItemID']
                                InvoiceItem['SaleItemID']=0
                                InvoiceItem['SaleID']=0
                                InvoiceItem['Party']=InvoiceItem['PartyID']
                                BaseUnitQuantity=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,0,0).GetBaseUnitQuantity()
                                InvoiceItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                                QtyInNo=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,1,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInNo'] =  float(QtyInNo)
                                QtyInKg=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,2,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInKg'] =  float(QtyInKg)
                                QtyInBox=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,4,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInBox'] = float(QtyInBox)
                               
                            Invoice_serializer = SPOSInvoiceSerializer(data=Invoicedata)
                            
                            if Invoice_serializer.is_valid():
                                Invoice = Invoice_serializer.save()
                                
                                LastInsertId = Invoice.id
                                LastIDs.append(Invoice.id)
                                log_entry = create_transaction_logNew(request, Invoicedata,Party ,'InvoiceDate:'+Invoicedata['InvoiceDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastInsertId),383,LastInsertId,0,0, Invoicedata['Customer'])
                            else:
                                transaction.set_rollback(True)
                                # CustomPrint(Invoicedata, Party, 'InvoiceSave:'+str(Invoice_serializer.errors),34,0,InvoiceDate,0,Invoicedata['Customer'])
                                # log_entry = create_transaction_logNew(request, Invoicedata, Party, str(Invoice_serializer.errors),34,0,0,0,Invoicedata['Customer'])
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
                            
                    
                return JsonResponse({'status_code': 200, 'Success': True,  'Message': 'Invoice Save Successfully','TransactionID':LastIDs, 'Data':[]})
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, 0, 0,'InvoiceSave:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})
        


class SPOSMaxsaleIDView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    
    @transaction.atomic()
    def get(self, request,DivisionID,ClientID):
        try:
            with transaction.atomic():
                
                user=BasicAuthenticationfunction(request)
                    
                if user is not None: 
                    
                    QueryfordivisionID = M_SweetPOSRoleAccess.objects.filter(Party=DivisionID).values('Party')
                    if not QueryfordivisionID:
                            
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'DivisionId is not mapped. Please map it from the SPOSRoleAccess page.', 'Data':[]})
                    else:
                        
                        QueryForMaxSalesID=T_SPOSInvoices.objects.raw('''SELECT 1 id,ifnull(max(SaleID),0) MaxSaleID FROM SweetPOS.T_SPOSInvoices where Party=%s and clientID=%s''', [QueryfordivisionID[0]['Party'] ,ClientID])
                        for row in QueryForMaxSalesID:
                            maxSaleID=row.MaxSaleID

                        log_entry = create_transaction_logNew(request, 0, QueryfordivisionID[0]['Party'],'',384,0,0,0,ClientID)
                        return JsonResponse({"Success":True,"status_code":200,"SaleID":maxSaleID,"Toprows":100})    
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, 0, 0,'GET_Max_SweetPOS_SaleID_By_ClientID:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})            