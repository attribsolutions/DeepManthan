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
        try:
            with transaction.atomic():
                CreditDebitdata = JSONParser().parse(request)
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

                print(str(query.query))
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
                            "Receipt": a['Receipt']['FullReceiptNumber'],
                            "Invoice": a['Invoice']['FullInvoiceNumber'],
                            "PurchaseReturn": a['PurchaseReturn']['FullReturnNumber'],
                            "CreatedOn": a['CreatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CreditDebitListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


class CreditDebitNoteView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                CreditNotedata = JSONParser().parse(request)
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

                CreditNote_Serializer = CreditDebitNoteSerializer(
                    data=CreditNotedata)
                if CreditNote_Serializer.is_valid():
                    CreditNote_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CreditdebitNote Save Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': CreditNote_Serializer.errors, 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

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
                            CRDRNoteItems.append({
                                "Item": b['Item']['id'],
                                "ItemName": b['Item']['Name'],
                                "Quantity": b['Quantity'],
                                "MRP": b['MRP']['id'],
                                "MRPValue": b['MRP']['MRP'],
                                "Rate": b['Rate'],
                                "TaxType": b['TaxType'],
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BaseUnitQuantity": b['BaseUnitQuantity'],
                                "GST": b['GST']['id'],
                                "GSTPercentage": b['GST']['GSTPercentage'],
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
                            "CRDRInvoices": CRDRInvoices 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': CreditDebitListData[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                CreditDebitdata = T_CreditDebitNotes.objects.get(id=id)
                CreditDebitdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'CreditdebitNote Deleted Successfully', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'CreditdebitNote used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

