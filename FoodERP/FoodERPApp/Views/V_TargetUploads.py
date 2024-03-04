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
from rest_framework.response import Response


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


class GetTargetUploadsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                query = T_TargetUploads.objects.raw("""SELECT T_TargetUploads.id, Month, Year, Party_id, 
                                                        M_Parties.Name, SheetNo
                                                        FROM T_TargetUploads
                                                        JOIN M_Parties ON M_Parties.id = T_TargetUploads.Party_id
                                                        GROUP BY SheetNo
                                                        """)
                TargetrList = list()
                if query:  
                    TargetSerializer = TargetUploadsSerializer(query, many=True).data
                    for a in TargetSerializer:
                        TargetrList.append({
                            "Month": a['Month'],
                            "Year": a['Year'],
                            "PartyID": a['Party']['id'],  
                            "PartyName": a['Party']['Name'],  
                            "SheetNo": a['SheetNo']
                        })

                    return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetrList})
                
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available', 'Data': []})
        except Exception as e:
            return Response({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})



