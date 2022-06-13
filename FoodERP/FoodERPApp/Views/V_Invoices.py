from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Invoices import T_InvoiceSerializer

from ..models import  *

class T_InvoiceView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Invoicedata = T_Invoice.objects.all()
                Invoice_serializer = T_InvoiceSerializer(Invoicedata, many=True)
                return JsonResponse({'StatusCode': 200, 'Status': 'true', 'Data': Invoice_serializer.data})
        except Exception as e:
            raise Exception(e)
            print(e)

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Invoicedata = JSONParser().parse(request)
                Invoice_serializer = T_InvoiceSerializer(data=Invoicedata)
                if Invoice_serializer.is_valid():
                    Invoice_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': 'Invoice Save Successfully'})
                return JsonResponse({'StatusCode': 200, 'Status': 'true',  'Message': Invoice_serializer.errors})
        except Exception as e:
            raise Exception(e)

