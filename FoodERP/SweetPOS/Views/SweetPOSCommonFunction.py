from django.contrib.auth import authenticate
from ..models import *
import base64
from rest_framework.response import Response
from rest_framework import status
from django.db.models.functions import Coalesce
from datetime import datetime 
from FoodERPApp.models import  *
from django.db.models import *


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

def GetYear(TDate):
    date = datetime.strptime(str(TDate), "%Y-%m-%d").date()
    #initialize the current year
    year_of_date=date.year     
    #initialize the current financial year start date
    financial_year_start_date = datetime.strptime(str(year_of_date)+"-04-01","%Y-%m-%d").date()       
    if date<financial_year_start_date:           
        fs=  str(financial_year_start_date.year-1)+'-04-01'            
        fe=  str(financial_year_start_date.year)+'-03-31'           
    else:
        fs= str(financial_year_start_date.year)+ '-04-01'           
        fe= str(financial_year_start_date.year+1)+'-03-31'
    return fs,fe

class GetInvoiceDetails: 
    
    def GetPOSInvoiceNumber(*args):
        
            Return_year= GetYear(args[1])       
            fs,fe=Return_year 

            MaxInvoiceNumber=T_SPOSInvoices.objects.filter(Party=args[0],InvoiceDate__range=(fs,fe),ClientID=args[2]).values('InvoiceNumber').order_by('-id')[:1]   
            if MaxInvoiceNumber:
                max_invoice = int(MaxInvoiceNumber[0]['InvoiceNumber'])
                a = max_invoice + 1
            else:
                a = 1  

            return a
        
    def GetPOSInvoicePrifix(*args):
            Prifix=MC_PartyPrefixs.objects.filter(Party_id=args[0]).values('Invoiceprefix')
            if not Prifix :
                a=""
            else:
                a=Prifix[0]['Invoiceprefix']
            return a
            
        
        
        
        
        