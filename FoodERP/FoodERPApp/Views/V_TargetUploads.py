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
from django.db import transaction


class TargetUploadsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TargetUploadsSerializer  
    sheet_no_updated = False

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            request_data = request.data  

            if not self.sheet_no_updated: 
                max_sheet_no = T_TargetUploads.objects.aggregate(Max('SheetNo'))['SheetNo__max']
                
                next_sheet_no = max_sheet_no + 1 if max_sheet_no is not None else 1
                
                self.sheet_no_updated = True 
                
                
                request_data[0]['SheetNo'] = next_sheet_no

                
                serializer_first = self.get_serializer(data=request_data[0])
                serializer_first.is_valid(raise_exception=True)
                
                serializer_first.save()

                for data in request_data[1:]:
                    data['SheetNo'] = next_sheet_no

            serializer_others = self.get_serializer(data=request_data[1:], many=True)
            serializer_others.is_valid(raise_exception=True)

            serializer_others.save()

            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Target Data Uploaded Successfully', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
