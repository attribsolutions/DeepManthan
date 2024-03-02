from ..models import *
from ..Serializer.S_TargetUploads import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Q
from datetime import datetime
from django.db import connection
from django.db.models import Max


class TargetUploadsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TargetUploadsSerializer 
    
    @transaction.atomic()
    def perform_create(self, serializer):
       
        max_sheet_no = T_TargetUploads.objects.aggregate(Max('SheetNo'))['SheetNo__max']
        
        next_sheet_no = max_sheet_no + 1 if max_sheet_no is not None else 1
  
        serializer.validated_data['SheetNo'] = next_sheet_no
    
        serializer.save()

    def post(self, request):
        try:
            month = request.data.get('Month')
            year = request.data.get('Year')
            party = request.data.get('Party')
            item = request.data.get('Item')
            target_quantity = request.data.get('TargetQuantity')
            
            data = {
                'Month': month,
                'Year': year,
                'Party': party,
                'Item': item,
                'TargetQuantity': target_quantity,
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            
            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'TargetUploads Data Uploaded Successfully', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


  