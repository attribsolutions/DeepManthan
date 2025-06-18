from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Views.V_TransactionNumberfun import GetMaxNumber, GetPrifix
from ..Serializer.S_CreditDebit import *
from django.db.models import Sum
from ..models import *
########## Plain Credit Debit Note ########################################################

class CreditDebitNoteListView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        CreditDebitdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                FromDate = CreditDebitdata['FromDate']
                ToDate = CreditDebitdata['ToDate']
                Customer = CreditDebitdata['CustomerID']
                Party = CreditDebitdata['PartyID']
                NoteType = CreditDebitdata['NoteType']
                Note = CreditDebitdata['Note']
                

                if Note == "Credit":
                    if NoteType == '':
                        P=Q(NoteType_id__in=(37,39))
                    else:
                        P=Q(NoteType=NoteType)    
                        
                else:
                    if NoteType == '':
                        P=Q(NoteType_id__in=(38,40))
                    else:
                        P=Q(NoteType=NoteType)
                            
                if(Customer == ''):
                    query = T_CreditDebitNotes.objects.filter(CRDRNoteDate__range=[FromDate, ToDate], Party=Party).filter(P)
                else:
                    query = T_CreditDebitNotes.objects.filter(CRDRNoteDate__range=[FromDate, ToDate], Customer=Customer, Party=Party).filter(P)

                if query:
                    CreditDebit_serializer = CreditDebitNoteSecondSerializer(
                        query, many=True).data
                    CreditDebitListData = list()
                    for a in CreditDebit_serializer:
                        CreditDebitListData.append({
                            "id": a['id'],
                            "CRDRNoteDate": a['CRDRNoteDate'],
                            "NoteNo": a['NoteNo'],
                            "FullNoteNumber": a['FullNoteNumber'],
                            "NoteType": a['NoteType']['Name'],
                            "NoteReason": a['NoteReason']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "Narration": a['Narration'],
                            "CreatedOn": a['CreatedOn'],
                            "IsRecordDeleted" : a["IsDeleted"],
                            "CRDRNoteUploads" : a["CRDRNoteUploads"],
                            "ImportFromExcel" : a["ImportFromExcel"]
                        })
                    #for log
                    if Customer == '':
                        Customer = 0
                    else:
                        Customer = Customer
                    log_entry = create_transaction_logNew(request, CreditDebitdata,Party,'From:'+FromDate+','+'To:'+ToDate,83,0,FromDate,ToDate,Customer)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CreditDebitListData})
                log_entry = create_transaction_logNew(request, CreditDebitdata, Party,'CreditDebitList Not Available',83,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, CreditDebitdata, 0,'CreditDebitList:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class CreditDebitNoteView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        CreditNotedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Party = CreditNotedata['Party']
                CRDRNoteDate = CreditNotedata['CRDRNoteDate']
                NoteType = CreditNotedata['NoteType']
                # ==========================Get Max Credit Debit  Number=====================================================
                a = GetMaxNumber.GetCreditDebitNumber(
                    Party, NoteType, CRDRNoteDate)
                CreditNotedata['NoteNo'] = a
                '''Get  Credit Debit Prifix '''
                b = GetPrifix.GetCRDRPrifix(Party, NoteType)
                CreditNotedata['FullNoteNumber'] = str(b)+""+str(a)
                # ==================================================================================================
                CRDRNoteItems = CreditNotedata['CRDRNoteItems']
                for CRDRNoteItem in CRDRNoteItems:
                       
                    if CRDRNoteItem['Item'] is None:
                        CRDRNoteItem['BaseUnitQuantity'] =0
                        CRDRNoteItem['QtyInNo'] =0
                        CRDRNoteItem['QtyInKg'] =0
                        CRDRNoteItem['QtyInBox'] =0
                    else:

                        BaseUnitQuantity=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,0,0).GetBaseUnitQuantity()
                        CRDRNoteItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                        QtyInNo=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                        CRDRNoteItem['QtyInNo'] =  float(QtyInNo)
                        QtyInKg=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                        CRDRNoteItem['QtyInKg'] =  float(QtyInKg)
                        QtyInBox=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                        CRDRNoteItem['QtyInBox'] = float(QtyInBox)
                
                CreditNote_Serializer = CreditDebitNoteSerializer(
                    data=CreditNotedata)
                if CreditNote_Serializer.is_valid():
                    CreditDebit = CreditNote_Serializer.save()
                    LastInsertID = CreditDebit.id
                    if(NoteType==37 or NoteType==39):
                        log_entry = create_transaction_logNew(request, CreditNotedata, Party,'CRDRNoteDate:'+CreditNotedata['CRDRNoteDate']+','+'TransactionID:'+str(LastInsertID),84,LastInsertID,0,0,CreditNotedata['Customer'])
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CreditNote Save Successfully', 'TransactionID':LastInsertID, 'Data': []})
                    else:
                        log_entry = create_transaction_logNew(request, CreditNotedata, Party,'CRDRNoteDate:'+CreditNotedata['CRDRNoteDate']+','+'TransactionID:'+str(LastInsertID),197,LastInsertID,0,0,CreditNotedata['Customer'])
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'DebitNote Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, CreditNotedata, Party,'CreditDebitNoteSave:'+str(CreditNote_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CreditNote_Serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, CreditNotedata, 0,'CreditDebitNoteSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_CreditDebitNotes.objects.filter(id=id)
               
                if query:
                    CreditDebitNote_serializer = SingleCreditDebitNoteThirdSerializer(query,many=True).data
                    CreditDebitListData = list()
                    # return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': CreditDebitNote_serializer})
                    for a in CreditDebitNote_serializer:
                        CRDRNoteItems = list()
                        for b in a['CRDRNoteItems']:
                                  
                            if b['ServiceItem']['id'] is None:
                                ItemId= b['Item']['id']
                                ItemName=b['Item']['Name']
                                HSNCode =b['GST']['HSNCode']
                            else:
                                ItemId=b['ServiceItem']['id']
                                ItemName=b['ServiceItem']['Name']
                                HSNCode = b['ServiceItem']['HSNCode']
                            
                            
                            CRDRNoteItems.append({
                                "Item": ItemId,
                                "ItemName": ItemName,
                                "HSNCode":HSNCode,
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
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
                                "BatchCode": b['BatchCode'],
                                "BatchDate": b['BatchDate'],
                                "GSTPercentage": b['GSTPercentage'],
                                "MRPValue": b['MRPValue'],
                                "Discount": b['Discount'],
                                "DiscountAmount": b['DiscountAmount'],
                                "DiscountType": b['DiscountType'],
                                "QtyInNo": b['QtyInNo'],
                                "QtyInKg": b['QtyInKg'],
                                "QtyInBox": b['QtyInBox'],
                                "ItemComment":b['ItemComment']
                                
                            }) 
                        
                        CRDRInvoices = list()
                        for c in a['CRDRInvoices']:
                            CRDRInvoices.append({
                                "id":c['id'],
                                "GrandTotal": c['GrandTotal'],
                                "PaidAmount": c['PaidAmount'],
                                "AdvanceAmtAdjusted":c['AdvanceAmtAdjusted'],
                                "InvoiceDate": c['Invoice']['InvoiceDate'],
                                "FullInvoiceNumber": c['Invoice']['FullInvoiceNumber'],
                                "CreatedOn": c['Invoice']['CreatedOn']
                            }) 
                        
                        DefCustomerAddress = ''  
                        for ad in a['Customer']['PartyAddress']:
                            if ad['IsDefault'] == True :
                                DefCustomerAddress = ad['Address']
                                
                        DefPartyAddress = ''
                        for x in a['Party']['PartyAddress']:
                            if x['IsDefault'] == True :
                                DefPartyAddress = x['Address']
                            
                        CreditDebitListData.append({
                            "id": a['id'],
                            "CRDRNoteDate": a['CRDRNoteDate'],
                            "NoteNo": a['NoteNo'],
                            "FullNoteNumber": a['FullNoteNumber'],
                            "NoteType": a['NoteType']['Name'],
                            "NoteReason": a['NoteReason']['Name'],
                            "GrandTotal": a['GrandTotal'],
                            "RoundOffAmount": a['RoundOffAmount'],
                            "CustomerID": a['Customer']['id'],
                            "Customer": a['Customer']['Name'],
                            "CustomerGSTIN": a['Customer']['GSTIN'],
                            "CustomerFSSAINo": a['Customer']['PartyAddress'][0]['FSSAINo'],
                            "CustomerState": a['Customer']['State']['Name'],
                            "CustomerAddress": DefCustomerAddress,
                            "PartyID": a['Party']['id'],
                            "Party": a['Party']['Name'],
                            "PartyGSTIN": a['Party']['GSTIN'],
                            "PartyFSSAINo": a['Party']['PartyAddress'][0]['FSSAINo'],
                            "PartyState": a['Party']['State']['Name'],
                            "PartyAddress": DefPartyAddress,                            
                            "Narration": a['Narration'],
                            "CreatedOn": a['CreatedOn'],
                            "CRDRNoteItems":CRDRNoteItems,
                            "CRDRInvoices": CRDRInvoices,
                            "CRDRNoteUploads" : a["CRDRNoteUploads"]
                        })

                if query:                   
                    log_entry = create_transaction_logNew(request, {'CreditDebitNoteID':id}, a['Party']['id'],'',85,0,0,0,a['Customer']['id'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CreditDebitListData[0]})
                log_entry = create_transaction_logNew(request, {'CreditDebitNoteID':id}, 0,'Record Not Found',29,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'Single CreditdebitNote:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():

                query = T_CreditDebitNotes.objects.filter(id=id).values('NoteType')
                NoteType = query[0]['NoteType']
                CreditDebitdata = T_CreditDebitNotes.objects.filter(id=id).update(IsDeleted=1)
                if(NoteType==37 or NoteType==39):
                    log_entry = create_transaction_logNew(request, {'CreditDebitNoteID':id}, 0,'',86,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CreditNote Deleted Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, {'CreditDebitNoteID':id}, 0,'',86,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'DebitNote Deleted Successfully', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, {'CreditDebitNoteID':id}, 0,'',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'CreditdebitNote used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'CreditDebitNoteDelete:'+ str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class CreditDebitNoteExcelView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        CreditNotedata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                queryaa=T_CreditDebitNotes.objects.filter(CRDRNoteDate=CreditNotedata['BulkData'][0]['CRDRNoteDate'],Party=CreditNotedata['BulkData'][0]['Party'],ImportFromExcel=CreditNotedata['BulkData'][0]['ImportFromExcel'])
                # queryaa=T_CreditDebitNotes.objects.filter(CRDRNoteDate=CreditNotedata['BulkData'][0]['CRDRNoteDate'],Party=CreditNotedata['BulkData'][0]['Party'] ,IsDeleted=0)
                if queryaa:
                    log_entry = create_transaction_logNew(request, CreditNotedata, 0,'CRDRNoteUpload:'+str('CreditNote data has already been uploaded for the date '+ CreditNotedata['BulkData'][0]['CRDRNoteDate']),379,0)
                    return JsonResponse({'StatusCode': 226, 'Status': True,  'Message': 'CreditNote data has already been uploaded for the date '+ CreditNotedata['BulkData'][0]['CRDRNoteDate'] , 'Data':[]})
                else:
                
                    for aa in CreditNotedata['BulkData']:
                        aa["NoteNo"]=0
                        aa["ImportFromExcel"] =1
                        Party = aa['Party']
                        CRDRNoteDate = aa['CRDRNoteDate']
                        NoteType = aa['NoteType']

                        checkduplicate=T_CreditDebitNotes.objects.filter(FullNoteNumber=aa['FullNoteNumber'] ,Party=aa['Party'])
                        if checkduplicate:
                            
                            return JsonResponse({'StatusCode': 226, 'Status': True,  'Message': 'CreditNote No : '+ str(aa['FullNoteNumber']) +' already Uploaded ', 'Data':[]})
                        else:
                            
                            CRDRNoteItems = aa['CRDRNoteItems']
                            for CRDRNoteItem in CRDRNoteItems:
                                
                                UnitMapping=M_UnitMappingMaster.objects.filter(MapUnit=CRDRNoteItem['Unit'],Party=aa['Party']).values("Unit")
                                if UnitMapping.count() > 0:
                                    
                                    MC_UnitID=MC_ItemUnits.objects.filter(UnitID=UnitMapping[0]["Unit"],Item=CRDRNoteItem["Item"],IsDeleted=0).values("id")
                                    
                                    CRDRNoteItem['Unit']=MC_UnitID[0]['id']
                                    
                                    if MC_UnitID.count() > 0:    
                                        
                                        BaseUnitQuantity=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,0,0).GetBaseUnitQuantity()
                                        CRDRNoteItem['BaseUnitQuantity'] =  round(BaseUnitQuantity,3) 
                                        QtyInNo=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,1,0).ConvertintoSelectedUnit()
                                        CRDRNoteItem['QtyInNo'] =  float(QtyInNo)
                                        QtyInKg=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,2,0).ConvertintoSelectedUnit()
                                        CRDRNoteItem['QtyInKg'] =  float(QtyInKg)
                                        QtyInBox=UnitwiseQuantityConversion(CRDRNoteItem['Item'],CRDRNoteItem['Quantity'],CRDRNoteItem['Unit'],0,0,4,0).ConvertintoSelectedUnit()
                                        CRDRNoteItem['QtyInBox'] = float(QtyInBox)
                                    else : 
                                        # log_entry = create_transaction_logNew(request, CreditNotedata, 0, " MC_ItemUnits Data Mapping Missing",39,0)
                                        return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " MC_ItemUnits Data Mapping Missing", 'Data':[]})
                                else:
                                    # log_entry = create_transaction_logNew(request, CreditNotedata, 0, "Unit Data Mapping Missing",40,0)
                                    return JsonResponse({'StatusCode': 406, 'Status': True,  'Message': " Unit Data Mapping Missing", 'Data':[]})
                            
                            CreditNote_Serializer = CreditDebitNoteExcelSerializer(data=aa)
                            if CreditNote_Serializer.is_valid():
                                CreditDebit = CreditNote_Serializer.save()
                                
                            else:
                                log_entry = create_transaction_logNew(request, CreditNotedata, Party,'CreditDebitNoteSave:'+str(CreditNote_Serializer.errors),34,0)
                                transaction.set_rollback(True)
                                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CreditNote_Serializer.errors, 'Data': []})
                    log_entry = create_transaction_logNew(request, CreditNotedata, Party,'CRDRNoteDate:'+aa['CRDRNoteDate'],84,0,0,0,aa['Customer'])
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CreditNote Data Upload Successfully', 'Data': []})
        except Exception as e:
            
            log_entry = create_transaction_logNew(request,CreditNotedata, 0,'CreditDebitNoteSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})                  


    @transaction.atomic()
    def delete(self, request):
        CreditNote_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
               
                CreditNote_ids = CreditNote_data.get('CreditNote_ID', '').split(',')
                
                if not CreditNote_ids:
                    log_entry = create_transaction_logNew(request, CreditNote_data, 0,'No Invoice IDs provided',352,0)
                    return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'No CreditNote IDs provided', 'Data': []})
                
                T_CreditDebitNotes.objects.filter(id__in=CreditNote_ids).delete()
                log_entry = create_transaction_logNew(request, CreditNote_data, 0,f'CreditNote_ID: {CreditNote_ids}Deleted Successfully',352,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bulk CreditNote Delete Successfully', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'CreditNoteIDs used in another table',8,0)     
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, CreditNote_data,0,'CreditNoteIDsNotDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})