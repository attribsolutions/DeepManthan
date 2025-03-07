import json
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from SweetPOS.models import *

from ..Serializer.S_EInvoiceEwayBill import *


from ..Serializer.S_Orders import *
from ..models import *
import requests
import json
from datetime import datetime, timedelta


def generate_Access_Token():
    Auth_URL = "https://pro.mastersindia.co/oauth/access_token"
    dataArray = {
        "username": "a.kiranmali@gmail.com",
        "password": "MastersPassWord@7",
        "client_id": "ihaBcllRnZoJekHqxX",
        "client_secret": "wbx4SxdBdogRDjxxqnUp1Sof",
        "grant_type": "password"
    }
    payload = json.dumps(dataArray)
    headers = {'Content-Type': 'application/json',}

    response = requests.request("POST", Auth_URL, headers=headers, data=payload)
    data_dict = json.loads(response.text)
    # access_token = data_dict['access_token']
    if(response.ok):
        return  '1!'+data_dict['access_token']
    else:
        return  '0!'+str(data_dict)

#================================================Uploaded_EInvoice=============================================

class Uploaded_EInvoice(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0,Mode=0):
        try:
            with transaction.atomic():

                access_token = generate_Access_Token()
                aa=access_token.split('!')
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
# =======================================================================================
                
                if(aa[0] == '1'):
                    
                    access_token=aa[1]
                    if int(Mode) == 1:    #This Mode is 1 for FoodERPInvoice and 2 for SweetPoS Invoice
                        
                        ItemQuery = T_Invoices.objects.raw('''select * from (SELECT T_Invoices.id ,T_Invoices.InvoiceDate document_date,
    P.Name seller_legal_name,C.Name Buyer_legal_name,T_Invoices.FullInvoiceNumber document_number,
    PS.Name seller_State ,CS.Name buyer_State,PS.StateCode Seller_state_code ,CS.StateCode Buyer_state_code,
    PD.Name Seller_location ,CD.Name Buyer_location,
    P.GSTIN Seller_gstin,C.GSTIN Buyer_gstin, 
    PA.Address seller_address1,PA.PIN seller_pincode,CA.Address Buyer_address1,PA.PIN buyer_pincode 
    FROM T_Invoices 
    join M_Parties P on P.id=T_Invoices.Party_id
    join M_Parties C on C.id=T_Invoices.Customer_id
    left join MC_PartyAddress PA on PA.Party_id=P.id and PA.IsDefault=1
    left join MC_PartyAddress CA on CA.Party_id=C.id and CA.IsDefault=1
    left join M_States PS on PS.id=P.State_id
    left join M_States CS on CS.id=C.State_id
    left join M_Districts PD on PD.id=P.District_id
    left join M_Districts CD on  CD.id=C.District_id
    where T_Invoices.id=%s)a
    left join 
    (select sum(BasicAmount)Total_assessable_value,(sum(Amount))total_invoice_value,sum(CGST)total_cgst_value,
    sum(SGST) total_sgst_value,sum(IGST)total_igst_value,sum(DiscountAmount)total_discount, Invoice_id 
    from TC_InvoiceItems where Invoice_id=%s)b
    on a.id=b.Invoice_id''',([id],[id])
    )
                        InvoiceItem=TC_InvoiceItems.objects.raw('''SELECT M_Items.id,M_Items.Name ItemName ,M_GSTHSNCode.HSNCode,sum(Quantity) Quantity,M_Units.EwayBillUnit,TC_InvoiceItems.Rate,sum(TC_InvoiceItems.DiscountAmount)DiscountAmount,
    sum(CGST)CGST,sum(SGST)SGST,sum(IGST)IGST,(sum(BasicAmount)+sum(DiscountAmount))total_amount,(sum(BasicAmount))assessable_value,TC_InvoiceItems.GSTPercentage gst_rate,
    sum(Amount) total_item_value
    FROM TC_InvoiceItems 
    join M_Items on TC_InvoiceItems.Item_id=M_Items.id
    join M_GSTHSNCode on M_GSTHSNCode.id=TC_InvoiceItems.GST_id
    join MC_ItemUnits on MC_ItemUnits.id=TC_InvoiceItems.Unit_id
    join M_Units on M_Units.id=MC_ItemUnits.UnitID_id


    where Invoice_id=%s group by TC_InvoiceItems.Item_id,M_GSTHSNCode.HSNCode,M_Units.EwayBillUnit,TC_InvoiceItems.Rate,TC_InvoiceItems.GSTPercentage
    ''',[id])
                        
                    else:
                        
                        ItemQuery = T_SPOSInvoices.objects.raw('''select * from (SELECT SPOSInvoice.id ,SPOSInvoice.InvoiceDate document_date,
P.Name seller_legal_name,C.Name Buyer_legal_name,SPOSInvoice.FullInvoiceNumber document_number,
PS.Name seller_State ,CS.Name buyer_State,PS.StateCode Seller_state_code ,CS.StateCode Buyer_state_code,
PD.Name Seller_location ,CD.Name Buyer_location,
P.GSTIN Seller_gstin,C.GSTIN Buyer_gstin, 
PA.Address seller_address1,PA.PIN seller_pincode,CA.Address Buyer_address1,CA.PIN buyer_pincode 
FROM SweetPOS.T_SPOSInvoices SPOSInvoice
join FoodERP.M_Parties P on P.id=SPOSInvoice.Party
join FoodERP.M_Parties C on C.id=SPOSInvoice.Customer
left join FoodERP.MC_PartyAddress PA on PA.Party_id=P.id and PA.IsDefault=1
left join FoodERP.MC_PartyAddress CA on CA.Party_id=C.id and CA.IsDefault=1
left join FoodERP.M_States PS on PS.id=P.State_id
left join FoodERP.M_States CS on CS.id=C.State_id
left join FoodERP.M_Districts PD on PD.id=P.District_id
left join FoodERP.M_Districts CD on  CD.id=C.District_id
where SPOSInvoice.id=%s)a
left join 
(select sum(BasicAmount)Total_assessable_value,(sum(Amount))total_invoice_value,sum(CGST)total_cgst_value,
sum(SGST) total_sgst_value,sum(IGST)total_igst_value,sum(DiscountAmount)total_discount, Invoice_id 
from SweetPOS.TC_SPOSInvoiceItems where Invoice_id=%s)b
on a.id=b.Invoice_id''',([id],[id])
)
                        InvoiceItem=TC_SPOSInvoiceItems.objects.raw('''SELECT M_Items.id,M_Items.Name ItemName ,SPOSInvoiceItems.HSNCode,sum(Quantity) Quantity,M_Units.EwayBillUnit,SPOSInvoiceItems.Rate,sum(SPOSInvoiceItems.DiscountAmount)DiscountAmount,
sum(CGST)CGST,sum(SGST)SGST,sum(IGST)IGST,(sum(BasicAmount)+sum(DiscountAmount))total_amount,(sum(BasicAmount))assessable_value,SPOSInvoiceItems.GSTPercentage gst_rate,
sum(Amount) total_item_value
FROM SweetPOS.TC_SPOSInvoiceItems SPOSInvoiceItems
join FoodERP.M_Items on SPOSInvoiceItems.Item=M_Items.id
join FoodERP.MC_ItemUnits on MC_ItemUnits.id=SPOSInvoiceItems.Unit
join FoodERP.M_Units on M_Units.id=MC_ItemUnits.UnitID_id


where Invoice_id=%s group by SPOSInvoiceItems.Item,SPOSInvoiceItems.HSNCode,M_Units.EwayBillUnit,SPOSInvoiceItems.Rate,SPOSInvoiceItems.GSTPercentage
 ''',[id])
                    
                    InvoiceUploadSerializer = InvoicegovUploadSerializer2(ItemQuery, many=True).data
                    Invoice=InvoiceUploadSerializer[0]
                    InvoiceItemUploadSerializer = InvoiceItemgovUploadSerializer2(InvoiceItem, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceItemUploadSerializer})

                    InvoiceData = list()
                    transaction_details = list()
                    document_details = list()
                    seller_details = list()
                    buyer_details = list()
                    dispatch_details = list()
                    ship_details = list()
                    reference_details = list()
                    document_period_details = list()
                    preceding_document_details = list()
                    value_details = list()
                    ewaybill_details = list()
                    InvoiceItemDetails = list()
                    # Total_assessable_value = 0
                    # total_invoice_value = 0
                    # total_cgst_value = 0
                    # total_sgst_value = 0
                    # total_igst_value = 0
                    # total_discount = 0
                    # for Invoice in InvoiceUploadSerializer:
                        # user_gstin=Invoice['Party']['GSTIN']
                    
                    for a in InvoiceItemUploadSerializer:
                        if int(Mode) == 1:
                            q0=TC_InvoiceItems.objects.filter(Invoice_id=id ,Item_id=a['id']).values("BatchCode")
                        else:
                            q0=TC_SPOSInvoiceItems.objects.using('sweetpos_db').filter(Invoice_id=id ,Item=a['id']).values("BatchCode")
                        Batchlist = list()
                        for d in q0:
                            Batchlist.append({
                                'name': "Batch-"+d['BatchCode']
                            })
                            if a['HSNCode'].startswith("99"):
                                is_service= "Y"  # Yes, it's a service
                            else:
                                is_service= "N" # No, it's not a service
                        InvoiceItemDetails.append({
                            'item_serial_number': a['id'],
                            'product_description': a['ItemName'],
                            'is_service': is_service,
                            'hsn_code': a['HSNCode'],
                            'quantity': a['Quantity'],
                            'unit': a['EwayBillUnit'],
                            'unit_price': a['Rate'],
                            'discount': a['DiscountAmount'],
                            'igst_amount': a['IGST'],
                            'cgst_amount': a['CGST'],
                            'sgst_amount': a['SGST'],
                            'total_amount': float(a['total_amount']),
                            'assessable_value': float(a['assessable_value']),
                            'gst_rate': a['gst_rate'],
                            'total_item_value': float(a['total_item_value']),
                            'batch_details': Batchlist
                        })

                   
                   
                    transaction_details.append({
                        "supply_type": 'B2B'
                    }),
                    document_details.append({
                        'document_type': 'INV',
                        'document_number': Invoice['document_number'],
                        'document_date': Invoice['document_date']
                    }),
                    seller_details.append({
                        'gstin': Invoice['Seller_gstin'],
                        'legal_name': Invoice['seller_legal_name'],
                        'address1': Invoice['seller_address1'][:100],
                        'location': Invoice['Seller_location'],
                        'pincode': Invoice['seller_pincode'],
                        'state_code': Invoice['seller_State']
                    }),
                    buyer_details.append({
                        'gstin': Invoice['Buyer_gstin'],
                        'legal_name': Invoice['Buyer_legal_name'],
                        'address1': Invoice['Buyer_address1'][:100],
                        'location': Invoice['Buyer_location'],
                        'pincode': Invoice['buyer_pincode'],
                        'place_of_supply': Invoice['Buyer_state_code'],
                        'state_code': Invoice['buyer_State']
                    }),
                    dispatch_details.append({
                        'company_name': Invoice['seller_legal_name'],
                        'address1': Invoice['seller_address1'][:100],
                        'location': Invoice['Seller_location'],
                        'pincode': Invoice['seller_pincode'],
                        'state_code': Invoice['seller_State']
                    }),
                    ship_details.append({
                        'gstin': Invoice['Buyer_gstin'],
                        'legal_name': Invoice['Buyer_legal_name'],
                        'address1': Invoice['Buyer_address1'][:100],
                        'location': Invoice['Buyer_location'],
                        'pincode':Invoice['buyer_pincode'],
                        'state_code': Invoice['buyer_State']
                    }),
                    a= datetime.strptime(Invoice['document_date'], "%Y-%m-%d")
                    c = a+timedelta(days=1)
                    d=c.date()
                    # CustomPrint(d)
                    document_period_details.append({
                        'invoice_period_start_date': Invoice['document_date'],
                        # 'invoice_period_end_date': c.date()
                        'invoice_period_end_date': Invoice['document_date']
                    })
                    reference_details.append({
                        'document_period_details': document_period_details
                    }),

                    preceding_document_details.append({
                        'reference_of_original_invoice': Invoice['id'],
                        'preceding_invoice_date': Invoice['document_date']
                    }),
                    value_details.append({
                        'total_assessable_value': Invoice['Total_assessable_value'],
                        'total_invoice_value': Invoice['total_invoice_value'],
                        'total_cgst_value': Invoice['total_cgst_value'],
                        'total_sgst_value': Invoice['total_sgst_value'],
                        'total_igst_value': Invoice['total_igst_value'],
                        'total_discount': 0
                    }),
                    ewaybill_details.append({
                        'transportation_mode': 1,
                        'transportation_distance': 1
                    })

                    
                    InvoiceData.append({

                        "access_token": access_token,
                        "user_gstin": Invoice['Seller_gstin'],
                        "transaction_details": transaction_details[0],
                        "document_details": document_details[0],
                        "seller_details": seller_details[0],
                        "buyer_details": buyer_details[0],
                        "dispatch_details": dispatch_details[0],
                        "ship_details": ship_details[0],
                        "reference_details": reference_details[0],
                        "preceding_document_details": preceding_document_details[0],
                        "value_details": value_details[0],
                        "ewaybill_details": ewaybill_details[0],
                        "item_list": InvoiceItemDetails
                    })
                    # CustomPrint(InvoiceData)
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': '', 'Data': InvoiceData[0]})
                    EInvoice_URL = 'https://pro.mastersindia.co/generateEinvoice'
                    payload1 = json.dumps(InvoiceData[0])
                    # payload = json.loads(payload1)
                    headers = {
                        'Content-Type': 'application/json',
                    }
                   
                    response = requests.request(
                        "POST", EInvoice_URL, headers=headers, data=payload1)
                    
                    data_dict = json.loads(response.text)
                    # print(data_dict)
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': data_dict['results']['status'], 'Data': InvoiceData[0]})
                    if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                        if int(Mode) == 1:
                            Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                        else:
                            Query=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice_id=id)
                        if(Query.count() > 0):
                            if int(Mode) == 1:
                                StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())
                            else:
                                StatusUpdates=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice=id).update(Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())
                            log_entry = create_transaction_logNew(request,InvoiceUploadSerializer,0,'E-Invoice Upload Successfully',362,0 )
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Upload Successfully', 'Data': payload1 })
                        else:
                            if int(Mode) == 1:
                                InvoiceID=T_Invoices.objects.get(id=id)
                                Statusinsert=TC_InvoiceUploads.objects.create(Invoice=InvoiceID,user_gstin=Invoice['Seller_gstin'],Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())        
                            else:
                                InvoiceID=T_SPOSInvoices.objects.using('sweetpos_db').get(id=id)
                                Statusinsert=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').create(Invoice=InvoiceID,user_gstin=Invoice['Seller_gstin'],Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())        
                            
                            log_entry = create_transaction_logNew(request,InvoiceUploadSerializer,0,f'E-Invoice Upload Successfully  of InvoiceID: {InvoiceID}',362,0 )
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Upload Successfully', 'Data': payload1})
                    else:
                        log_entry = create_transaction_logNew(request, InvoiceUploadSerializer,0, data_dict['results'], 92,0)
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results'], 'Data': InvoiceData[0] })
                    
                else:
                    log_entry = create_transaction_logNew(request,InvoiceUploadSerializer,0, aa[1],362,0) 
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'E-Invoice Upload:'+str((e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': Exception(e), 'Data': []})


# class Uploaded_EwayBill(CreateAPIView):
#     permission_classes = (IsAuthenticated,)

#     @transaction.atomic()
#     def get(self, request, id=0,userID=0):
#         try:
#             with transaction.atomic():
#                 Query=T_Invoices.objects.filter(id=id).values('Vehicle')
#                 if (Query[0]['Vehicle']) is None:
#                     log_entry = create_transaction_logNew(request,0,0,'Vehicle Number is required',363,0)
#                     return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Vehicle Number is required', 'Data':id })
#                 else:
#                     # CustomPrint('bbbbbbbbbb')
#                     access_token = generate_Access_Token()
#                     aa=access_token.split('!')
#                     # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
#     # =======================================================================================
                    
#                     if(aa[0] == '1'):
#                         # CustomPrint('ccccccccccc')
#                         access_token=aa[1]
#                         ItemQuery = T_Invoices.objects.filter(id=id)
#                         InvoiceUploadSerializer = InvoicegovUploadSerializer(
#                             ItemQuery, many=True).data
#                         # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceUploadSerializer})
#                         # CustomPrint('qqqqqqqqqqq')
#                         InvoiceData = list()
#                         InvoiceItemDetails = list()
#                         Total_assessable_value = 0
#                         total_invoice_value = 0
#                         total_cgst_value = 0
#                         total_sgst_value = 0
#                         total_igst_value = 0
#                         total_discount = 0
#                         for Invoice in InvoiceUploadSerializer:
#                             user_gstin=Invoice['Party']['GSTIN']
#                             for address in Invoice['Party']['PartyAddress']:
#                                 if address['IsDefault'] == 1:
#                                     selleraddress = address['Address'][:100]
#                                     sellerpin = address['PIN']

#                             for address in Invoice['Customer']['PartyAddress']:
#                                 if address['IsDefault'] == 1:
#                                     buyeraddress = address['Address'][:100]
#                                     buyerpin = address['PIN']
#                 #====================================Distance Calculate API====================================================            
#                             Calculate_Distance_URL = f"https://pro.mastersindia.co/distance?access_token={access_token}&fromPincode={sellerpin}&toPincode={buyerpin}"
#                             headers = {'Content-Type': 'application/json',}
#                             response = requests.request("GET", Calculate_Distance_URL, headers=headers)

#                             distance_dict = json.loads(response.text)
                            
#                 #===============================================================================================================           
#                             if(distance_dict['results']['status']== 'Success' and distance_dict['results']['code']== 200):
                                
                            
#                                 for a in Invoice['InvoiceItems']:

#                                     # assessable_value=float(a['Quantity'])*float(a['Rate'])
#                                     Total_assessable_value = float(
#                                         Total_assessable_value) + float(a['BasicAmount'])
#                                     total_invoice_value = float(
#                                         total_invoice_value) + float(a['Amount'])
#                                     total_cgst_value = float(
#                                         total_cgst_value) + float(a['CGST'])
#                                     total_sgst_value = float(
#                                         total_sgst_value) + float(a['SGST'])
#                                     total_igst_value = float(
#                                         total_igst_value) + float(a['IGST'])
#                                     total_discount = float(
#                                         total_discount) + float(a['DiscountAmount'])

#                                     InvoiceItemDetails.append({
#                                         "product_name": a['Item']['Name'],
#                                         "product_description": a['Item']['Name'],
#                                         "hsn_code": a['GST']['HSNCode'],
#                                         "quantity": a['Quantity'],
#                                         "unit_of_product": a['Unit']['UnitID']['EwayBillUnit'],
#                                         "cgst_rate": a['SGSTPercentage'],
#                                         "sgst_rate": a['SGSTPercentage'],
#                                         "igst_rate": a['IGSTPercentage'],
#                                         "cess_rate": 0,
#                                         "cessNonAdvol": 0,
#                                         "taxable_amount": a['BasicAmount'],
#                                     })

                                

#                                 InvoiceData.append({

#                                     'access_token': access_token,
#                                     'userGstin': Invoice['Party']['GSTIN'],
#                                     'supply_type': "outward",
#                                     'sub_supply_type': "Supply",
#                                     'sub_supply_description': " ",
#                                     'document_type': "TaxInvoice",
#                                     'document_number': Invoice['id'],
#                                     'document_date': Invoice['InvoiceDate'],
#                                     'gstin_of_consignor': Invoice['Party']['GSTIN'],
#                                     'legal_name_cosignor': Invoice['Party']['Name'],
#                                     'address1_of_consignor': selleraddress,
#                                     'address2_of_consignor': '',
#                                     'pincode_of_consignor': sellerpin,
#                                     'state_of_consignor': Invoice['Party']['State']['Name'],
#                                     'actual_from_state_name': Invoice['Party']['State']['Name'],
#                                     'gstin_of_consignee': Invoice['Customer']['GSTIN'],
#                                     'legal_name_of_consignee': Invoice['Customer']['Name'],
#                                     'address1_of_consignee': buyeraddress,
#                                     'address2_of_consignee': "",
#                                     'place_of_consignee': Invoice['Customer']['City']['Name'],
#                                     'pincode_of_consignee': buyerpin,
#                                     'state_of_supply': Invoice['Customer']['State']['Name'],
#                                     'actual_to_state_name': Invoice['Customer']['State']['Name'],
#                                     'other_value': '0',
#                                     'total_invoice_value': Invoice['GrandTotal'],
#                                     'taxable_amount': Total_assessable_value,
#                                     'cgst_amount': total_cgst_value,
#                                     'sgst_amount': total_sgst_value,
#                                     'igst_amount': total_igst_value,
#                                     'cess_amount': '0',
#                                     'cess_nonadvol_value': '0',
#                                     'transporter_id': "",
#                                     'transporter_document_number': "",
#                                     'transporter_document_date': "",
#                                     'transportation_mode': "road",
#                                     'transportation_distance': distance_dict['results']['distance'],
#                                     'vehicle_number': Invoice['Vehicle']['VehicleNumber'],
#                                     'transporter_name': "",
#                                     'vehicle_type': "Regular",
#                                     'data_source': "erp",
#                                     'user_ref': "1232435466sdsf234",
#                                     'eway_bill_status': "Y",
#                                     'auto_print': "Y",
#                                     'email' : Invoice['Party']['Email'],
#                                     'itemList': InvoiceItemDetails
#                                 })
#                                 # CustomPrint('ddddddddddddd')
#                                 E_Way_Bill_URL = 'https://pro.mastersindia.co/ewayBillsGenerate'
                                
#                                 payload = json.dumps(InvoiceData[0])
                                
#                                 headers = {
#                                     'Content-Type': 'application/json',
#                                 }
#                                 # CustomPrint(payload)
                            
#                                 response = requests.request(
#                                     "POST", E_Way_Bill_URL, headers=headers, data=payload)

#                                 data_dict = json.loads(response.text)
#                                 # CustomPrint('ffffffffffffff')
#                                 # CustomPrint(data_dict)
#                                 if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
#                                     # CustomPrint('ggggggg')
#                                     Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                                    
#                                     if(Query.count() > 0):
                                        
#                                         StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())
#                                         log_entry = create_transaction_logNew(request,InvoiceUploadSerializer,0,'E-WayBill Upload Successfully',363,0 )
#                                         return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Upload Successfully', 'Data': InvoiceData[0] })
#                                     else:
#                                         InvoiceID=T_Invoices.objects.get(id=id)
#                                         Statusinsert=TC_InvoiceUploads.objects.create(Invoice=InvoiceID,user_gstin=user_gstin,EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())        
#                                         log_entry = create_transaction_logNew(request,InvoiceUploadSerializer,0,f'E-WayBill Upload Successfully  of InvoiceID: {InvoiceID}',363,0 )
#                                         return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Upload Successfully', 'Data': InvoiceData[0] })
#                                 else:
#                                     # CustomPrint('hhhhhhh')
#                                     log_entry = create_transaction_logNew(request, InvoiceUploadSerializer,0, data_dict['results'], 363,0)
#                                     return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': data_dict['results'], 'Data': InvoiceData[0] })
#                             else:
#                                 log_entry = create_transaction_logNew(request, InvoiceUploadSerializer,0, distance_dict['results'], 363,0)
#                                 return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': distance_dict['results'], 'Data': [] })     
                            
#                     else:
#                         log_entry = create_transaction_logNew(request,InvoiceUploadSerializer,0, aa[1],363,0) 
#                         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
#         except Exception as e:
#             log_entry = create_transaction_logNew(request, 0, 0, 'E-WayBill Upload:'+str((e)),33,0)
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
#==========+}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}}==================================================================== 
class Uploaded_EwayBill(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0,Mode=0):
        try:
            with transaction.atomic():
                if int(Mode) == 1:
                    Query=T_Invoices.objects.filter(id=id).values('Vehicle')
                else:
                    Query=T_SPOSInvoices.objects.using('sweetpos_db').filter(id=id).values('Vehicle')
                  
                if (Query[0]['Vehicle']) is None:
                    log_entry = create_transaction_logNew(request,0,0,'Vehicle Number is required',363,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Vehicle Number is required', 'Data':id })
                else:
                   
                    # CustomPrint('bbbbbbbbbb')
                    access_token = generate_Access_Token()
                    aa=access_token.split('!')
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
    # =======================================================================================
                    
                    if(aa[0] == '1'):
                        
                        access_token=aa[1]
                        if int(Mode) == 1:
                            InvoiceQuery=T_Invoices.objects.raw(f'''SELECT P.Name PartyName,PA.Address selleraddress,PA.PIN sellerpin,PS.Name PartyState,P.GSTIN PartyGSTIN,
       C.Name CustomerName,CA.Address buyeraddress,CA.PIN buyerpin,CS.Name CustomerState,C.GSTIN CustomerGSTIN,
       SPOSIn.id,SPOSIn.InvoiceDate,SPOSIn.GrandTotal,vehic.VehicleNumber VehicleNumber,CC.Name CustomerCity,P.Email PartyEmail ,
       SPOSIn.FullInvoiceNumber
FROM FoodERP.T_Invoices SPOSIn
join FoodERP.M_Parties P on P.id=SPOSIn.Party_id
join FoodERP.M_Parties C on C.id=SPOSIn.Customer_id
left join FoodERP.MC_PartyAddress PA on PA.Party_id=P.id and PA.IsDefault=1
left join FoodERP.MC_PartyAddress CA on CA.Party_id=C.id and CA.IsDefault=1
left join FoodERP.M_States PS on PS.id=P.State_id
left join FoodERP.M_States CS on CS.id=C.State_id
left join FoodERP.M_Cities CC on CC.id=C.City_id
left join FoodERP.M_Vehicles vehic on SPOSIn.Vehicle_id=vehic.id                                                                 
where SPOSIn.id= {id}''')
                        else:

                            InvoiceQuery=T_SPOSInvoices.objects.raw(f'''SELECT P.Name PartyName,PA.Address selleraddress,PA.PIN sellerpin,PS.Name PartyState,P.GSTIN PartyGSTIN,
       C.Name CustomerName,CA.Address buyeraddress,CA.PIN buyerpin,CS.Name CustomerState,C.GSTIN CustomerGSTIN,
       SPOSIn.id,SPOSIn.InvoiceDate,SPOSIn.GrandTotal,vehic.VehicleNumber VehicleNumber,CC.Name CustomerCity,P.Email PartyEmail ,
       SPOSIn.FullInvoiceNumber                                                             
FROM SweetPOS.T_SPOSInvoices SPOSIn
join FoodERP.M_Parties P on P.id=SPOSIn.Party
join FoodERP.M_Parties C on C.id=SPOSIn.Customer
left join FoodERP.MC_PartyAddress PA on PA.Party_id=P.id and PA.IsDefault=1
left join FoodERP.MC_PartyAddress CA on CA.Party_id=C.id and CA.IsDefault=1
left join FoodERP.M_States PS on PS.id=P.State_id
left join FoodERP.M_States CS on CS.id=C.State_id
left join FoodERP.M_Cities CC on CC.id=C.City_id
left join FoodERP.M_Vehicles vehic on SPOSIn.Vehicle=vehic.id 
where SPOSIn.id= {id}''')
                       
                        # InvoiceUploadSerializer = InvoicegovUploadSerializer(
                        #     ItemQuery, many=True).data
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceUploadSerializer})
                        # CustomPrint('qqqqqqqqqqq')
                        InvoiceData = list()
                        InvoiceItemDetails = list()
                        Total_assessable_value = 0
                        total_invoice_value = 0
                        total_cgst_value = 0
                        total_sgst_value = 0
                        total_igst_value = 0
                        total_discount = 0
                        
                        for Invoice in InvoiceQuery:
                           
                            user_gstin = Invoice.PartyGSTIN
                            sellerpin = Invoice.sellerpin
                            buyerpin = Invoice.buyerpin
                            # for address in Invoice['Party']['PartyAddress']:
                            #     if address['IsDefault'] == 1:
                            #         selleraddress = address['Address'][:100]
                            #         sellerpin = Invoice.PIN['PIN']

                            # for address in Invoice['Customer']['PartyAddress']:
                            #     if address['IsDefault'] == 1:
                            #         buyeraddress = address['Address'][:100]
                            #         buyerpin = address['PIN']
                #====================================Distance Calculate API====================================================            
                            Calculate_Distance_URL = f"https://pro.mastersindia.co/distance?access_token={access_token}&fromPincode={sellerpin}&toPincode={buyerpin}"
                            headers = {'Content-Type': 'application/json',}
                            response = requests.request("GET", Calculate_Distance_URL, headers=headers)

                            distance_dict = json.loads(response.text)
                           
                #===============================================================================================================           
                            if(distance_dict['results']['status']== 'Success' and distance_dict['results']['code']== 200):
                                if int(Mode) ==1 : 
                                    Itemquery=TC_SPOSInvoiceItems.objects.raw(f'''SELECT item.id,item.Name ItemName,gsthsn.HSNCode,SPOSItems.Quantity,units.EwayBillUnit,SPOSItems.SGSTPercentage,SPOSItems.CGSTPercentage,
SPOSItems.IGSTPercentage,
SPOSItems.BasicAmount, SPOSItems.CGST,SPOSItems.SGST,SPOSItems.IGST,SPOSItems.Amount,SPOSItems.DiscountAmount
FROM FoodERP.T_Invoices SPOSIn
join FoodERP.TC_InvoiceItems SPOSItems on SPOSIn.id=SPOSItems.Invoice_id
join FoodERP.M_Items item on item.id=SPOSItems.Item_id
join FoodERP.MC_ItemUnits itemunit on itemunit.id=SPOSItems.Unit_id
join FoodERP.M_Units units on units.id=itemunit.UnitID_id
join FoodERP.M_GSTHSNCode gsthsn on gsthsn.id=SPOSItems.GST_id
where Invoice_id={Invoice.id}''')
                                else :     
                                    Itemquery=TC_SPOSInvoiceItems.objects.raw(f'''SELECT item.id,item.Name ItemName,SPOSItems.HSNCode,SPOSItems.Quantity,units.EwayBillUnit,SPOSItems.SGSTPercentage,SPOSItems.CGSTPercentage,
SPOSItems.IGSTPercentage,
SPOSItems.BasicAmount, SPOSItems.CGST,SPOSItems.SGST,SPOSItems.IGST,SPOSItems.Amount,SPOSItems.DiscountAmount
FROM SweetPOS.T_SPOSInvoices SPOSIn
join SweetPOS.TC_SPOSInvoiceItems SPOSItems on SPOSIn.id=SPOSItems.Invoice_id
join FoodERP.M_Items item on item.id=SPOSItems.Item
join FoodERP.MC_ItemUnits itemunit on itemunit.id=SPOSItems.Unit
join FoodERP.M_Units units on units.id=itemunit.UnitID_id
where Invoice_id={Invoice.id}''')
                                
                                for a in Itemquery:

                                    # assessable_value=float(a['Quantity'])*float(a['Rate'])
                                    Total_assessable_value = float(
                                        Total_assessable_value) + float(a.BasicAmount)
                                    total_invoice_value = float(
                                        total_invoice_value) + float(a.Amount)
                                    total_cgst_value = float(
                                        total_cgst_value) + float(a.CGST)
                                    total_sgst_value = float(
                                        total_sgst_value) + float(a.SGST)
                                    total_igst_value = float(
                                        total_igst_value) + float(a.IGST)
                                    total_discount = float(
                                        total_discount) + float(a.DiscountAmount)

                                    InvoiceItemDetails.append({
                                        "product_name": a.ItemName,
                                        "product_description": a.ItemName,
                                        "hsn_code": a.HSNCode,
                                        "quantity": float(a.Quantity),
                                        "unit_of_product": a.EwayBillUnit,
                                        "cgst_rate": float(a.SGSTPercentage),
                                        "sgst_rate": float(a.SGSTPercentage),
                                        "igst_rate": float(a.IGSTPercentage),
                                        "cess_rate": 0,
                                        "cessNonAdvol": 0,
                                        "taxable_amount": float(a.BasicAmount),
                                    })

                                

                                InvoiceData.append({

                                    'access_token': access_token,
                                    'userGstin': Invoice.PartyGSTIN,
                                    'supply_type': "outward",
                                    'sub_supply_type': "Supply",
                                    'sub_supply_description': " ",
                                    'document_type': "TaxInvoice",
                                    'document_number': Invoice.FullInvoiceNumber,
                                    'document_date': str(Invoice.InvoiceDate),
                                    'gstin_of_consignor': Invoice.PartyGSTIN,
                                    'legal_name_cosignor': Invoice.PartyName,
                                    'address1_of_consignor': Invoice.selleraddress,
                                    'address2_of_consignor': '',
                                    'pincode_of_consignor': sellerpin,
                                    'state_of_consignor': Invoice.PartyState,
                                    'actual_from_state_name': Invoice.PartyState,
                                    'gstin_of_consignee': Invoice.CustomerGSTIN,
                                    'legal_name_of_consignee': Invoice.CustomerName,
                                    'address1_of_consignee': Invoice.buyeraddress,
                                    'address2_of_consignee': "",
                                    'place_of_consignee': Invoice.CustomerCity,
                                    'pincode_of_consignee': buyerpin,
                                    'state_of_supply': Invoice.CustomerState,
                                    'actual_to_state_name': Invoice.CustomerState,
                                    'other_value': '0',
                                    'total_invoice_value': float(Invoice.GrandTotal),
                                    'taxable_amount': float(Total_assessable_value),
                                    'cgst_amount': float(total_cgst_value),
                                    'sgst_amount': float(total_sgst_value),
                                    'igst_amount': float(total_igst_value),
                                    'cess_amount': '0',
                                    'cess_nonadvol_value': '0',
                                    'transporter_id': "",
                                    'transporter_document_number': "",
                                    'transporter_document_date': "",
                                    'transportation_mode': "road",
                                    'transportation_distance': distance_dict['results']['distance'],
                                    'vehicle_number': Invoice.VehicleNumber,
                                    'transporter_name': "",
                                    'vehicle_type': "Regular",
                                    'data_source': "erp",
                                    'user_ref': "1232435466sdsf234",
                                    'eway_bill_status': "Y",
                                    'auto_print': "Y",
                                    'email' : Invoice.PartyEmail,
                                    'itemList': InvoiceItemDetails,
                                })
                                # print(InvoiceData[0])
                                E_Way_Bill_URL = 'https://pro.mastersindia.co/ewayBillsGenerate'
                                
                               
                                payload = json.dumps(InvoiceData[0])
                                
                                headers = {
                                    'Content-Type': 'application/json',
                                }
                                
                            
                                response = requests.request(
                                    "POST", E_Way_Bill_URL, headers=headers, data=payload)

                                data_dict = json.loads(response.text)
                                
                                if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                                    # CustomPrint('ggggggg')
                                    if int(Mode) ==1 :
                                        Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                                    else:
                                        Query=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice_id=id)
                                    
                                    if(Query.count() > 0):
                                        if int(Mode)==1:
                                            StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())
                                        else:
                                            StatusUpdates=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice=id).update(EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())
                                        log_entry = create_transaction_logNew(request,payload,0,'E-WayBill Upload Successfully',363,0 )
                                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Upload Successfully', 'Data': InvoiceData[0] })
                                    else:
                                        if int(Mode) == 1:
                                            InvoiceID=T_Invoices.objects.get(id=id)
                                            Statusinsert=TC_InvoiceUploads.objects.create(Invoice=InvoiceID,user_gstin=user_gstin,EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())        
                                        else:
                                            InvoiceID=T_SPOSInvoices.objects.using('sweetpos_db').get(id=id)
                                            Statusinsert=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').create(Invoice=InvoiceID,user_gstin=user_gstin,EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())
                                        log_entry = create_transaction_logNew(request,payload,0,f'E-WayBill Upload Successfully  of InvoiceID: {InvoiceID}',363,0 )
                                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Upload Successfully', 'Data': InvoiceData[0] })
                                else:
                                    # CustomPrint('hhhhhhh')
                                    log_entry = create_transaction_logNew(request, payload,0, data_dict['results'], 363,0)
                                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': data_dict['results'], 'Data': InvoiceData[0] })
                            else:
                                log_entry = create_transaction_logNew(request, payload,0, distance_dict['results'], 363,0)
                                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': distance_dict['results'], 'Data': [] })     
                            
                    else:
                        log_entry = create_transaction_logNew(request,payload,0, aa[1],363,0) 
                        return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'E-WayBill Upload:'+str((e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})        


class Cancel_EwayBill(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0,Mode=0):
        try:
            with transaction.atomic():

                access_token = generate_Access_Token()
                aa=access_token.split('!')
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
# =======================================================================================
                invoicedetaillist=list()
                if(aa[0] == '1'):
                    access_token=aa[1]
                    if int(Mode) == 1:
                        InvoiceUploadsData=TC_InvoiceUploads.objects.filter(Invoice=id).values("user_gstin","EwayBillNo")
                    else:
                        InvoiceUploadsData=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice=id).values("user_gstin","EwayBillNo")    
                  
                    invoicedetaillist.append({
                            "access_token" : access_token,
                            "userGstin" : InvoiceUploadsData[0]["user_gstin"],
                            "eway_bill_number" : InvoiceUploadsData[0]["EwayBillNo"],
                            "reason_of_cancel" : "Others",
                            "cancel_remark" : "Data Entry Mistake",
                            "data_source" : 'erp'

                    })
                    EWayBillCancel_URL = 'https://pro.mastersindia.co/ewayBillCancel'
                    payload = json.dumps(invoicedetaillist[0])
                    
                    headers = {
                        'Content-Type': 'application/json',
                    }

                    response = requests.request(
                        "POST", EWayBillCancel_URL, headers=headers, data=payload)

                    data_dict = json.loads(response.text)
                  
                    if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                        if int(Mode) == 1:
                            Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                        else:
                            Query=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice_id=id)
                        
                        if(Query.count() > 0):
                            if int(Mode)==1:
                                StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EwayBillIsCancel=1,EwayBillCanceledBy=userID,EwayBillCanceledOn=datetime.now())
                            else:
                                StatusUpdates=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice=id).update(EwayBillIsCancel=1,EwayBillCanceledBy=userID,EwayBillCanceledOn=datetime.now())    
                            log_entry = create_transaction_logNew(request,0,0,'E-WayBill Cancel Successfully',364,0 )
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Cancel Successfully', 'Data': [] })
                        else:
                            log_entry = create_transaction_logNew(request,0,0,'E-WayBill Data Invalid',364,0 ) 
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Data Invalid', 'Data': [] })
                    else:
                        log_entry = create_transaction_logNew(request, 0,0, data_dict['results']['message'], 364,0)
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['message'], 'Data': [] })
                else:
                    log_entry = create_transaction_logNew(request,0,0, aa[1],364,0) 
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'E-WayBill Cancel:'+str((e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class Cancel_EInvoice(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0,Mode=0):
        try:
            with transaction.atomic():

                access_token = generate_Access_Token()
                aa=access_token.split('!')
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
# =======================================================================================
                invoicedetaillist=list()
                if(aa[0] == '1'):
                    access_token=aa[1]
                    if int(Mode) == 1:
                        InvoiceUploadsData=TC_InvoiceUploads.objects.filter(Invoice=id).values("user_gstin","Irn")
                    else:
                        InvoiceUploadsData=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice=id).values("user_gstin","Irn")
                    invoicedetaillist.append({
                            "access_token" : access_token,
                            "user_gstin" : InvoiceUploadsData[0]["user_gstin"],
                            "irn" : InvoiceUploadsData[0]["Irn"],
                            "cancel_reason" : "2",
                            "cancel_remarks" : "Data Entry Mistake"

                    })
                    EInvoiceCancel_URL = 'https://pro.mastersindia.co/cancelEinvoice'
                    payload = json.dumps(invoicedetaillist[0])
                    
                    headers = {
                        'Content-Type': 'application/json',
                    }

                    response = requests.request(
                        "POST", EInvoiceCancel_URL, headers=headers, data=payload)

                    data_dict = json.loads(response.text)
                    
                    if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                        if int(Mode) == 1:
                            Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                        else:
                            Query=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice_id=id)    
                        
                        if(Query.count() > 0):
                            if int(Mode) == 1:
                                StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EInvoiceIsCancel=1,EInvoiceCanceledBy=userID,EInvoiceCanceledOn=datetime.now())
                            else:
                                StatusUpdates=TC_SPOSInvoiceUploads.objects.using('sweetpos_db').filter(Invoice=id).update(EInvoiceIsCancel=1,EInvoiceCanceledBy=userID,EInvoiceCanceledOn=datetime.now())
                            
                            log_entry = create_transaction_logNew(request,0,0,'E-Invoice Cancel Successfully',365,0 )
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Cancel Successfully', 'Data': [] })
                        else:
                            log_entry = create_transaction_logNew(request,0,0,'E-InvoiceData Invalid',365,0 )   
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Data Invalid', 'Data': [] })
                    else:
                        log_entry = create_transaction_logNew(request, 0,0, data_dict['results']['errorMessage'], 92,0)
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['errorMessage'], 'Data': [] })
                else:
                    log_entry = create_transaction_logNew(request,0,0, aa[1],365,0) 
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0, 'E-Invoice Cancel:'+str((e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})



#================================================Uploaded_CreditDebitNotes_EInvoice=============================================

class Uploaded_CreditDebitNotes_EInvoice(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0):
        try:
            with transaction.atomic():

                access_token = generate_Access_Token()
                aa=access_token.split('!')
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
# =======================================================================================
                
                if(aa[0] == '1'):
                    
                    access_token=aa[1]
                    ItemQuery = T_CreditDebitNotes.objects.raw('''select * from 
                    (SELECT T_CreditDebitNotes.id ,T_CreditDebitNotes.CRDRNoteDate document_date,
P.Name seller_legal_name,C.Name Buyer_legal_name,T_CreditDebitNotes.FullNoteNumber document_number,
PS.Name seller_State ,CS.Name buyer_State,PS.StateCode Seller_state_code ,CS.StateCode Buyer_state_code,
PD.Name Seller_location ,CD.Name Buyer_location,
P.GSTIN Seller_gstin,C.GSTIN Buyer_gstin, 
PA.Address seller_address1,PA.PIN seller_pincode,CA.Address Buyer_address1,PA.PIN buyer_pincode ,T_CreditDebitNotes.NoteType_id
FROM T_CreditDebitNotes 
join M_Parties P on P.id=T_CreditDebitNotes.Party_id
join M_Parties C on C.id=T_CreditDebitNotes.Customer_id
left join MC_PartyAddress PA on PA.Party_id=P.id and PA.IsDefault=1
left join MC_PartyAddress CA on CA.Party_id=C.id and CA.IsDefault=1
left join M_States PS on PS.id=P.State_id
left join M_States CS on CS.id=C.State_id
left join M_Districts PD on PD.id=P.District_id
left join M_Districts CD on  CD.id=C.District_id
where T_CreditDebitNotes.id=%s)a
left join 
(select sum(BasicAmount)Total_assessable_value,(sum(Amount))total_invoice_value,sum(CGST)total_cgst_value,
sum(SGST) total_sgst_value,sum(IGST)total_igst_value,sum(DiscountAmount)total_discount, CRDRNote_id 
from TC_CreditDebitNoteItems where CRDRNote_id=%s)b
on a.id=b.CRDRNote_id''',([id],[id])
)
                    InvoiceItem=TC_InvoiceItems.objects.raw('''SELECT 
(case when M_Items.id is null then M_CentralServiceItems.id else M_Items.id end )id ,
(case when M_Items.id is null then M_CentralServiceItems.Name else M_Items.Name end )ItemName ,
(case when M_Items.id is null then M_CentralServiceItems.HSNCode else M_GSTHSNCode.HSNCode end )HSNCode,
sum(Quantity) Quantity,M_Units.EwayBillUnit,TC_CreditDebitNoteItems.Rate,sum(TC_CreditDebitNoteItems.DiscountAmount)DiscountAmount,
sum(CGST)CGST,sum(SGST)SGST,sum(IGST)IGST,(sum(Quantity)* TC_CreditDebitNoteItems.Rate)total_amount,((sum(Quantity)* TC_CreditDebitNoteItems.Rate)-sum(DiscountAmount))assessable_value,TC_CreditDebitNoteItems.GSTPercentage gst_rate,
sum(Amount) total_item_value
FROM TC_CreditDebitNoteItems 
left join M_Items on TC_CreditDebitNoteItems.Item_id=M_Items.id
left join M_GSTHSNCode on M_GSTHSNCode.id=TC_CreditDebitNoteItems.GST_id
left join MC_ItemUnits on MC_ItemUnits.id=TC_CreditDebitNoteItems.Unit_id
left join M_Units on M_Units.id=MC_ItemUnits.UnitID_id
left join M_CentralServiceItems on M_CentralServiceItems.id=TC_CreditDebitNoteItems.ServiceItem_id


where CRDRNote_id=%s group by id,ItemName,HSNCode,M_Units.EwayBillUnit,TC_CreditDebitNoteItems.Rate,TC_CreditDebitNoteItems.GSTPercentage''',[id])
                    InvoiceUploadSerializer = CRDRNotegovUploadSerializer2(ItemQuery, many=True).data
                    Invoice=InvoiceUploadSerializer[0]
                    InvoiceItemUploadSerializer = InvoiceItemgovUploadSerializer2(InvoiceItem, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceItemUploadSerializer})

                    InvoiceData = list()
                    transaction_details = list()
                    document_details = list()
                    seller_details = list()
                    buyer_details = list()
                    dispatch_details = list()
                    ship_details = list()
                    reference_details = list()
                    document_period_details = list()
                    preceding_document_details = list()
                    value_details = list()
                    ewaybill_details = list()
                    InvoiceItemDetails = list()
                    
                    for a in InvoiceItemUploadSerializer:
                        q0=TC_CreditDebitNoteItems.objects.filter(CRDRNote_id=id ,Item_id=a['id']).values("BatchCode")
                          
                        Batchlist = list()
                        for d in q0:
                            Batchlist.append({
                                'name': "Batch-"+d['BatchCode']
                            })
                        InvoiceItemDetails.append({
                            'item_serial_number': a['id'],
                            'product_description': a['ItemName'],
                            'is_service': 'N',
                            'hsn_code': a['HSNCode'],
                            'quantity': a['Quantity'],
                            'unit': a['EwayBillUnit'],
                            'unit_price': a['Rate'],
                            'discount': a['DiscountAmount'],
                            'igst_amount': a['IGST'],
                            'cgst_amount': a['CGST'],
                            'sgst_amount': a['SGST'],
                            'total_amount':  round(float(a['Quantity'])*float(a['Rate']),2),
                            'assessable_value': round((float(a['Quantity'])*float(a['Rate']))-(float(a['DiscountAmount'])),2),
                            'gst_rate': a['gst_rate'],
                            'total_item_value': float(a['total_item_value']),
                            'batch_details': Batchlist
                        })

                    if Invoice['NoteType_id'] == 37 or Invoice['NoteType_id'] == 39:
                            document_type='CRN'
                            NoteType= 'CreditNote'
                    else:
                            document_type='DBN'  
                            NoteType= 'DebitNote'

                    transaction_details.append({
                        "supply_type": 'B2B'
                    }),
                    document_details.append({
                        'document_type': document_type,
                        'document_number': Invoice['document_number'],
                        'document_date': Invoice['document_date']
                    }),
                    seller_details.append({
                        'gstin': Invoice['Seller_gstin'],
                        'legal_name': Invoice['seller_legal_name'],
                        'address1': Invoice['seller_address1'][:100],
                        'location': Invoice['Seller_location'],
                        'pincode': Invoice['seller_pincode'],
                        'state_code': Invoice['seller_State']
                    }),
                    buyer_details.append({
                        'gstin': Invoice['Buyer_gstin'],
                        'legal_name': Invoice['Buyer_legal_name'],
                        'address1': Invoice['Buyer_address1'][:100],
                        'location': Invoice['Buyer_location'],
                        'pincode': Invoice['buyer_pincode'],
                        'place_of_supply': Invoice['Buyer_state_code'],
                        'state_code': Invoice['seller_State']
                    }),
                    dispatch_details.append({
                        'company_name': Invoice['seller_legal_name'],
                        'address1': Invoice['seller_address1'][:100],
                        'location': Invoice['Seller_location'],
                        'pincode': Invoice['seller_pincode'],
                        'state_code': Invoice['seller_State']
                    }),
                    ship_details.append({
                        'gstin': Invoice['Buyer_gstin'],
                        'legal_name': Invoice['Buyer_legal_name'],
                        'address1': Invoice['Buyer_address1'][:100],
                        'location': Invoice['Buyer_location'],
                        'pincode':Invoice['buyer_pincode'],
                        'state_code': Invoice['buyer_State']
                    }),
                    a= datetime.strptime(Invoice['document_date'], "%Y-%m-%d")
                    c = a+timedelta(days=1)

                    document_period_details.append({
                        'invoice_period_start_date': Invoice['document_date'],
                        # 'invoice_period_end_date': c.date()
                        'invoice_period_end_date': Invoice['document_date']
                    })
                    reference_details.append({
                        'document_period_details': document_period_details
                    }),

                    preceding_document_details.append({
                        'reference_of_original_invoice': Invoice['id'],
                        'preceding_invoice_date': Invoice['document_date']
                    }),
                    value_details.append({
                        'total_assessable_value': Invoice['Total_assessable_value'],
                        'total_invoice_value': Invoice['total_invoice_value'],
                        'total_cgst_value': Invoice['total_cgst_value'],
                        'total_sgst_value': Invoice['total_sgst_value'],
                        'total_igst_value': Invoice['total_igst_value'],
                        'total_discount': 0
                    }),
                    ewaybill_details.append({
                        'transportation_mode': 1,
                        'transportation_distance': 1
                    })

                    
                    InvoiceData.append({

                        "access_token": access_token,
                        "user_gstin": Invoice['Seller_gstin'],
                        "transaction_details": transaction_details[0],
                        "document_details": document_details[0],
                        "seller_details": seller_details[0],
                        "buyer_details": buyer_details[0],
                        "dispatch_details": dispatch_details[0],
                        "ship_details": ship_details[0],
                        "reference_details": reference_details[0],
                        "preceding_document_details": preceding_document_details[0],
                        "value_details": value_details[0],
                        "ewaybill_details": ewaybill_details[0],
                        "item_list": InvoiceItemDetails
                    })
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': '', 'Data': InvoiceData[0]})
                    EInvoice_URL = 'https://pro.mastersindia.co/generateEinvoice'
                    payload1 = json.dumps(InvoiceData[0])
                    # payload = json.loads(payload1)
                    headers = {
                        'Content-Type': 'application/json',
                    }
                   
                    response = requests.request(
                        "POST", EInvoice_URL, headers=headers, data=payload1)
                    
                    data_dict = json.loads(response.text)
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': data_dict['results']['status'], 'Data': InvoiceData[0]})
                    if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                        Query=TC_CreditDebitNoteUploads.objects.filter(CRDRNote_id=id)
                       
                        if(Query.count() > 0):
                            
                            StatusUpdates=TC_CreditDebitNoteUploads.objects.filter(CRDRNote=id).update(Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': NoteType +' E-Invoice Upload Successfully', 'Data': [] })
                        else:
                           
                            InvoiceID=T_CreditDebitNotes.objects.get(id=id)
                            Statusinsert=TC_CreditDebitNoteUploads.objects.create(CRDRNote=InvoiceID,user_gstin=Invoice['Seller_gstin'],Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())        
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': NoteType +' E-Invoice Upload Successfully', 'Data': [] })
                    else:
                        
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['errorMessage'], 'Data': InvoiceData[0] })
                    
                else:
                    
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

#==========================================================================================================================
class Cancel_CreditDebitNotes_EInvoice(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0):
        try:
            with transaction.atomic():

                access_token = generate_Access_Token()
                aa=access_token.split('!')
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
# =======================================================================================
                invoicedetaillist=list()
                if(aa[0] == '1'):
                    access_token=aa[1]
                    InvoiceUploadsData=TC_CreditDebitNoteUploads.objects.filter(CRDRNote_id=id).values("user_gstin","Irn")
                   
                    invoicedetaillist.append({
                            "access_token" : access_token,
                            "user_gstin" : InvoiceUploadsData[0]["user_gstin"],
                            "irn" : InvoiceUploadsData[0]["Irn"],
                            "cancel_reason" : "2",
                            "cancel_remarks" : "Data Entry Mistake"

                    })
                    EInvoiceCancel_URL = 'https://pro.mastersindia.co/cancelEinvoice'
                    payload = json.dumps(invoicedetaillist[0])
                    
                    headers = {
                        'Content-Type': 'application/json',
                    }

                    response = requests.request(
                        "POST", EInvoiceCancel_URL, headers=headers, data=payload)

                    data_dict = json.loads(response.text)
                    
                    if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                        Query=TC_CreditDebitNoteUploads.objects.filter(CRDRNote_id=id)
                        
                        if(Query.count() > 0):
                            
                            StatusUpdates=TC_CreditDebitNoteUploads.objects.filter(CRDRNote_id=id).update(EInvoiceIsCancel=1,EInvoiceCanceledBy=userID,EInvoiceCanceledOn=datetime.now())
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Cancel Successfully', 'Data': [] })
                        else:
                              
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Data Invalid', 'Data': [] })
                    else:
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['errorMessage'], 'Data': [] })
                else:
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})            
