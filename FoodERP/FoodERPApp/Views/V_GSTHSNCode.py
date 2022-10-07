from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from django.db.models import Max
from rest_framework.parsers import JSONParser
from ..Serializer.S_GSTHSNCode import *
from ..Serializer.S_Items import *
from .V_CommFunction import *
from ..models import *


class M_GstHsnCodeView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                GstHsnCodedata = JSONParser().parse(request)
                a=MaxValueMaster(M_GSTHSNCode,'CommonID')
                jsondata=a.GetMaxValue() 
                additionaldata= list()
                for b in GstHsnCodedata:
                    b.update({'CommonID': jsondata})
                    additionaldata.append(b)
                M_GstHsncodeSerializer = M_GstHsnCodeSerializer(data=additionaldata,many=True)
            if M_GstHsncodeSerializer.is_valid():
                M_GstHsncodeSerializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'GST HsnCode Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_GstHsncodeSerializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})


