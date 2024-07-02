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
        mulInvoicedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                LastIDs=[]
                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                    
                    for Invoicedata in mulInvoicedata:                        
                        Party = Invoicedata['DivisionID']
                        queryforParty=M_SweetPOSRoleAccess.objects.using('sweetpos_db').filter(Party=Invoicedata['DivisionID']).values('Party')
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
                            Invoicedata['Party'] = queryforParty[0]['Party']
                            Invoicedata['GrandTotal'] =Invoicedata['NetAmount']
                            Invoicedata['RoundOffAmount'] =Invoicedata['NetAmount']
                            Invoicedata['Driver'] = 0
                            Invoicedata['Vehicle'] = 0
                            Invoicedata['NetAmount'] =Invoicedata['NetAmount']
                            Invoicedata['SaleID'] =0
                             
                            
                            #================================================================================================== 
                            InvoiceItems = Invoicedata['SaleItems']
                            
                            for InvoiceItem in InvoiceItems:
                                
                                queryforItem=M_Items.objects.filter(id=InvoiceItem['ERPItemID']).values('id')
                                
                                    
                                if not queryforItem:
                                    ItemId= 0
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'ERPItemId is not mapped.', 'Data':[]})
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
                                
                            else:
                                transaction.set_rollback(True)
                                # CustomPrint(Invoicedata, Party, 'InvoiceSave:'+str(Invoice_serializer.errors),34,0,InvoiceDate,0,Invoicedata['Customer'])
                                # log_entry = create_transaction_logNew(request, Invoicedata, Party, str(Invoice_serializer.errors),34,0,0,0,Invoicedata['Customer'])
                                return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
                            
                log_entry = create_transaction_logNew(request, mulInvoicedata,Party ,'InvoiceDate:'+Invoicedata['InvoiceDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastIDs),383,0,0,0, 0)    
                return JsonResponse({'status_code': 200, 'Success': True,  'Message': 'Invoice Save Successfully','TransactionID':LastIDs, 'Data':[]})
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, mulInvoicedata, 0,'InvoiceSave:'+str(Exception(e)),33,0)
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
                        
                        QueryForMaxSalesID=T_SPOSInvoices.objects.raw('''SELECT 1 id,ifnull(max(ClientSaleID),0) MaxSaleID FROM SweetPOS.T_SPOSInvoices where Party=%s and clientID=%s''', [QueryfordivisionID[0]['Party'] ,ClientID])
                        for row in QueryForMaxSalesID:
                            maxSaleID=row.MaxSaleID

                        log_entry = create_transaction_logNew(request, 0, QueryfordivisionID[0]['Party'],'',384,0,0,0,ClientID)
                        return JsonResponse({"Success":True,"status_code":200,"SaleID":maxSaleID,"Toprows":100})    
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, 0, 0,'GET_Max_SweetPOS_SaleID_By_ClientID:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})            
        


class SPOSInvoiceViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, id=0,characters=None):
        try:
            
            with transaction.atomic():
                if characters:
                    if characters == "P":
                        A = "InvoicePrint"
                        B = 50

                    else:
                        A = "InvoiceEdit"
                        B = 351
                else:
                    A = "Action is not defined"
                # CustomPrint(characters)
                # CustomPrint(id)
                InvoiceQuery = T_SPOSInvoices.objects.raw(f'''SELECT SPOSInv.id,InvoiceDate,InvoiceNumber,FullInvoiceNumber,TCSAmount,GrandTotal,RoundOffAmount,Customer,
                                                          cust.Name CustomerName,cust.GSTIN CustomerGSTIN,cust.MobileNo CustomerMobileNo,
Party,party.Name PartyName,party.GSTIN PartyGSTIN,party.MobileNo PartyMobileNo,M_Drivers.Name DriverName,M_Vehicles.VehicleNumber,SPOSInv.CreatedOn,
custaddr.FSSAINo CustomerFSSAI ,custaddr.Address CustomerAddress,
partyaddr.FSSAINo PartyFSSAI,partyaddr.Address PartyAddress,MC_PartyBanks.BranchName,MC_PartyBanks.IFSC,MC_PartyBanks.AccountNo,M_Bank.Name BankName,MC_PartyBanks.IsDefault,custstate.Name CustState,partystate.Name PartyState
,IU.AckNo, IU.Irn, IU.QRCodeUrl, IU.EInvoicePdf, IU.EwayBillNo, IU.EwayBillUrl, IU.EInvoiceCreatedBy, IU.EInvoiceCreatedOn, IU.EwayBillCreatedBy, IU.EwayBillCreatedOn, IU.EInvoiceCanceledBy, IU.EInvoiceCanceledOn, IU.EwayBillCanceledBy, IU.EwayBillCanceledOn, 
IU.EInvoiceIsCancel, IU.EwayBillIsCancel
FROM SweetPOS.T_SPOSInvoices SPOSInv
join FoodERP.M_Parties cust on cust.id=SPOSInv.Customer
join FoodERP.M_Parties party on party.id=SPOSInv.Party 
left join FoodERP.M_Drivers on M_Drivers.Party_id=SPOSInv.Party
left join FoodERP.M_Vehicles on M_Vehicles.Party_id=SPOSInv.Party
left join FoodERP.MC_PartyAddress partyaddr  on partyaddr.Party_id=SPOSInv.Party and partyaddr.IsDefault=1
left join FoodERP.MC_PartyAddress custaddr on custaddr.Party_id=SPOSInv.Customer and custaddr.IsDefault=1
left join FoodERP.MC_PartyBanks on MC_PartyBanks.Party_id=SPOSInv.Party and MC_PartyBanks.IsSelfDepositoryBank=1 and MC_PartyBanks.IsDefault=1
left join FoodERP.M_Bank on M_Bank.id=MC_PartyBanks.Bank_id
left join FoodERP.M_States custstate on custstate.id=cust.State_id
left join FoodERP.M_States partystate on partystate.id=party.State_id
left join FoodERP.TC_InvoiceUploads IU on IU.Invoice_id=SPOSInv.id                                                          
                                                          

where SPOSInv.id={id}''')
                # print(InvoiceQuery.query)
                if InvoiceQuery:
                    # InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceQuery:
            
                        InvoiceItemDetails = list()
                        InvoiceItemQuery=TC_SPOSInvoiceItems.objects.raw(f'''SELECT items.id,items.Name,SPOSInv.Quantity,0 MRP,SPOSInv.MRPValue,SPOSInv.Rate,SPOSInv.TaxType,SPOSInv.BaseUnitQuantity,0 GST,SPOSInv.GSTPercentage,0 MarginValue,
SPOSInv.BasicAmount,SPOSInv.GSTAmount,SPOSInv.CGST,SPOSInv.SGST,SPOSInv.IGST,SPOSInv.CGSTPercentage,SPOSInv.SGSTPercentage,SPOSInv.IGSTPercentage,SPOSInv.Amount,
'' BatchCode,'' BatchDate,SPOSInv.HSNCode,SPOSInv.DiscountType,SPOSInv.Discount,SPOSInv.DiscountAmount,SPOSInv.Unit,unit.Name UnitName


FROM SweetPOS.TC_SPOSInvoiceItems SPOSInv 
join FoodERP.M_Items items on items.id=SPOSInv.Item
join FoodERP.MC_ItemUnits itemunit on itemunit.id=SPOSInv.Unit
join FoodERP.M_Units unit on unit.id=itemunit.UnitID_id

WHERE SPOSInv.Invoice_id = {a.id}''')
                        # print(InvoiceItemQuery.query)
                        for b in InvoiceItemQuery:
                            aaaa=UnitwiseQuantityConversion(b.id,b.Quantity,b.Unit,0,0,0,0).GetConvertingBaseUnitQtyBaseUnitName()
                            print(aaaa)
                            if (aaaa == b.UnitName):
                                bb=""
                            else:
                                bb=aaaa   
                                
                            InvoiceItemDetails.append({
                                "Item": b.id,
                                "ItemName": b.Name,
                                "Quantity": b.Quantity,
                                "MRP": b.MRP,
                                "MRPValue": b.MRPValue,
                                "Rate": b.Rate,
                                "TaxType": b.TaxType,
                                "PrimaryUnitName":b.UnitName,
                                "UnitName":bb,
                                "BaseUnitQuantity": b.BaseUnitQuantity,
                                "GST": b.GST,
                                "GSTPercentage": b.GSTPercentage,
                                "MarginValue": b.MarginValue,
                                "BasicAmount": b.BasicAmount,
                                "GSTAmount": b.GSTAmount,
                                "CGST": b.CGST,
                                "SGST": b.SGST,
                                "IGST": b.IGST,
                                "CGSTPercentage": b.CGSTPercentage,
                                "SGSTPercentage": b.SGSTPercentage,
                                "IGSTPercentage": b.IGSTPercentage,
                                "Amount": b.Amount,
                                "BatchCode": b.BatchCode,
                                "BatchDate": b.BatchDate,
                                "HSNCode":b.HSNCode,
                                "DiscountType":b.DiscountType,
                                "Discount":b.Discount,
                                "DiscountAmount":b.DiscountAmount
                            })
                            
                        InvoiceReferenceDetails = list()
                        
                        InvoiceReferenceDetails.append({
                            # "Invoice": d['Invoice'],
                            "Order": 0,
                            "FullOrderNumber": 0,
                            "Description":''
                        })
    
                            
                            
                        # DefCustomerAddress = ''  
                        # for ad in a.Customer']['PartyAddress']:
                        #     if ad['IsDefault'] == True :
                        #         DefCustomerAddress = ad['Address']
                        #         DefCustomerFSSAI = ad['FSSAINo']
                        # for x in a.Party']['PartyAddress']:
                        #     if x['IsDefault'] == True :
                        #         DefPartyAddress = x['Address']
                        #         DefPartyFSSAI = x['FSSAINo']

                        # code by ankita 
                        # DefCustomerRoute = ''
                        # for bb in a.Customer']['MCSubParty']:
                        #     # if bb['IsDefault'] == True:
                        #         DefCustomerRoute = bb['Route']['Name']
                        
                        
                        # query= MC_PartyBanks.objects.filter(Party=a.Party']['id'],IsSelfDepositoryBank=1,IsDefault=1).all()
                        # BanksSerializer= PartyBanksSerializer(query, many=True).data
                        BankData=list()
                        # for e in BanksSerializer:
                        #     if e['IsDefault'] == 1:
                        BankData.append({
                            "BankName": a.BankName,
                            "BranchName": a.BranchName,
                            "IFSC": a.IFSC,
                            "AccountNo": a.AccountNo,
                            "IsDefault" : a.IsDefault
                        })

                        
                        InvoiceUploads=list()
                        if a.AckNo :
                            InvoiceUploads.append({
                                "AckNo" : a.AckNo,
                                "Irn": a.Irn,
                                "QRCodeUrl" : a.QRCodeUrl,
                                "EInvoicePdf" :a.EInvoicePdf,
                                "EwayBillNo" : a.EwayBillNo,
                                "EwayBillUrl" : a.EwayBillUrl,
                                "EInvoiceCreatedBy" : a.EInvoiceCreatedBy,
                                "EInvoiceCreatedOn" : a.EInvoiceCreatedOn ,
                                "EwayBillCreatedBy" :a.EwayBillCreatedBy,
                                "EwayBillCreatedOn" : a.EwayBillCreatedOn,
                                "EInvoiceCanceledBy" : a.EInvoiceCanceledBy,
                                "EInvoiceCanceledOn" : a.EInvoiceCanceledOn,
                                "EwayBillCanceledBy" : a.EwayBillCanceledBy,
                                "EwayBillCanceledOn" : a.EwayBillCanceledOn,
                                "EInvoiceIsCancel" : a.EInvoiceIsCancel,
                                "EwayBillIsCancel" :a.EwayBillIsCancel

                            })
                            
                        InvoiceData.append({
                            "id": a.id,
                            "InvoiceDate": a.InvoiceDate,
                            "InvoiceNumber": a.InvoiceNumber,
                            "FullInvoiceNumber": a.FullInvoiceNumber,
                            "TCSAmount" : a.TCSAmount, 
                            "GrandTotal": a.GrandTotal,
                            "RoundOffAmount":a.RoundOffAmount,
                            "Customer": a.Customer,
                            "CustomerName": a.CustomerName,
                            "CustomerGSTIN": a.CustomerGSTIN,
                            "CustomerMobileNo": a.CustomerMobileNo,
                            "Party": a.Party,
                            "PartyName": a.PartyName,
                            "PartyGSTIN": a.PartyGSTIN,
                            "PartyMobileNo": a.PartyMobileNo,
                            "PartyFSSAINo": a.PartyFSSAI,
                            "CustomerFSSAINo": a.CustomerFSSAI,
                            "PartyState": a.PartyState,
                            "CustomerState": a.CustState,
                            "PartyAddress": a.PartyAddress,                            
                            "CustomerAddress": a.CustomerAddress,
                            # "CustomerRoute":DefCustomerRoute,
                            "DriverName":a.DriverName,
                            "VehicleNo": a.VehicleNumber,
                            "CreatedOn" : a.CreatedOn,
                            "InvoiceItems": InvoiceItemDetails,
                            "InvoicesReferences": InvoiceReferenceDetails,
                            "InvoiceUploads" : InvoiceUploads,
                            "BankData":BankData
                                                        
                        })
                    # log_entry = create_transaction_logNew(request, {'InvoiceID':id}, a.Party']['id'], A+','+"InvoiceID:"+str(id),int(B),0,0,0,a.Customer']['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                # log_entry = create_transaction_logNew(request, {'InvoiceID':id}, a.Party']['id'], "Invoice Not available",int(B),0,0,0,a.Customer']['id'])
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Invoice Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'SingleInvoice:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        