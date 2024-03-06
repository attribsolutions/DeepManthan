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
    serializer_class = TargetUploadsOneSerializer  
    sheet_no_updated = False

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            request_data = request.data  
            if not self.sheet_no_updated:
                existing_sheet = T_TargetUploads.objects.filter(Month=request_data[0]['Month'], Year=request_data[0]['Year']).first()
                if existing_sheet:
                    return JsonResponse({'StatusCode': 409, 'Status': False, 'Message': 'Sheet for this month and year already exists', 'Data': []})

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
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Sheet already uploaded for this month and year', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data':[]})
        

class GetTargetUploadsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            TargetData = JSONParser().parse(request)       
            month = TargetData['Month']   
            year=  TargetData['Year']  
            party_id=TargetData['Party']
            
            query = T_TargetUploads.objects.raw("""SELECT T_TargetUploads.id, Month, Year, Party_id, 
                                                    M_Parties.Name, SheetNo
                                                    FROM T_TargetUploads
                                                    JOIN M_Parties ON M_Parties.id = T_TargetUploads.Party_id
                                                    WHERE Month = %s AND Year = %s AND Party_id = %s""", [month, year, party_id])

            TargetList = []
            for a in query:
                TargetList.append({
                    "Month": a.Month,
                    "Year": a.Year,
                    "PartyID": a.Party_id,  
                    "PartyName": a.Name,  
                    "SheetNo": a.SheetNo
                })

            if TargetList:
                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetList})
            else:
                return Response({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available', 'Data': []})
        except Exception as e:
            return Response({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


class GetTargetUploadsBySheetNoView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    def get(self, request, SheetNo, PartyID):
        try:
            query = T_TargetUploads.objects.filter(SheetNo=SheetNo, Party_id=PartyID)
            TargetList = []
            if query:
                Targetrdata = TargetUploadsSerializer(query, many=True).data
                for a in Targetrdata:
                    TargetList.append({
                            "Month": a['Month'],
                            "Year": a['Year'],
                            "PartyID": a['Party']['id'],  
                            "PartyName": a['Party']['Name'], 
                            "ItemID" : a['Item']['id'],
                            "ItemName" : a['Item']['Name'],
                            "TargetQuantity" : a['TargetQuantity'],
                            "SheetNo": a['SheetNo']
                        })    

                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetList})
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class DeleteTargetRecordsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def delete(self, request):
        try:
            with transaction.atomic():
                target_data = JSONParser().parse(request)
                months = target_data.get('Month', '').split(',')
                years = target_data.get('Year', '').split(',')
                party_ids = target_data.get('Party', '').split(',')
             
                T_TargetUploads.objects.filter(Month__in=months,Year__in=years, Party__in=party_ids).delete()
             
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Targets Delete Successfully', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})

 