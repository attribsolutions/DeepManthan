from django.shortcuts import render

from FoodERPApp.models import M_Settings

from .models import *
from datetime import date

# Create your views here.
def get_client_ip(request):
    """
    Get the client's IP address from the request.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def create_transaction_logNew2(request, data, PartyID, TransactionDetails, TransactionType=0, TransactionID=0, FromDate=0, ToDate=0, CustomerID=0):
    
    Authenticated_User = request.user
    User = Authenticated_User.id
    aa = M_Settings.objects.filter(id=31).values('DefaultValue')
    

    if aa[0]['DefaultValue'] == '1':
        
        if not User:
            User = data.get('UserID', 0)
            # User = data['UserID']
        else:
            pass
        
        if not FromDate:
            
            log_entry = L_Transactionlog.objects.using('transactionlog_db').create(TranasactionDate=date.today(), User=User, PartyID=PartyID, IPaddress=get_client_ip(
                request), TransactionDetails=TransactionDetails, JsonData=0, TransactionType=TransactionType, TransactionID=TransactionID, CustomerID=CustomerID)
        else:
            
            log_entry = L_Transactionlog.objects.using('transactionlog_db').create(TranasactionDate=date.today(), User=User, PartyID=PartyID, IPaddress=get_client_ip(
                request), TransactionDetails=TransactionDetails, JsonData=0, TransactionType=TransactionType, TransactionID=TransactionID, FromDate=FromDate, ToDate=ToDate, CustomerID=CustomerID)
            
        L_TransactionLogJsonData.objects.using('transactionlog_db').create(Transactionlog=log_entry, JsonData=data)

        return log_entry

    else:
        
        return None