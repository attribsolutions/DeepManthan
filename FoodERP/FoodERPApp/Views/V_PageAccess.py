from msilib import sequence
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PageAccess import H_PageAccessSerializer

from ..models import *



class H_PageAccessView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                H_PageAccess_data = H_PageAccess.objects.all().order_by('Sequence')
                if H_PageAccess_data.exists():
                    H_PageAccess_serializer = H_PageAccessSerializer(H_PageAccess_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': H_PageAccess_serializer.data })
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Page Access Not available', 'Data': []})      
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                
               