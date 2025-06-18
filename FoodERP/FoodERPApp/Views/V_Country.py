from ..models import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from .V_CommFunction import *
from ..Serializer.S_Country import *


class CountryCurrencySaveView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request):
        CountryCurrency_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Country_serializer = CountrySerializer(data=CountryCurrency_data, many=True)
                if Country_serializer.is_valid():                    
                    Country_serializer.save()
                    log_entry = create_transaction_logNew(request, CountryCurrency_data,0,'',423,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Country Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, 0,0,'CountrySave:'+str(Country_serializer.errors),34,0)
                    transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Country_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, CountryCurrency_data,0,'CountrySave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data': []})

class CountryCurrencyListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():
                query = M_Country.objects.all()
                if query:
                    Country_serializer = CountrySerializer(query, many=True).data
                    log_entry = create_transaction_logNew(request, Country_serializer,0,'',424,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Country_serializer})
                log_entry = create_transaction_logNew(request, Country_serializer,0,'Country not available',424,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Country not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'Get List of Country:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':str(e), 'Data':[]})
        
class CountryCurrencyViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Countrydata = M_Country.objects.get(id=id)
                Country_serializer = CountrySerializer(Countrydata)
                log_entry = create_transaction_logNew(request, Country_serializer,0,'',425,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Country_serializer.data})
        except  M_Country.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Country not available',425,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Country Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'Get single Country'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
    @transaction.atomic()
    def put(self, request, id=0):
        Countrydata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                query = M_Country.objects.get(id=id)
                for a in Countrydata:
                    Country_serializer = CountrySerializer(query, data=a)
                    if Country_serializer.is_valid():
                        Country_serializer.save()
                        log_entry = create_transaction_logNew(request, Countrydata,0,'CountryID:'+str(id),426,id)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Country Updated Successfully','Data' :[]})
                    else:
                        log_entry = create_transaction_logNew(request, Countrydata,0,'CountryUpdate:'+str(Country_serializer.errors),34,0)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Country_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request,Countrydata,0,'CountryUpdate:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
    

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Countrydata = M_Country.objects.get(id=id)
                Countrydata.delete()
                log_entry = create_transaction_logNew(request, 0,0,'CountryID:'+str(id),427,id)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Country Deleted Successfully','Data':[]})
        except M_Bank.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Country Not available',427,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Country Not available', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'CountryDelete:'+'Country used in transaction',8,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Country used in transaction', 'Data': []})

   
