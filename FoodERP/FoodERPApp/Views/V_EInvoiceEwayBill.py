import json
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from ..Serializer.S_EInvoiceEwayBill import InvoicegovUploadSerializer


from ..Serializer.S_Orders import *
from ..models import *
import requests
import json
from datetime import datetime


def generate_Access_Token():
    Auth_URL = "https://pro.mastersindia.co/oauth/access_token"
    dataArray = {
        "username": "a.kiranmali@gmail.com",
        "password": "Kiran@123",
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
    def get(self, request, id=0,userID=0):
        try:
            with transaction.atomic():

                access_token = generate_Access_Token()
                aa=access_token.split('!')
                # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
# =======================================================================================
                
                if(aa[0] == '1'):
                    
                    access_token=aa[1]
                    ItemQuery = T_Invoices.objects.filter(id=id)
                    InvoiceUploadSerializer = InvoicegovUploadSerializer(
                        ItemQuery, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceUploadSerializer})

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
                    Total_assessable_value = 0
                    total_invoice_value = 0
                    total_cgst_value = 0
                    total_sgst_value = 0
                    total_igst_value = 0
                    total_discount = 0
                    for Invoice in InvoiceUploadSerializer:
                        user_gstin=Invoice['Party']['GSTIN']
                        for a in Invoice['InvoiceItems']:

                            assessable_value = float(a['BasicAmount'])
                            Total_assessable_value = float(
                                Total_assessable_value + assessable_value)
                            total_invoice_value = float(
                                total_invoice_value) + (float(a['Amount'])-float(a['DiscountAmount']))
                            total_cgst_value = float(
                                total_cgst_value) + float(a['CGST'])
                            total_sgst_value = float(
                                total_sgst_value) + float(a['SGST'])
                            total_igst_value = float(
                                total_igst_value) + float(a['IGST'])
                            total_discount = float(
                                total_discount) + float(a['DiscountAmount'])

                            Batchlist = list()
                            Batchlist.append({
                                'name': "Batch-"+a['BatchCode']
                            })
                            InvoiceItemDetails.append({
                                'item_serial_number': a['Item']['id'],
                                'product_description': a['Item']['Name'],
                                'is_service': 'N',
                                'hsn_code': a['GST']['HSNCode'],
                                'quantity': a['Quantity'],
                                'unit': a['Unit']['UnitID']['EwayBillUnit'],
                                'unit_price': a['Rate'],
                                'discount': a['DiscountAmount'],
                                'igst_amount': a['IGST'],
                                'cgst_amount': a['CGST'],
                                'sgst_amount': a['SGST'],
                                'total_amount':  round(float(a['Quantity'])*float(a['Rate']),2),
                                'assessable_value': round((float(a['Quantity'])*float(a['Rate']))-(float(a['DiscountAmount'])),2),
                                'gst_rate': a['GST']['GSTPercentage'],
                                'total_item_value': float(a['Amount']),
                                'batch_details': Batchlist
                            })

                    for address in Invoice['Party']['PartyAddress']:
                        if address['IsDefault'] == 1:
                            selleraddress = address['Address']
                            sellerpin = address['PIN']

                    for address in Invoice['Customer']['PartyAddress']:
                        if address['IsDefault'] == 1:
                            buyeraddress = address['Address']
                            buyerpin = address['PIN']

                    transaction_details.append({
                        "supply_type": 'B2B'
                    }),
                    document_details.append({
                        'document_type': 'INV',
                        'document_number': Invoice['id'],
                        'document_date': Invoice['InvoiceDate']
                    }),
                    seller_details.append({
                        'gstin': Invoice['Party']['GSTIN'],
                        'legal_name': Invoice['Party']['Name'],
                        'address1': selleraddress,
                        'location': Invoice['Party']['District']['Name'],
                        'pincode': sellerpin,
                        'state_code': Invoice['Party']['State']['Name']
                    }),
                    buyer_details.append({
                        'gstin': Invoice['Customer']['GSTIN'],
                        'legal_name': Invoice['Customer']['Name'],
                        'address1': buyeraddress,
                        'location': Invoice['Customer']['District']['Name'],
                        'pincode': buyerpin,
                        'place_of_supply': Invoice['Customer']['State']['StateCode'],
                        'state_code': Invoice['Customer']['State']['StateCode']
                    }),
                    dispatch_details.append({
                        'company_name': Invoice['Party']['Name'],
                        'address1': selleraddress,
                        'location': Invoice['Party']['District']['Name'],
                        'pincode': sellerpin,
                        'state_code': Invoice['Customer']['State']['Name']
                    }),
                    ship_details.append({
                        'gstin': Invoice['Customer']['GSTIN'],
                        'legal_name': Invoice['Customer']['Name'],
                        'address1': buyeraddress,
                        'location': Invoice['Customer']['District']['Name'],
                        'pincode': buyerpin,
                        'state_code': Invoice['Customer']['State']['Name']
                    }),

                    document_period_details.append({
                        'invoice_period_start_date': Invoice['InvoiceDate'],
                        'invoice_period_end_date': Invoice['InvoiceDate']
                    })
                    reference_details.append({
                        'document_period_details': document_period_details
                    }),

                    preceding_document_details.append({
                        'reference_of_original_invoice': Invoice['id'],
                        'preceding_invoice_date': Invoice['InvoiceDate']
                    }),
                    value_details.append({
                        'total_assessable_value': round(Total_assessable_value, 2),
                        'total_invoice_value': round(total_invoice_value, 2),
                        'total_cgst_value': round(total_cgst_value, 2),
                        'total_sgst_value': round(total_sgst_value, 2),
                        'total_igst_value': round(total_igst_value, 2),
                        'total_discount': round(total_discount, 2)
                    }),
                    ewaybill_details.append({
                        'transportation_mode': 1,
                        'transportation_distance': 1
                    })

                    
                    InvoiceData.append({

                        "access_token": access_token,
                        "user_gstin": Invoice['Party']['GSTIN'],
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
                    
                    EInvoice_URL = 'https://pro.mastersindia.co/generateEinvoice'
                    payload1 = json.dumps(InvoiceData[0])
                    # payload = json.loads(payload1)
                    headers = {
                        'Content-Type': 'application/json',
                    }

                    response = requests.request(
                        "POST", EInvoice_URL, headers=headers, data=payload1)
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'aa[1]', 'Data': InvoiceData[0]})
                    data_dict = json.loads(response.text)
                    
                    if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                        Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                        
                        if(Query.count() > 0):
                            
                            StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())
                        else:
                            InvoiceID=T_Invoices.objects.get(id=id)
                            Statusinsert=TC_InvoiceUploads.objects.create(Invoice=InvoiceID,user_gstin=user_gstin,Irn=data_dict['results']['message']['Irn'],AckNo=data_dict['results']['message']['AckNo'],EInvoicePdf=data_dict['results']['message']['EinvoicePdf'],QRCodeUrl=data_dict['results']['message']['QRCodeUrl'],EInvoiceCreatedBy=userID,EInvoiceCreatedOn=datetime.now())        
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Upload Successfully', 'Data': [] })
                    else:
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['errorMessage'], 'Data': InvoiceData[0] })
                    
                else:
                    
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class Uploaded_EwayBill(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,userID=0):
        try:
            with transaction.atomic():
                Query=T_Invoices.objects.filter(id=id).values('Vehicle')
                if (Query[0]['Vehicle']) is None:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message': 'Vehicle Number is required', 'Data':id })
                else:
                    print('bbbbbbbbbb')
                    access_token = generate_Access_Token()
                    aa=access_token.split('!')
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': access_token})
    # =======================================================================================
                    
                    if(aa[0] == '1'):
                        print('ccccccccccc')
                        access_token=aa[1]
                        ItemQuery = T_Invoices.objects.filter(id=id)
                        InvoiceUploadSerializer = InvoicegovUploadSerializer(
                            ItemQuery, many=True).data
                        # return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': InvoiceUploadSerializer})
                        print('qqqqqqqqqqq')
                        InvoiceData = list()
                        InvoiceItemDetails = list()
                        Total_assessable_value = 0
                        total_invoice_value = 0
                        total_cgst_value = 0
                        total_sgst_value = 0
                        total_igst_value = 0
                        total_discount = 0
                        for Invoice in InvoiceUploadSerializer:
                            user_gstin=Invoice['Party']['GSTIN']
                            print('wwwwwwwwwwwwww')
                            for a in Invoice['InvoiceItems']:

                                # assessable_value=float(a['Quantity'])*float(a['Rate'])
                                Total_assessable_value = float(
                                    Total_assessable_value) + float(a['BasicAmount'])
                                total_invoice_value = float(
                                    total_invoice_value) + float(a['Amount'])
                                total_cgst_value = float(
                                    total_cgst_value) + float(a['CGST'])
                                total_sgst_value = float(
                                    total_sgst_value) + float(a['SGST'])
                                total_igst_value = float(
                                    total_igst_value) + float(a['IGST'])
                                total_discount = float(
                                    total_discount) + float(a['DiscountAmount'])

                                InvoiceItemDetails.append({
                                    "product_name": a['Item']['Name'],
                                    "product_description": a['Item']['Name'],
                                    "hsn_code": a['GST']['HSNCode'],
                                    "quantity": a['Quantity'],
                                    "unit_of_product": a['Unit']['UnitID']['EwayBillUnit'],
                                    "cgst_rate": a['SGSTPercentage'],
                                    "sgst_rate": a['SGSTPercentage'],
                                    "igst_rate": a['SGSTPercentage'],
                                    "cess_rate": 0,
                                    "cessNonAdvol": 0,
                                    "taxable_amount": a['BasicAmount'],
                                })

                            for address in Invoice['Party']['PartyAddress']:
                                if address['IsDefault'] == 1:
                                    selleraddress = address['Address']
                                    sellerpin = address['PIN']

                            for address in Invoice['Customer']['PartyAddress']:
                                if address['IsDefault'] == 1:
                                    buyeraddress = address['Address']
                                    buyerpin = address['PIN']

                            InvoiceData.append({

                                'access_token': access_token,
                                'userGstin': Invoice['Party']['GSTIN'],
                                'supply_type': "outward",
                                'sub_supply_type': "Supply",
                                'sub_supply_description': " ",
                                'document_type': "TaxInvoice",
                                'document_number': Invoice['id'],
                                'document_date': Invoice['InvoiceDate'],
                                'gstin_of_consignor': Invoice['Party']['GSTIN'],
                                'legal_name_cosignor': Invoice['Party']['Name'],
                                'address1_of_consignor': selleraddress,
                                'address2_of_consignor': '',
                                'pincode_of_consignor': sellerpin,
                                'state_of_consignor': Invoice['Party']['State']['Name'],
                                'actual_from_state_name': Invoice['Party']['State']['Name'],
                                'gstin_of_consignee': Invoice['Customer']['GSTIN'],
                                'legal_name_of_consignee': Invoice['Customer']['Name'],
                                'address1_of_consignee': buyeraddress,
                                'address2_of_consignee': "",
                                'place_of_consignee': Invoice['Customer']['City']['Name'],
                                'pincode_of_consignee': buyerpin,
                                'state_of_supply': Invoice['Customer']['State']['Name'],
                                'actual_to_state_name': Invoice['Customer']['State']['Name'],
                                'other_value': '0',
                                'total_invoice_value': Invoice['GrandTotal'],
                                'taxable_amount': Total_assessable_value,
                                'cgst_amount': total_cgst_value,
                                'sgst_amount': total_sgst_value,
                                'igst_amount': total_igst_value,
                                'cess_amount': '0',
                                'cess_nonadvol_value': '0',
                                'transporter_id': "",
                                'transporter_document_number': "",
                                'transporter_document_date': "",
                                'transportation_mode': "road",
                                'transportation_distance': "1",
                                'vehicle_number': Invoice['Vehicle']['VehicleNumber'],
                                'transporter_name': "",
                                'vehicle_type': "Regular",
                                'data_source': "erp",
                                'user_ref': "1232435466sdsf234",
                                'eway_bill_status': "Y",
                                'auto_print': "Y",
                                'email' : Invoice['Party']['Email'],
                                'itemList': InvoiceItemDetails
                            })
                            print('ddddddddddddd')
                            E_Way_Bill_URL = 'https://pro.mastersindia.co/ewayBillsGenerate'
                            payload = json.dumps(InvoiceData[0])
                            
                            headers = {
                                'Content-Type': 'application/json',
                            }
                            print('eeeeeeeeeeee')
                            response = requests.request(
                                "POST", E_Way_Bill_URL, headers=headers, data=payload)

                            data_dict = json.loads(response.text)
                            print('ffffffffffffff')
                            if(data_dict['results']['status']== 'Success' and data_dict['results']['code']== 200):
                                Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                                
                                if(Query.count() > 0):
                                    
                                    StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())
                                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Upload Successfully', 'Data': [] })
                                else:
                                    InvoiceID=T_Invoices.objects.get(id=id)
                                    Statusinsert=TC_InvoiceUploads.objects.create(Invoice=InvoiceID,user_gstin=user_gstin,EwayBillUrl=data_dict['results']['message']['url'],EwayBillNo=data_dict['results']['message']['ewayBillNo'],EwayBillCreatedBy=userID,EwayBillCreatedOn=datetime.now())        
                                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Upload Successfully', 'Data': [] })
                            else:
                                return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['errorMessage'], 'Data': [] })
                    else:
                        return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class Cancel_EwayBill(CreateAPIView):
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
                    InvoiceUploadsData=TC_InvoiceUploads.objects.filter(Invoice=id).values("user_gstin","EwayBillNo")
                  
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
                        Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                        
                        if(Query.count() > 0):
                            
                            StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EwayBillIsCancel=1,EwayBillCanceledBy=userID,EwayBillCanceledOn=datetime.now())
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Cancel Successfully', 'Data': [] })
                        else:
                              
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-WayBill Data Invalid', 'Data': [] })
                    else:
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['message'], 'Data': [] })
                else:
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class Cancel_EInvoice(CreateAPIView):
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
                    InvoiceUploadsData=TC_InvoiceUploads.objects.filter(Invoice=id).values("user_gstin","Irn")
                   
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
                        Query=TC_InvoiceUploads.objects.filter(Invoice_id=id)
                        
                        if(Query.count() > 0):
                            
                            StatusUpdates=TC_InvoiceUploads.objects.filter(Invoice=id).update(EInvoiceIsCancel=1,EInvoiceCanceledBy=userID,EInvoiceCanceledOn=datetime.now())
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Cancel Successfully', 'Data': [] })
                        else:
                              
                            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'E-Invoice Data Invalid', 'Data': [] })
                    else:
                        return JsonResponse({'StatusCode': data_dict['results']['code'], 'Status': True, 'Message': data_dict['results']['errorMessage'], 'Data': [] })
                else:
                    return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': aa[1], 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
