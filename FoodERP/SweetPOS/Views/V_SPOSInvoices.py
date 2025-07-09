from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
import base64
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from django.contrib.auth import authenticate
from FoodERPApp.Views.V_CommFunction import *
from FoodERPApp.models import *
from SweetPOS.Serializer.S_SPOSInvoices import *
# from SweetPOS.Serializer.S_SPOSInvoices import SaleItemSerializer
from rest_framework import status
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction
from FoodERPApp.models import  *
from django.db.models import *
from datetime import timedelta
from SweetPOS.Views.SweetPOSCommonFunction import *
from FoodERPApp.Views.V_TransactionNumberfun import *
from django.db.models import Min, Max



class SPOSInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        mulInvoicedata = JSONParser().parse(request)
        inputdata = mulInvoicedata
        try:
            with transaction.atomic():
                
                LastIDs=[]
                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                    
                    for Invoicedata in mulInvoicedata:                      
                        Party = Invoicedata['DivisionID']
                        SaleDate = Invoicedata['SaleDate']
                        ClientID = Invoicedata['ClientID']
                      
                        # queryforParty=M_SweetPOSRoleAccess.objects.using('sweetpos_db').filter(Party=Invoicedata['DivisionID']).values('Party')
                        # CustomPrint(queryforParty)
                        # queryforParty=1
                        # if not queryforParty:
                        #     return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'DivisionId is not mapped. Please map it from the SPOSRoleAccess page.', 'Data':[]})
                        # else:
                        
                        # ==========================Get Max Invoice Number=====================================================
                        
                        if  'FullInvoiceNumber' in Invoicedata:
                            pass
                        else:    
                            a = GetInvoiceDetails.GetPOSInvoiceNumber(Party,SaleDate,ClientID)
                            b = GetInvoiceDetails.GetPOSInvoicePrifix(Party)
                            
                        #================================================================================================== 
                        
                        Invoicedata['TCSAmount']=0.0
                        if 'FullInvoiceNumber' in Invoicedata:
                            Invoicedata['InvoiceNumber'] = Invoicedata['BillNumber']
                            Invoicedata['FullInvoiceNumber'] = Invoicedata['FullInvoiceNumber']
                        else:   
                            Invoicedata['FullInvoiceNumber'] = b+""+str(a)
                            Invoicedata['InvoiceNumber'] = a
                        
                        Invoicedata['InvoiceDate'] = Invoicedata['SaleDate']
                        Invoicedata['Party'] = Invoicedata['DivisionID']
                        Invoicedata['GrandTotal'] =Invoicedata['RoundedAmount']
                        Invoicedata['RoundOffAmount'] =Invoicedata['RoundOffAmount']
                        Invoicedata['Driver'] = 0
                        Invoicedata['SaleID'] =0
                        Invoicedata['MobileNo'] =Invoicedata['Mobile']
                                            
                        if Invoicedata['CustomerID'] == 0:
                            Invoicedata['Customer'] = 43194
                        else:
                            Invoicedata['Customer'] = Invoicedata['CustomerID']
                        customer = M_Parties.objects.filter(id=Invoicedata['Customer']).values('GSTIN').first()
                        Invoicedata['CustomerGSTIN'] = customer['GSTIN'] if customer else None

                            
                        if 'Vehicle' in Invoicedata and Invoicedata['Vehicle'] == "":
                            Invoicedata['Vehicle'] = None
                        else:
                            Invoicedata['Vehicle'] = Invoicedata.get('Vehicle', None)
                            
                        if 'AdvanceAmount' in Invoicedata and Invoicedata['AdvanceAmount'] == "":
                            Invoicedata['AdvanceAmount'] = None
                        else:
                            Invoicedata['AdvanceAmount'] = Invoicedata.get('AdvanceAmount', None) 
                        #================================================================================================== 
                        InvoiceItems = Invoicedata['SaleItems']
                        
                        
                        for InvoiceItem in InvoiceItems:
                            
                            # queryforItem=M_Items.objects.filter(id=InvoiceItem['ERPItemID']).values('id')
                            # queryforItem=1
                                
                            # if not queryforItem:
                            #     ItemId= 0
                            #     return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'ERPItemId is not mapped.', 'Data':[]})
                            # else:
                            ItemId=InvoiceItem['ERPItemID']
                            unit= int(InvoiceItem['UnitID'])
                            # if InvoiceItem['UnitID'] == 1:
                            #     unit=2
                            # else: 
                            #     unit=1 
                            
                            quryforunit=MC_ItemUnits.objects.filter(Item=ItemId,IsDeleted=0,UnitID=unit).values('id')
                            
                            InvoiceItem['Unit'] = quryforunit[0]['id']
                            
                            queryformobile = M_ConsumerMobile.objects.filter(Mobile=Invoicedata['MobileNo'],MacID=Invoicedata.get('MacID', None) )
                            if queryformobile:
                                M_ConsumerMobile.objects.filter(Mobile=Invoicedata['MobileNo'],MacID=Invoicedata['MacID']).update(IsLinkToBill=1)
                            
                            # InvoiceItem['BasicAmount'] = InvoiceItem['Amount']
                            InvoiceItem['InvoiceDate'] = InvoiceItem['SaleDate']
                            InvoiceItem['MRPValue'] = InvoiceItem['MRP']
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
                            InvoiceItem['HSNCode']=InvoiceItem['HSNCode']
                            InvoiceItem['Party']=InvoiceItem['PartyID']
                            InvoiceItem['IsMixItem'] = InvoiceItem.get('IsMixItem') or 0  
                            InvoiceItem['MixItemId'] = InvoiceItem.get('MixItemId', None) 
                            BaseUnitQuantity=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,0,0).GetBaseUnitQuantity()
                            InvoiceItem['BaseUnitQuantity'] = BaseUnitQuantity
                            QtyInNo=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,1,0).ConvertintoSelectedUnit()
                            InvoiceItem['QtyInNo'] =  float(QtyInNo)
                            QtyInKg=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,2,0).ConvertintoSelectedUnit()
                            InvoiceItem['QtyInKg'] = float(QtyInKg)
                            QtyInBox=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,4,0).ConvertintoSelectedUnit()
                            InvoiceItem['QtyInBox'] = float(QtyInBox)
                            
                        if 'SPOSInvoicesReferences' in Invoicedata:
                            Invoice_serializer = SPOSInvoiceSerializer1(data=Invoicedata)
                        else:
                            
                            Invoice_serializer = SPOSInvoiceSerializer(data=Invoicedata)
                            
                        # if Invoicedata['SPOSInvoicesReferences']['Order']:
                        #     ReferenceData = Invoicedata['SPOSInvoicesReferences']['Order']                            
                        # else:
                        #     ReferenceData=0
                        
                        # print(ReferenceData)
                        if Invoice_serializer.is_valid():
                            Invoice = Invoice_serializer.save()
                            
                            LastInsertId = Invoice.id
                            LastIDs.append(Invoice.id)
                            
                            
                            
                          # Process VoucherCodes as list of objects if present
                            if 'AppliedSchemes' in Invoicedata and Invoicedata['AppliedSchemes']:
                                for voucher_entry in Invoicedata['AppliedSchemes']:
                                    voucher_code = (voucher_entry.get('VoucherCode') or '').strip()
                                    scheme_id = voucher_entry.get('SchemeID', 'NULL')

                                    if voucher_code and voucher_code != 'SSCCBM2025':
                                        voucher_obj = M_GiftVoucherCode.objects.filter(VoucherCode=voucher_code).first()
                                        if voucher_obj and voucher_obj.IsActive == 1:
                                            voucher_obj.IsActive = 0
                                            voucher_obj.InvoiceDate = Invoicedata.get('InvoiceDate')
                                            voucher_obj.InvoiceNumber = Invoicedata.get('InvoiceNumber')
                                            voucher_obj.InvoiceAmount = Invoicedata.get('GrandTotal')
                                            voucher_obj.Party = Invoicedata.get('Party')
                                            voucher_obj.client = Invoicedata.get('ClientID')   
                                            voucher_obj.ClientSaleID = Invoicedata.get('ClientSaleID')
                                            voucher_obj.save()

                                    VoucherQuery = f"""
                                        INSERT INTO SweetPOS.TC_InvoicesSchemes (Invoice_id, scheme, VoucherCode)
                                        VALUES ({LastInsertId}, {scheme_id}, {'NULL' if not voucher_code else f"'{voucher_code}'"})
                                    """
                                    connection.cursor().execute(VoucherQuery)

                            # Process VoucherCode string (comma-separated) + SchemeIDs string (comma-separated)
                            elif 'VoucherCode' in Invoicedata and Invoicedata['VoucherCode']:
                                VoucherCodes = (Invoicedata.get('VoucherCode') or '').split(",")
                                SchemeIDs = (Invoicedata.get('SchemeID') or '').split(",") if Invoicedata.get('SchemeID') else []

                                for idx, code in enumerate(VoucherCodes):
                                    code = code.strip()
                                    if code == 'SSCCBM2025':
                                        continue

                                    voucher_obj = M_GiftVoucherCode.objects.filter(VoucherCode=code).first()
                                    if voucher_obj and voucher_obj.IsActive == 1:
                                        voucher_obj.IsActive = 0
                                        voucher_obj.InvoiceDate = Invoicedata.get('InvoiceDate')
                                        voucher_obj.InvoiceNumber = Invoicedata.get('InvoiceNumber')
                                        voucher_obj.InvoiceAmount = Invoicedata.get('GrandTotal')
                                        voucher_obj.Party = Invoicedata.get('Party')
                                        voucher_obj.client = Invoicedata.get('ClientID')
                                        voucher_obj.ClientSaleID = Invoicedata.get('ClientSaleID')
                                        voucher_obj.save()

                                    # Pick scheme ID if available for this position, else NULL
                                    scheme_id = SchemeIDs[idx] if idx < len(SchemeIDs) else 'NULL'

                                    VoucherQuery = f"""
                                        INSERT INTO SweetPOS.TC_InvoicesSchemes (Invoice_id, scheme, VoucherCode)
                                        VALUES ({LastInsertId}, {scheme_id}, {'NULL' if not code else f"'{code}'"})
                                    """
                                    connection.cursor().execute(VoucherQuery)
                               

                            # If only SchemeID provided without VoucherCode
                            elif 'SchemeID' in Invoicedata and Invoicedata['SchemeID']:
                                SchemeIDs = Invoicedata['SchemeID'].split(",")
                                for scheme_id in SchemeIDs:
                                    VoucherQuery = f"""
                                        INSERT INTO SweetPOS.TC_InvoicesSchemes (Invoice_id, scheme, VoucherCode)
                                        VALUES ({LastInsertId}, {scheme_id}, NULL)
                                    """
                                    connection.cursor().execute(VoucherQuery)

                        else:
                            log_entry = create_transaction_logNew(request, inputdata, Party, str(Invoice_serializer.errors),34,0,0,0,0)
                            transaction.set_rollback(True)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
                           
                log_entry = create_transaction_logNew(request, inputdata,Party ,'InvoiceDate:'+Invoicedata['InvoiceDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastIDs),383,0,0,0, 0)    
                return JsonResponse({'status_code': 200, 'Success': True,  'Message': 'Invoice Save Successfully','TransactionID':LastIDs,'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, inputdata, 0,'InvoiceSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
        


class SPOSMaxsaleIDView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    
    @transaction.atomic()
    def get(self, request,DivisionID,ClientID):
        try:
            with transaction.atomic():
                
                user=BasicAuthenticationfunction(request)
                    
                if user is not None: 
                    
                    # QueryfordivisionID = M_SweetPOSRoleAccess.objects.filter(Party=DivisionID).values('Party')
                    QueryforSaleRecordCount = M_SweetPOSMachine.objects.filter(Party=DivisionID ,id=ClientID).values('UploadSaleRecordCount')
                
                    if not QueryforSaleRecordCount:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'SweetPOSMachine is not mapped', 'Data':[]})
                    if QueryforSaleRecordCount[0]['UploadSaleRecordCount'] == 0:
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Sale data upload is not allowed at the moment', 'Data': []})
                    else:
                        QueryForMaxSalesID=T_SPOSInvoices.objects.raw('''SELECT 1 id,ifnull(max(ClientSaleID),0) MaxSaleID FROM SweetPOS.T_SPOSInvoices where Party=%s and clientID=%s''', [DivisionID ,ClientID])
                        for row in QueryForMaxSalesID:
                            maxSaleID=row.MaxSaleID

                        log_entry = create_transaction_logNew(request, 0, DivisionID,{'SaleID':maxSaleID},384,0,0,0,ClientID)
                        return JsonResponse({"Success":True,"status_code":200,"SaleID":maxSaleID,"Toprows":QueryforSaleRecordCount[0]['UploadSaleRecordCount']})    
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GET_Max_SweetPOS_SaleID_By_ClientID:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})            
        


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
                InvoiceQuery = T_SPOSInvoices.objects.raw(f'''SELECT SPOSInv.id,InvoiceDate,InvoiceNumber,FullInvoiceNumber,AdvanceAmount,TCSAmount,GrandTotal,RoundOffAmount,Customer,
                                                          cust.Name CustomerName,cust.GSTIN CustomerGSTIN,cust.MobileNo CustomerMobileNo,
Party,party.Name PartyName,party.GSTIN PartyGSTIN,party.MobileNo PartyMobileNo,M_Drivers.Name DriverName,M_Vehicles.VehicleNumber,
SPOSInv.CreatedOn,custaddr.FSSAINo CustomerFSSAI ,custaddr.Address CustomerAddress, partyaddr.FSSAINo PartyFSSAI,
partyaddr.Address PartyAddress,MC_PartyBanks.BranchName,MC_PartyBanks.IFSC,MC_PartyBanks.AccountNo,M_Bank.Name BankName,MC_PartyBanks.IsDefault,custstate.Name CustState,partystate.Name PartyState,
SPOSIU.AckNo, SPOSIU.Irn, SPOSIU.QRCodeUrl, SPOSIU.EInvoicePdf, SPOSIU.EwayBillNo, SPOSIU.EwayBillUrl, SPOSIU.EInvoiceCreatedBy, SPOSIU.EInvoiceCreatedOn, SPOSIU.EwayBillCreatedBy,
SPOSIU.EwayBillCreatedOn, SPOSIU.EInvoiceCanceledBy, SPOSIU.EInvoiceCanceledOn, SPOSIU.EwayBillCanceledBy, SPOSIU.EwayBillCanceledOn, 
SPOSIU.EInvoiceIsCancel, SPOSIU.EwayBillIsCancel,c.name as CompanyName,u.LoginName as CashierName,party.AlternateContactNo
FROM SweetPOS.T_SPOSInvoices SPOSInv
join FoodERP.M_Parties cust on cust.id=SPOSInv.Customer
join FoodERP.M_Parties party on party.id=SPOSInv.Party 
left join FoodERP.M_Drivers on M_Drivers.id=SPOSInv.Driver
left join FoodERP.M_Vehicles on M_Vehicles.id=SPOSInv.Vehicle
left join FoodERP.MC_PartyAddress partyaddr  on partyaddr.Party_id=SPOSInv.Party and partyaddr.IsDefault=1
left join FoodERP.MC_PartyAddress custaddr on custaddr.Party_id=SPOSInv.Customer and custaddr.IsDefault=1
left join FoodERP.MC_PartyBanks on MC_PartyBanks.Party_id=SPOSInv.Party and MC_PartyBanks.IsSelfDepositoryBank=1 and MC_PartyBanks.IsDefault=1
left join FoodERP.M_Bank on M_Bank.id=MC_PartyBanks.Bank_id
left join FoodERP.M_States custstate on custstate.id=cust.State_id
left join FoodERP.M_States partystate on partystate.id=party.State_id
left JOIN SweetPOS.TC_SPOSInvoiceUploads SPOSIU  ON SPOSIU.Invoice_id = SPOSInv.id    
left join FoodERP.C_Companies c on party.Company_id=c.id  
left join FoodERP.M_Users u on SPOSInv.CreatedBy=u.id                                                      
where SPOSInv.id={id}''') 
                if InvoiceQuery:
                    # InvoiceSerializedata = InvoiceSerializerSecond(InvoiceQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceSerializedata})
                    InvoiceData = list()
                    for a in InvoiceQuery:
            
                        InvoiceItemDetails = list()
                        InvoiceItemQuery=TC_SPOSInvoiceItems.objects.raw(f'''SELECT items.id,items.Name,SPOSInv.Quantity,0 MRP,SPOSInv.MRPValue,SPOSInv.Rate,SPOSInv.TaxType,SPOSInv.BaseUnitQuantity,0 GST,SPOSInv.GSTPercentage,0 MarginValue,
SPOSInv.BasicAmount,SPOSInv.GSTAmount,SPOSInv.CGST,SPOSInv.SGST,SPOSInv.IGST,SPOSInv.CGSTPercentage,SPOSInv.SGSTPercentage,SPOSInv.IGSTPercentage,SPOSInv.Amount,
'' BatchCode,'' BatchDate,SPOSInv.HSNCode,SPOSInv.DiscountType,SPOSInv.Discount,SPOSInv.DiscountAmount,SPOSInv.Unit,unit.Name UnitName,
SPOSInv.IsMixItem, SPOSInv.MixItemId
FROM SweetPOS.TC_SPOSInvoiceItems SPOSInv 
join FoodERP.M_Items items on items.id=SPOSInv.Item
join FoodERP.MC_ItemUnits itemunit on itemunit.id=SPOSInv.Unit
join FoodERP.M_Units unit on unit.id=itemunit.UnitID_id
WHERE SPOSInv.Invoice_id = {a.id}''')
                        # print(InvoiceItemQuery.query)
                        for b in InvoiceItemQuery:
                            aaaa=UnitwiseQuantityConversion(b.id,b.Quantity,b.Unit,0,0,0,0).GetConvertingBaseUnitQtyBaseUnitName()
                            
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
                                "DiscountAmount":b.DiscountAmount,
                                "IsMixItem" : b.IsMixItem,
                                "MixItemId" : b.MixItemId
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
                        if (a.AckNo or a.EwayBillNo):
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
                            # Add Company Name, CashierName, AlternateContactNo
                            "CompanyName":a.CompanyName,
                            "CashierName" :a.CashierName,
                            "AlternateContactNo":a.AlternateContactNo,
                            "AdvanceAmount" : a.AdvanceAmount,
                            # End Add Extra Fields
                            "InvoiceItems": InvoiceItemDetails,
                            "InvoicesReferences": InvoiceReferenceDetails,
                            "InvoiceUploads" : InvoiceUploads,
                            "BankData":BankData
                                                        
                        }) 
                        
                    log_entry = create_transaction_logNew(request,0, a.Party, A+','+"InvoiceID:"+str(id),int(B),0,0,0,a.Customer)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceData[0]})
                log_entry = create_transaction_logNew(request,0, a.Party, "Invoice Not available",int(B),0,0,0,a.Customer)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Invoice Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'SingleInvoice:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})        


class UpdateCustomerVehiclePOSInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        CustomerVehicledata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                VehicleUpdate = T_SPOSInvoices.objects.using('sweetpos_db').filter(id=CustomerVehicledata['InvoiceID']).update(Vehicle=CustomerVehicledata['vehicle'],Customer=CustomerVehicledata['Customer'])
            
                Get_Invoice = T_SPOSInvoices.objects.using('sweetpos_db').get(id=CustomerVehicledata['InvoiceID'])
                Get_PartyID = M_Parties.objects.using('default').filter(id=Get_Invoice.Party).first()  
                Get_CustomerID = M_Parties.objects.using('default').filter(id=Get_Invoice.Customer).first()
                Party_GSTIN = Get_PartyID.GSTIN if Get_PartyID and Get_PartyID.GSTIN else ''
                Customer_GSTIN = Get_CustomerID.GSTIN if Get_CustomerID and Get_CustomerID.GSTIN else ''
                Party_StateCode = str(Party_GSTIN)[:2] if Party_GSTIN else ''
                Customer_StateCode = str(Customer_GSTIN)[:2] if Customer_GSTIN else ''
                
                if (not Party_GSTIN and not Customer_GSTIN):
                    same_state = True
                elif (Party_GSTIN and not Customer_GSTIN) or (not Party_GSTIN and Customer_GSTIN):
                    same_state = True
                elif (Party_GSTIN and Customer_GSTIN and Party_StateCode == Customer_StateCode):
                    same_state = True
                else:
                    same_state = False

                items = TC_SPOSInvoiceItems.objects.using('sweetpos_db').filter(Invoice_id=CustomerVehicledata['InvoiceID'])

                for item in items:
                    gst_amount = item.GSTAmount or 0
                    gst_percentage = item.GSTPercentage or 0 

                    if same_state:
                        if Get_PartyID and Get_PartyID.IsSEZ:
                            item.CGST = 0
                            item.SGST = 0
                            item.CGSTPercentage = 0
                            item.SGSTPercentage = 0
                            item.IGST = gst_amount
                            item.IGSTPercentage = gst_percentage
                        else:
                            item.CGST = round(gst_amount / 2, 2)
                            item.SGST = round(gst_amount / 2, 2)
                            item.CGSTPercentage = round(gst_percentage / 2, 2)
                            item.SGSTPercentage = round(gst_percentage / 2, 2)
                            item.IGST = 0
                            item.IGSTPercentage = 0
                    else:
                        item.CGST = 0
                        item.SGST = 0
                        item.CGSTPercentage = 0
                        item.SGSTPercentage = 0
                        item.IGST = gst_amount
                        item.IGSTPercentage = gst_percentage
                    item.save(using='sweetpos_db')

                log_entry = create_transaction_logNew(request, CustomerVehicledata, 0, {'POSInvoiceID': CustomerVehicledata['InvoiceID']}, 67, 0)
                return JsonResponse({'StatusCode': 200,'Status': True,'Message': 'Customer, Vehicle Number updated and GST adjusted successfully.','Data': []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, CustomerVehicledata, 0, 'UpdateCustomerVehiclePOSInvoice: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400,'Status': True,'Message': str(e),'Data': []})

        
class DeleteInvoiceView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    def post(self, request):
        DeleteInvoicedatas = JSONParser().parse(request)
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                    
                if user is not None:
                
                    InvoiceIDs=list()
                    for DeleteInvoicedata in DeleteInvoicedatas:
                        InvoiceDeleteUpdate = T_SPOSInvoices.objects.using('sweetpos_db').filter(ClientID=DeleteInvoicedata['ClientID'],ClientSaleID=DeleteInvoicedata['ClientSaleID'],Party=DeleteInvoicedata['PartyID'],InvoiceDate=DeleteInvoicedata['InvoiceDate']).values('id', 'VoucherCode')
                        
                        if not InvoiceDeleteUpdate:
                            continue  
                        
                        if InvoiceDeleteUpdate[0]['VoucherCode']:
                            queryforvouchercode = M_GiftVoucherCode.objects.filter(VoucherCode=InvoiceDeleteUpdate[0]['VoucherCode']).update(InvoiceDate=None,InvoiceNumber=None,InvoiceAmount=None,Party=0,client=0,IsActive=1)
                        
                        if DeleteInvoicedata['UpdatedInvoiceDetails'] :
                            
                            invoice_instance = T_SPOSInvoices.objects.get(id=InvoiceDeleteUpdate[0]['id'])
                            InvoiceItems = DeleteInvoicedata['UpdatedInvoiceDetails'][0]['SaleItems']
                            AdvanceAmountValue = DeleteInvoicedata['UpdatedInvoiceDetails'][0].get('AdvanceAmount', 0)
                            InvoiceUpdate=T_SPOSInvoices.objects.filter(id=InvoiceDeleteUpdate[0]['id']).update(GrandTotal=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['RoundedAmount'],DiscountAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0] ['DiscountAmount'],TotalAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['TotalAmount'], RoundOffAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['RoundOffAmount'], NetAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['NetAmount'], AdvanceAmount=AdvanceAmountValue, UpdatedBy=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['UpdatedBy'])
                            DeleteItemsData=TC_SPOSInvoiceItems.objects.filter(Invoice=InvoiceDeleteUpdate[0]['id']).delete()

                            # return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'ERPItemId is not mapped.', 'Data':InvoiceItems})
                            for InvoiceItem in InvoiceItems:
                                ItemId=InvoiceItem['ERPItemID']
                                unit= int(InvoiceItem['UnitID'])
                               
                                quryforunit=MC_ItemUnits.objects.filter(Item=ItemId,IsDeleted=0,UnitID=unit).values('id')
                                
                                InvoiceItem['Unit'] = quryforunit[0]['id']
                                
                                # InvoiceItem['InvoiceDate'] = InvoiceItem['SaleDate']
                                InvoiceItem['InvoiceDate'] = InvoiceItem['SaleDate']
                                InvoiceItem['MRPValue'] = InvoiceItem['MRP']
                                InvoiceItem['TaxType'] = 'GST'
                                InvoiceItem['GSTPercentage'] = InvoiceItem['GSTRate']
                                # InvoiceItem['GSTAmount'] = InvoiceItem['GSTAmount']
                                # InvoiceItem['DiscountType'] = InvoiceItem['DiscountType']
                                InvoiceItem['Discount'] = InvoiceItem['DiscountValue']
                                # InvoiceItem['DiscountAmount'] = InvoiceItem['DiscountAmount']
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
                                InvoiceItem['IsMixItem']=InvoiceItem.get('IsMixItem') or 0
                                # InvoiceItem['HSNCode']=InvoiceItem['HSNCode']
                                InvoiceItem['Party']=InvoiceItem['PartyID']
                                BaseUnitQuantity=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,0,0).GetBaseUnitQuantity()
                                InvoiceItem['BaseUnitQuantity'] =  float(BaseUnitQuantity)
                                QtyInNo=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,1,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInNo'] =  float(QtyInNo)
                                QtyInKg=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,2,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInKg'] = float(QtyInKg)
                                QtyInBox=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,4,0).ConvertintoSelectedUnit()
                                InvoiceItem['QtyInBox'] = float(QtyInBox)
                                InvoiceItem['Invoice'] = invoice_instance
                                del InvoiceItem['SaleDate'] ,InvoiceItem['PartyID'],InvoiceItem['ItemID'],InvoiceItem['ItemName']
                                del InvoiceItem['UnitID'] ,InvoiceItem['DiscountValue'] ,InvoiceItem['MRP'] ,InvoiceItem['GSTRate']
                                del InvoiceItem['CGSTRate'],InvoiceItem['CGSTAmount'],InvoiceItem['SGSTRate'],InvoiceItem['SGSTAmount']
                                del InvoiceItem['IGSTRate'],InvoiceItem['IGSTAmount'],InvoiceItem['SaleID'],
                               
                                InvoiceItemID =TC_SPOSInvoiceItems.objects.create(**InvoiceItem)
                                InvoiceItemID.save()    
                            ss=T_SPOSDeletedInvoices(DeletedTableAutoID=DeleteInvoicedata['DeletedTableAutoID'], ClientID=DeleteInvoicedata['ClientID'], ClientSaleID=DeleteInvoicedata['ClientSaleID'], InvoiceDate=DeleteInvoicedata['InvoiceDate'], Party=DeleteInvoicedata['PartyID'], DeletedBy=DeleteInvoicedata['DeletedBy'], DeletedOn=DeleteInvoicedata['DeletedOn'], ReferenceInvoiceID=DeleteInvoicedata['ReferenceInvoiceID'],Invoice_id=InvoiceDeleteUpdate[0]['id'])
                            ss.save()
                        else:
                            
                            # InvoiceDeleteUpdate = T_SPOSInvoices.objects.using('sweetpos_db').filter(ClientID=DeleteInvoicedata['ClientID'],ClientSaleID=DeleteInvoicedata['ClientSaleID'],Party=DeleteInvoicedata['PartyID'],InvoiceDate=DeleteInvoicedata['InvoiceDate']).values('id')
                            InvoiceDeleteUpdate.update(IsDeleted=1)
                            ss=T_SPOSDeletedInvoices(DeletedTableAutoID=DeleteInvoicedata['DeletedTableAutoID'], ClientID=DeleteInvoicedata['ClientID'], ClientSaleID=DeleteInvoicedata['ClientSaleID'], InvoiceDate=DeleteInvoicedata['InvoiceDate'], Party=DeleteInvoicedata['PartyID'], DeletedBy=DeleteInvoicedata['DeletedBy'], DeletedOn=DeleteInvoicedata['DeletedOn'], ReferenceInvoiceID=DeleteInvoicedata['ReferenceInvoiceID'],Invoice_id=InvoiceDeleteUpdate[0]['id'])
                            ss.save()
                        
                        InvoiceIDs.append(DeleteInvoicedata['ClientSaleID'])
                    log_entry = create_transaction_logNew(request,DeleteInvoicedatas,0, {'DeletedInvoiceID':InvoiceIDs}, 388,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'Invoice Delete Successfully ', 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, DeleteInvoicedatas, 0,'UpdateInvoiceDeleteFlag:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})             
        

class SPOSMaxDeletedInvoiceIDView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    
    @transaction.atomic()
    def get(self, request,DivisionID,ClientID):
        try:
            with transaction.atomic():
                
                user=BasicAuthenticationfunction(request)
                    
                if user is not None: 
                    QueryforSaleRecordCount = M_SweetPOSMachine.objects.filter(Party=DivisionID ,id=ClientID).values('UploadSaleRecordCount')
                    if not QueryforSaleRecordCount:
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'SweetPOSMachine is not mapped', 'Data':[]})
                    if QueryforSaleRecordCount[0]['UploadSaleRecordCount'] == 0:
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Sale data upload is not allowed at the moment', 'Data': []})
                    else:
                        QueryForMaxSalesID=T_SPOSDeletedInvoices.objects.raw('''SELECT 1 id,ifnull(max(DeletedTableAutoID),0) MaxSaleID 
                                                                            FROM SweetPOS.T_SPOSDeletedInvoices 
                                                                            where Party=%s and clientID=%s''', [DivisionID ,ClientID])
                        for row in QueryForMaxSalesID:
                            maxSaleID=row.MaxSaleID

                        log_entry = create_transaction_logNew(request, 0, DivisionID,'DeletedInvoiceID:'+str(maxSaleID),389,0,0,0,ClientID)
                        return JsonResponse({"Success":True,"status_code":200,"DeletedInvoiceID":maxSaleID,"Toprows":200})    
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, 0, DivisionID,'DeletedInvoiceID:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})      



class TopSaleItemsOfFranchiseView(CreateAPIView):
    permission_classes = ()
    authentication_classes = [BasicAuthentication]
 
    @transaction.atomic()
    def post(self, request):
        SaleData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = SaleData['FromDate']
                ToDate = SaleData['ToDate']
                Party = SaleData['Party']
 
                PartyDetails = M_Parties.objects.raw('''SELECT FoodERP.M_Parties.id, Name, FoodERP.MC_PartyAddress.Address,
                                                        (SELECT SUM(SweetPOS.T_SPOSInvoices.GrandTotal) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party= %s AND SweetPOS.T_SPOSInvoices.IsDeleted=0) TotalAmount,
                                                        (SELECT COUNT(id) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party= %s AND SweetPOS.T_SPOSInvoices.IsDeleted=0) BillCount,
                                                        (SELECT TIME(MIN(SweetPOS.T_SPOSInvoices.CreatedOn)) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s) FirstBillTime,
                                                        (SELECT TIME(MAX(SweetPOS.T_SPOSInvoices.CreatedOn)) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s) LastBillTime,
                                                        (SELECT FullInvoiceNumber FROM SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s ORDER BY id DESC LIMIT 1) LastInvoiceNumber,
                                                        (SELECT GrandTotal FROM SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s AND SweetPOS.T_SPOSInvoices.IsDeleted=0 ORDER BY id DESC LIMIT 1) LastInvoiceAmount
                                                        From FoodERP.M_Parties
                                                        JOIN FoodERP.MC_PartyAddress ON FoodERP.M_Parties.id = FoodERP.MC_PartyAddress.Party_id AND FoodERP.MC_PartyAddress.IsDefault = True
                                                        Where FoodERP.M_Parties.id= %s
                                                        GROUP BY FoodERP.M_Parties.id,Name,FoodERP.MC_PartyAddress.Address''', ([FromDate, ToDate, Party, FromDate, ToDate, Party, FromDate, ToDate, Party, FromDate, ToDate, Party, FromDate, ToDate, Party,FromDate, ToDate, Party, Party]))
                Party_List = []
                for party in PartyDetails:
                    TopSaleItems = TC_SPOSInvoiceItems.objects.raw('''SELECT 1 as id,SweetPOS.TC_SPOSInvoiceItems.Item, FoodERP.M_Items.Name AS ItemName,
                                                                    SUM(SweetPOS.TC_SPOSInvoiceItems.Amount) AS TotalAmount,
                                                                    SUM(SweetPOS.TC_SPOSInvoiceItems.Quantity) AS TotalQuantity,
                                                                    FoodERP.M_Units.Name AS UnitName
                                                                    FROM SweetPOS.TC_SPOSInvoiceItems                                                                  
                                                                    JOIN SweetPOS.T_SPOSInvoices  ON SweetPOS.TC_SPOSInvoiceItems.Invoice_id = SweetPOS.T_SPOSInvoices.id
                                                                    JOIN FoodERP.M_Items ON SweetPOS.TC_SPOSInvoiceItems.Item = FoodERP.M_Items.id
                                                                    JOIN FoodERP.MC_ItemUnits ON SweetPOS.TC_SPOSInvoiceItems.Unit = FoodERP.MC_ItemUnits.id
                                                                    JOIN FoodERP.M_Units ON FoodERP.MC_ItemUnits.UnitID_id = FoodERP.M_Units.id
                                                                    WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party= %s AND SweetPOS.T_SPOSInvoices.IsDeleted=0
                                                                    GROUP BY SweetPOS.TC_SPOSInvoiceItems.Item, M_Items.Name, M_Units.Name
                                                                    ORDER BY TotalAmount DESC, TotalQuantity DESC LIMIT 5''', ([FromDate, ToDate, Party]))
                    TopSaleItems_List = []
                    for item in TopSaleItems:
                        TopSaleItems_List.append({
                            "Item": item.Item,
                            "ItemName": item.ItemName,
                            "TotalAmount": item.TotalAmount,
                            "TotalQuantity": item.TotalQuantity,
                            "UnitName": item.UnitName
                        })

                    InvoiceValues = T_SPOSInvoices.objects.filter(InvoiceDate__range=[FromDate, ToDate],Party=Party,IsDeleted=0).aggregate(MinInvoiceValue=Min('GrandTotal'), MaxInvoiceValue=Max('GrandTotal'))

                    MinInvoiceValue = InvoiceValues['MinInvoiceValue'] or 0
                    MaxInvoiceValue = InvoiceValues['MaxInvoiceValue'] or 0

                    UPTData = TC_SPOSInvoiceItems.objects.raw('''SELECT 1 as id, AVG(ItemCount) as UnitPerTransaction FROM (SELECT COUNT(*) as ItemCount FROM SweetPOS.T_SPOSInvoices A JOIN SweetPOS.TC_SPOSInvoiceItems B ON A.id = B.Invoice_id WHERE A.InvoiceDate BETWEEN %s AND %s  AND A.Party = %s AND A.IsDeleted = 0 AND A.GrandTotal >= %s AND A.GrandTotal <= %s GROUP BY A.id) AS ItemCounts''', [FromDate, ToDate, Party, MinInvoiceValue, MaxInvoiceValue])
                    
                    UnitPerTransaction = 0
                    for upt in UPTData:
                        UnitPerTransaction = upt.UnitPerTransaction or 0
                        
                    ATVData = T_SPOSInvoices.objects.raw('''SELECT 1 as id, AVG(GrandTotal) as AvgTransactionValue FROM SweetPOS.T_SPOSInvoices WHERE InvoiceDate BETWEEN %s AND %s AND Party = %s AND IsDeleted = 0 AND GrandTotal >= %s AND GrandTotal <= %s''', [FromDate, ToDate, Party, MinInvoiceValue, MaxInvoiceValue])

                    AverageTransactionValue = 0
                    for atv in ATVData:
                        AverageTransactionValue = atv.AvgTransactionValue or 0
                        
                    Party_List.append({
                        "PartyId": party.id,
                        "PartyName": party.Name,
                        "PartyAddress": party.Address,
                        "BillCount": party.BillCount,
                        "TotalAmount": party.TotalAmount,
                        "FirstBillTime": party.FirstBillTime,
                        "LastBillTime": party.LastBillTime,
                        "LastInvoiceNumber": party.LastInvoiceNumber,
                        "LastInvoiceAmount": party.LastInvoiceAmount,
                        "UnitPerTransaction": round(UnitPerTransaction, 2),
                        "AverageTransactionValue": round(AverageTransactionValue, 2),
                        "TopSaleItems": TopSaleItems_List
                    })
                if Party_List:
                    log_entry = create_transaction_logNew( request,{"RequestData": SaleData, "TopSaleItems": str(Party_List)},0, 'TopSaleItems-> Details Available In TransactionLogDetails',390,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Party_List})
                else:
                    log_entry = create_transaction_logNew(request, SaleData, Party, 'Record Not Found', 390, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
                    log_entry = create_transaction_logNew(request, SaleData, 0, 'TopSaleItems:' + str(e), 33, 0)
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
        
class MobileNumberSaveView(CreateAPIView):
    permission_classes = ()
    authentication_classes = [BasicAuthentication]
    
    @transaction.atomic()
    def post(self, request):
        Mobile_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Mobile_serializer = MobileSerializer(data=Mobile_Data)
                if Mobile_serializer.is_valid():
                    Mobile = Mobile_serializer.save()
                    LastInsertID = Mobile.id
                    log_entry = create_transaction_logNew(request, Mobile_Data, 0, '', 411, LastInsertID)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Mobile Save Successfully','TransactionID':LastInsertID, 'Data':[]})
                else:
                    log_entry = create_transaction_logNew(request, Mobile_Data, 0, 'ConsumerMobileSave:'+str(Mobile_serializer.errors), 34, 0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Mobile_serializer.errors, 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Mobile_Data, 0, 'ConsumerMobileSave:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
        
class ConsumerMobileListView(CreateAPIView):
    permission_classes = ()
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def post(self, request,MacID=0):
        MobileData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                MacID = MobileData['MacID']
                Party = MobileData['Party']
                query = M_ConsumerMobile.objects.raw('''SELECT id, Mobile, IsLinkToBill, MacID, Party, CreatedOn
                                            FROM SweetPOS.M_ConsumerMobile 
                                            WHERE IsLinkToBill = 0 
                                            AND MacID = %s 
                                            AND Party = %s
                                            AND CreatedOn between NOW() - INTERVAL 5 MINUTE and Now()
                                            ORDER BY id DESC''',[MacID,Party])
                MobileDataList = list()
                for a in query:
                    MobileDataList.append({
                        "id": a.id,
                        "Mobile": a.Mobile,
                        "IsLinkToBill": a.IsLinkToBill,
                        "MacID": a.MacID,
                        "Party": a.Party,
                        "CreatedOn": a.CreatedOn
                    })
                if MobileDataList:
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': MobileDataList})
                else:
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mobile Number not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]})
        

class MobileNumberUpdateView(CreateAPIView):
    permission_classes = ()
    authentication_classes = [BasicAuthentication]

    @transaction.atomic()
    def put(self, request,id=0):
        Mobile_Data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                MobileByID = M_ConsumerMobile.objects.get(id=id)
                Mobile_Serializer = MobileSerializer(
                    MobileByID, data=Mobile_Data)
                if Mobile_Serializer.is_valid():
                    Mobile_Serializer.save()
                    log_entry = create_transaction_logNew(request, Mobile_Data, 0, '', 413, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Mobile Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, Mobile_Data, 0, 'Consumer Mobile Update:'+str(Mobile_Serializer.errors), 412, 0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Mobile_Serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Mobile_Data, 0, 'Consumer Mobile Update:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})  
        
        
class FranchiseSaleWithBillCountView(CreateAPIView):
 
    permission_classes = (IsAuthenticated,)
 
    @transaction.atomic()
    def post(self, request):
        DailySale = JSONParser().parse(request)
        try:
            with transaction.atomic():
                EmployeeID = DailySale['EmployeeID']
                FromDate = DailySale['FromDate']
                ToDate = DailySale['ToDate']
 
                query = T_SPOSInvoices.objects.raw('''SELECT M_Parties.id, Name, Count(*) Bills, SUM(GrandTotal) GrandTotal,
                                                   T_SPOSInvoices.ClientID, MAX(T_SPOSInvoices.CreatedOn) AS LastBillTime
                                                    FROM SweetPOS.T_SPOSInvoices
                                                    left JOIN FoodERP.M_Parties on Party = M_Parties.id
                                                    WHERE InvoiceDate BETWEEN %s AND %s
                                                    AND Party IN (select Party_id from FoodERP.MC_ManagementParties WHERE Employee_id = %s)
                                                    Group By M_Parties.id, M_Parties.Name,T_SPOSInvoices.ClientID
                                                    Order By GrandTotal Desc''',[FromDate,ToDate,EmployeeID]) 
            
                DailySaleDataDict = {}
                for a in query:
                    party_id = a.id
                    if party_id not in DailySaleDataDict:
                        DailySaleDataDict[party_id] = {
                            "id": a.id,
                            "Name": a.Name,
                            "BillDetails": []
                        }

                    DailySaleDataDict[party_id]["BillDetails"].append({
                        "ClientID": a.ClientID,
                        "Bills": a.Bills,
                        "GrandTotal": a.GrandTotal,
                        "LastBillTime": a.LastBillTime
                    })
                    # Convert to list for JSON response
                DailySaleDataList = list(DailySaleDataDict.values())

                if DailySaleDataList:
                    log_entry = create_transaction_logNew(request, DailySale, 0, 'FranchiseSaleWithBillCount', 428, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': DailySaleDataList})
                else:
                    log_entry = create_transaction_logNew(request, DailySale, 0, 'FranchiseSaleWithBillCount Not Found', 428, 0)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'FranchiseSaleWithBillCount Not Available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, DailySale, 0, 'FranchiseSaleWithBillCount:' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]}) 


 
 
class FranchiseInvoiceDeleteView(CreateAPIView):
 
    permission_classes = (IsAuthenticated,)       
    @transaction.atomic()
    def delete(self, request, id=0):
            try:
                with transaction.atomic():
                    Invoice_data = T_SPOSInvoices.objects.get(id=id)
                    Invoice_data.delete()
                    # log_entry = create_transaction_logNew(request, 0,0,'InvoiceID:'+str(id),0,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Invoice Data Deleted Successfully','Data':[]})
            except T_SPOSInvoices.DoesNotExist:
                # log_entry = create_transaction_logNew(request, 0,0,'Invoice Data Not available',338,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Invoice_data Not available', 'Data': []})
            except IntegrityError: 
                # log_entry = create_transaction_logNew(request, 0,0,'Invoice_data used in another table',8,0)      
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Invoice_data used in another table', 'Data': []})
            except Exception as e:
                log_entry = create_transaction_logNew(request, 0,0,'InvoiceDeleted:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})


class FranchiseInvoiceEditView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query1 = TC_SPOSInvoicesReferences.objects.filter(Invoice=id).values('Order')
              
                Orderdata = list()
                query = T_SPOSInvoices.objects.filter(id=id).values('Customer','InvoiceDate','Vehicle','AdvanceAmount','CreatedBy')
                Customer=query[0]['Customer']
                InvoiceDate=query[0]['InvoiceDate']
                Vehicle=query[0]['Vehicle']
                AdvanceAmount = query[0].get('AdvanceAmount', 0)
                CreatedBy = query[0].get('CreatedBy', 0)
                
                Itemsquery= TC_SPOSInvoiceItems.objects.raw('''SELECT SweetPOS.TC_SPOSInvoiceItems.id,SweetPOS.TC_SPOSInvoiceItems.Item,FoodERP.M_Items.Name ItemName,M_Items.BaseUnitID_id MIUnitID,
                                                        SweetPOS.TC_SPOSInvoiceItems.Quantity,SweetPOS.TC_SPOSInvoiceItems.MRPValue,
                                                        SweetPOS.TC_SPOSInvoiceItems.Rate,SweetPOS.TC_SPOSInvoiceItems.Unit, FoodERP.MC_ItemUnits.BaseUnitConversion UnitName,
                                                        FoodERP.MC_ItemUnits.UnitID_id MCUnitsUnitID, FoodERP.MC_ItemUnits.BaseUnitQuantity ConversionUnit,
                                                        SweetPOS.TC_SPOSInvoiceItems.BaseUnitQuantity,SweetPOS.TC_SPOSInvoiceItems.HSNCode,
                                                        SweetPOS.TC_SPOSInvoiceItems.GSTPercentage,SweetPOS.TC_SPOSInvoiceItems.BasicAmount,SweetPOS.TC_SPOSInvoiceItems.GSTAmount,CGST,
                                                        SGST, IGST, CGSTPercentage,SGSTPercentage, IGSTPercentage,Amount,DiscountType,Discount,
                                                        DiscountAmount
                                                        FROM SweetPOS.TC_SPOSInvoiceItems
                                                        JOIN FoodERP.M_Items ON M_Items.id = SweetPOS.TC_SPOSInvoiceItems.Item
                                                        JOIN FoodERP.MC_ItemUnits ON MC_ItemUnits.id = SweetPOS.TC_SPOSInvoiceItems.Unit
                                                        Where SweetPOS.TC_SPOSInvoiceItems.Invoice_id=%s ''',([id]))
                if Itemsquery:
                    InvoiceEditSerializer = SPOSInvoiceEditItemSerializer(Itemsquery, many=True).data
                    
                    OrderItemDetails = []
                    for b in InvoiceEditSerializer:
                        ItemID = b['Item']
                        Unit = b['MIUnitID']
                        BaseUnitQuantity = b['BaseUnitQuantity']
                        GST = b['GSTPercentage']
                      
                     
                        ratemrpquery = M_Items.objects.raw(f''' SELECT 1 AS id, 
                                                    FoodERP.RateCalculationFunction1(0, {ItemID}, {Customer}, {Unit}, 0, 0, 0, 0) AS Rate,
                                                    FoodERP.GetTodaysDateMRP({ItemID}, CURDATE(), 2, 0, {Customer}, 0) AS MRP,
                                                    {BaseUnitQuantity} AS BaseUnitQuantity,
                                                    {GST} AS GST''')
                        
                        InvoiceEdit=SPOSInvoiceEditSerializer(ratemrpquery,many=True).data
                        InvoiceDatalist =[]
                        
                        for p in InvoiceEdit:
                                InvoiceDatalist.append({
                                    "Rate": p['Rate'],
                                    "MRP": p['MRP'],
                                    "BaseUnitQuantity": p['BaseUnitQuantity'],
                                    "GST": p['GST']
                                })

                        OrderItemDetails.append({
                            
                            "id": b['id'],
                            "Item": ItemID,
                            "ItemName": b['ItemName'],
                            "MIUnitID" : b['MIUnitID'],
                            "Quantity": b['Quantity'],
                            "MRPValue": b['MRPValue'],
                            "Rate": b['Rate'],
                            "Unit": b['Unit'],
                            "UnitName": b['UnitName'],
                            "MCUnitsUnitID":b['MCUnitsUnitID'],
                            "ConversionUnit": b['ConversionUnit'],
                            "BaseUnitQuantity": b['BaseUnitQuantity'],
                            "HSNCode": b['HSNCode'],
                            "GSTPercentage": b['GSTPercentage'],
                            "BasicAmount": b['BasicAmount'],
                            "GSTAmount": b['GSTAmount'],
                            "CGST": b['CGST'],
                            "SGST": b['SGST'],
                            "IGST": b['IGST'],
                            "CGSTPercentage": b['CGSTPercentage'],
                            "SGSTPercentage": b['SGSTPercentage'],
                            "IGSTPercentage": b['IGSTPercentage'],
                            "Amount": b['Amount'],
                            "DiscountType" : b['DiscountType'],
                            "Discount" :b['Discount'] ,
                            "DiscountAmount":b['DiscountAmount'],
                            "UnitDetails":UnitDropdown(b['Item'],Customer,0),
                            "StockDetails":InvoiceDatalist
                        })
                    Orderdata.append({
                        "OrderIDs":[str(query1[0]['Order'])],
                        "OrderItemDetails":OrderItemDetails,
                        "InvoiceDate":InvoiceDate,
                        "Vehicle":Vehicle,
                        "AdvanceAmount": AdvanceAmount,
                        "CreatedBy" : CreatedBy
                        }) 
             
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Orderdata[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})  

            
   