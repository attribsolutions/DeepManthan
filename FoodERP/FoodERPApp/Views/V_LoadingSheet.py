from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_LoadingSheet import *
from ..models import *



class LoadingSheetListView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Loadingsheet_data = JSONParser().parse(request)
                Party = Loadingsheet_data['Party']
                Routequery = T_LoadingSheet.objects.filter(Party=Party)
                if Routequery.exists():
                    Loadingsheet_Serializer = LoadingSheetSerializer(Routequery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': Loadingsheet_Serializer})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Not available', 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



class LoadingSheetView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Loadingsheet_data = JSONParser().parse(request)
                Loadingsheet_Serializer = LoadingSheetSerializer(data=Loadingsheet_data)
                if Loadingsheet_Serializer.is_valid():
                    Loadingsheet_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Loadingsheet_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Loadingsheetquery = T_LoadingSheet.objects.filter(id=id)
                if Loadingsheetquery.exists():
                    LoadingSheetdata = LoadingSheetSerializer(Loadingsheetquery, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': LoadingSheetdata})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Loading Sheet Not available ', 'Data': []})
        except M_Routes.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Loading Sheet Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Loadingsheetdata = JSONParser().parse(request)
                LoadingsheetdataByID = T_LoadingSheet.objects.get(id=id)
                Loadingsheet_Serializer = LoadingSheetSerializer(LoadingsheetdataByID, data=Loadingsheetdata)
                if Loadingsheet_Serializer.is_valid():
                    Loadingsheet_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Loadingsheet_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Loadingsheetdata = T_LoadingSheet.objects.get(id=id)
                Loadingsheetdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Loading Sheet Deleted Successfully', 'Data':[]})
        except T_LoadingSheet.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Loading Sheet Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Loading Sheet used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
  
class LoadingSheetInvoicesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                FromDate = Invoicedata['FromDate']
                ToDate = Invoicedata['ToDate']
                Party = Invoicedata['Party']
                Route = Invoicedata['Route']
                
                if(Route == ''):
                    query =  T_Invoices.objects.raw('''SELECT t_invoices.id as id, t_invoices.InvoiceDate, t_invoices.Customer_id, t_invoices.FullInvoiceNumber, t_invoices.GrandTotal, t_invoices.Party_id, t_invoices.CreatedOn,  t_invoices.UpdatedOn, m_parties.Name FROM t_invoices join m_parties on  m_parties.id=  t_invoices.Customer_id WHERE t_invoices.InvoiceDate BETWEEN %s AND %s AND t_invoices.Party_id = %s ''',[FromDate,ToDate,Party])
                else:
                    query =  T_Invoices.objects.raw('''SELECT t_invoices.id as id, t_invoices.InvoiceDate, t_invoices.Customer_id, t_invoices.FullInvoiceNumber, t_invoices.GrandTotal, t_invoices.Party_id, t_invoices.CreatedOn, t_invoices.UpdatedOn,m_parties.Name FROM t_invoices join m_parties on  m_parties.id=  t_invoices.Customer_id join mc_partysubparty on mc_partysubparty.SubParty_id = t_invoices.Customer_id and mc_partysubparty.Route_id =%s WHERE t_invoices.InvoiceDate BETWEEN %s AND %s AND t_invoices.Party_id=%s''', [Route,FromDate,ToDate,Party])
           
                if query:
                    Invoice_serializer = LoadingSheetInvoicesSerializer(query, many=True).data
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': Invoice_serializer})
                    InvoiceListData = list()
                    for a in Invoice_serializer:
                        InvoiceListData.append({
                            "id": a['id'],
                            "InvoiceDate": a['InvoiceDate'],
                            "FullInvoiceNumber": a['FullInvoiceNumber'],
                            "Customer": a['Name'],
                            "CustomerID": a['Customer_id'],
                            "PartyID": a['Party_id'],
                            "GrandTotal": a['GrandTotal'],
                            "CreatedOn": a['CreatedOn'] 
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': InvoiceListData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

