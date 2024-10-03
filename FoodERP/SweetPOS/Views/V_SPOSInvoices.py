from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
import base64
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from django.contrib.auth import authenticate
from FoodERPApp.Views.V_CommFunction import UnitwiseQuantityConversion, create_transaction_logNew
from FoodERPApp.models import *
from SweetPOS.Serializer.S_SPOSInvoices import *
# from SweetPOS.Serializer.S_SPOSInvoices import SaleItemSerializer
from rest_framework import status
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction

from ..models import  *


def BasicAuthenticationfunction(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
                    
        # Parsing the authorization header
        auth_type, auth_string = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            
            
            try:
                username, password = base64.b64decode(
                    auth_string).decode().split(':', 1)
            except (TypeError, ValueError, UnicodeDecodeError):
                return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                
        user = authenticate(request, username=username, password=password)
    return user

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
                        # queryforParty=M_SweetPOSRoleAccess.objects.using('sweetpos_db').filter(Party=Invoicedata['DivisionID']).values('Party')
                        # CustomPrint(queryforParty)
                        # queryforParty=1
                        # if not queryforParty:
                        #     return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'DivisionId is not mapped. Please map it from the SPOSRoleAccess page.', 'Data':[]})
                        # else:
                        # ==========================Get Max Invoice Number=====================================================
                        
                        Invoicedata['TCSAmount']=0.0
                        Invoicedata['InvoiceNumber'] = Invoicedata['BillNumber']
                        Invoicedata['InvoiceDate'] = Invoicedata['SaleDate']
                        Invoicedata['FullInvoiceNumber'] = Invoicedata['BillNumber']
                        Invoicedata['Customer'] = 43194
                        Invoicedata['Party'] = Invoicedata['DivisionID']
                        Invoicedata['GrandTotal'] =Invoicedata['RoundedAmount']
                        Invoicedata['RoundOffAmount'] =Invoicedata['RoundOffAmount']
                        Invoicedata['Driver'] = 0
                        # Invoicedata['Vehicle'] = ""
                        Invoicedata['SaleID'] =0
                        Invoicedata['MobileNo'] =Invoicedata['Mobile']
                        
                        
                            
                        
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
                            InvoiceItem['IsMixItem'] = InvoiceItem.get('IsMixItem', 0)  
                            InvoiceItem['MixItemId'] = InvoiceItem.get('MixItemId', None) 
                            BaseUnitQuantity=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,0,0).GetBaseUnitQuantity()
                            InvoiceItem['BaseUnitQuantity'] =  float(BaseUnitQuantity)
                            QtyInNo=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,1,0).ConvertintoSelectedUnit()
                            InvoiceItem['QtyInNo'] =  float(QtyInNo)
                            QtyInKg=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,2,0).ConvertintoSelectedUnit()
                            InvoiceItem['QtyInKg'] = float(QtyInKg)
                            QtyInBox=UnitwiseQuantityConversion(ItemId,InvoiceItem['Quantity'],quryforunit[0]['id'],0,0,4,0).ConvertintoSelectedUnit()
                            InvoiceItem['QtyInBox'] = float(QtyInBox)
                            
                            Invoice_serializer = SPOSInvoiceSerializer(data=Invoicedata)
                            
                        if Invoice_serializer.is_valid():
                            Invoice = Invoice_serializer.save()
                            
                            LastInsertId = Invoice.id
                            LastIDs.append(Invoice.id)
                            
                        else:
                            log_entry = create_transaction_logNew(request, inputdata, Party, str(Invoice_serializer.errors),34,0,0,0,0)
                            transaction.set_rollback(True)
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': Invoice_serializer.errors, 'Data':[]})
                            
                log_entry = create_transaction_logNew(request, inputdata,Party ,'InvoiceDate:'+Invoicedata['InvoiceDate']+','+'Supplier:'+str(Party)+','+'TransactionID:'+str(LastIDs),383,0,0,0, 0)    
                return JsonResponse({'status_code': 200, 'Success': True,  'Message': 'Invoice Save Successfully','TransactionID':LastIDs, 'Data':[]})
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
                    
                    QueryfordivisionID = M_SweetPOSRoleAccess.objects.filter(Party=DivisionID).values('Party')
                    if not QueryfordivisionID:
                            
                            return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': 'DivisionId is not mapped. Please map it from the SPOSRoleAccess page.', 'Data':[]})
                    else:
                        
                        QueryForMaxSalesID=T_SPOSInvoices.objects.raw('''SELECT 1 id,ifnull(max(ClientSaleID),0) MaxSaleID FROM SweetPOS.T_SPOSInvoices where Party=%s and clientID=%s''', [QueryfordivisionID[0]['Party'] ,ClientID])
                        for row in QueryForMaxSalesID:
                            maxSaleID=row.MaxSaleID

                        log_entry = create_transaction_logNew(request, 0, QueryfordivisionID[0]['Party'],'',384,0,0,0,ClientID)
                        return JsonResponse({"Success":True,"status_code":200,"SaleID":maxSaleID,"Toprows":200})    
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
                InvoiceQuery = T_SPOSInvoices.objects.raw(f'''SELECT SPOSInv.id,InvoiceDate,InvoiceNumber,FullInvoiceNumber,TCSAmount,GrandTotal,RoundOffAmount,Customer,
                                                          cust.Name CustomerName,cust.GSTIN CustomerGSTIN,cust.MobileNo CustomerMobileNo,
Party,party.Name PartyName,party.GSTIN PartyGSTIN,party.MobileNo PartyMobileNo,M_Drivers.Name DriverName,M_Vehicles.VehicleNumber,SPOSInv.CreatedOn,
custaddr.FSSAINo CustomerFSSAI ,custaddr.Address CustomerAddress,
partyaddr.FSSAINo PartyFSSAI,partyaddr.Address PartyAddress,MC_PartyBanks.BranchName,MC_PartyBanks.IFSC,MC_PartyBanks.AccountNo,M_Bank.Name BankName,MC_PartyBanks.IsDefault,custstate.Name CustState,partystate.Name PartyState
,IU.AckNo, IU.Irn, IU.QRCodeUrl, IU.EInvoicePdf, IU.EwayBillNo, IU.EwayBillUrl, IU.EInvoiceCreatedBy, IU.EInvoiceCreatedOn, IU.EwayBillCreatedBy, IU.EwayBillCreatedOn, IU.EInvoiceCanceledBy, IU.EInvoiceCanceledOn, IU.EwayBillCanceledBy, IU.EwayBillCanceledOn, 
IU.EInvoiceIsCancel, IU.EwayBillIsCancel,c.name as CompanyName,u.LoginName as CashierName,party.AlternateContactNo
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
left join FoodERP.C_Companies c on party.Company_id=c.id  
left join FoodERP.M_Users u on SPOSInv.CreatedBy=u.id                                                      
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
                            # Add Company Name, CashierName, AlternateContactNo
                            "CompanyName":a.CompanyName,
                            "CashierName" :a.CashierName,
                            "AlternateContactNo":a.AlternateContactNo,
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
    # authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        CustomerVehicledata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                VehicleUpdate = T_SPOSInvoices.objects.using('sweetpos_db').filter(id=CustomerVehicledata['InvoiceID']).update(Vehicle=CustomerVehicledata['vehicle'],Customer=CustomerVehicledata['Customer'])
                log_entry = create_transaction_logNew(request,CustomerVehicledata,0, {'POSInvoiceID':id},67,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': ' Customer and Vehicle No Updated Against Invoice Successfully ', 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, CustomerVehicledata, 0,'UpdateCustomerVehiclePOSInvoice:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})        
        
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
                        InvoiceDeleteUpdate = T_SPOSInvoices.objects.using('sweetpos_db').filter(ClientID=DeleteInvoicedata['ClientID'],ClientSaleID=DeleteInvoicedata['ClientSaleID'],Party=DeleteInvoicedata['PartyID'],InvoiceDate=DeleteInvoicedata['InvoiceDate']).values('id')
                        
                        
                        if DeleteInvoicedata['UpdatedInvoiceDetails'] :
                            
                            invoice_instance = T_SPOSInvoices.objects.get(id=InvoiceDeleteUpdate[0]['id'])
                            InvoiceItems = DeleteInvoicedata['UpdatedInvoiceDetails'][0]['SaleItems']
                            InvoiceUpdate=T_SPOSInvoices.objects.filter(id=InvoiceDeleteUpdate[0]['id']).update(GrandTotal=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['RoundedAmount'],DiscountAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['DiscountAmount'],TotalAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['TotalAmount'],RoundOffAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['RoundOffAmount'],NetAmount=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['NetAmount'],UpdatedBy=DeleteInvoicedata['UpdatedInvoiceDetails'][0]['UpdatedBy'])
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
                    log_entry = create_transaction_logNew(request,DeleteInvoicedatas,0, {'POSDeletedInvoiceID':InvoiceIDs}, 388,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True,  'Message': 'POSInvoice Delete Successfully ', 'Data':[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, DeleteInvoicedatas, 0,'UpdatePOSInvoiceDelete:'+str(e),33,0)
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
                    
                    QueryForMaxSalesID=T_SPOSDeletedInvoices.objects.raw('''SELECT 1 id,ifnull(max(DeletedTableAutoID),0) MaxSaleID FROM SweetPOS.T_SPOSDeletedInvoices where Party=%s and clientID=%s''', [DivisionID ,ClientID])
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
                                                        (SELECT SUM(SweetPOS.T_SPOSInvoices.TotalAmount) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party= %s) TotalAmount,
                                                        (SELECT COUNT(id) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party= %s) BillCount,
                                                        (SELECT TIME(MIN(SweetPOS.T_SPOSInvoices.CreatedOn)) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s) FirstBillTime,
                                                        (SELECT TIME(MAX(SweetPOS.T_SPOSInvoices.CreatedOn)) from SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s) LastBillTime,
                                                        (SELECT FullInvoiceNumber FROM SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s ORDER BY id DESC LIMIT 1) LastInvoiceNumber,
                                                        (SELECT TotalAmount FROM SweetPOS.T_SPOSInvoices WHERE SweetPOS.T_SPOSInvoices.InvoiceDate BETWEEN %s AND %s AND SweetPOS.T_SPOSInvoices.Party = %s ORDER BY id DESC LIMIT 1) LastInvoiceAmount
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
                        "TopSaleItems": TopSaleItems_List
                    })
                if Party_List:
                    log_entry = create_transaction_logNew(request, SaleData, 0, 'TopSaleItems:' + str(Party_List), 390, 0)
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
                query = M_ConsumerMobile.objects.filter(IsLinkToBill=False,MacID=MacID).order_by('-id')
                if query:
                    Mobile_serializer = MobileSerializer(query, many=True).data
                    log_entry = create_transaction_logNew(request, Mobile_serializer, 0, '', 412, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Mobile_serializer})
                log_entry = create_transaction_logNew(request, Mobile_serializer, 0, 'Mobile Number not available', 412, 0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Mobile Number not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'Get All Mobile Number:'+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]})
        

class MobileNumberUpdateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
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

