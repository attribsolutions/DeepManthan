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
    TargetSerializer = TargetUploadsOneSerializer
    SheetNoUpdated = False

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                request_data = request.data
          
            if not self.SheetNoUpdated:
                ExistingSheet = T_TargetUploads.objects.filter(Month=request_data[0]['Month'], Year=request_data[0]['Year'], Party=request_data[0]['Party']).first()
                if ExistingSheet:
                    return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Sheet has already been created.', 'Data': []})
   
                MaxSheetNo = T_TargetUploads.objects.aggregate(Max('SheetNo'))['SheetNo__max']
                NextSheetNo = MaxSheetNo + 1 if MaxSheetNo is not None else 1
                self.SheetNoUpdated = True

                request_data[0]['SheetNo'] = NextSheetNo

                TargetSerializerOne = self.TargetSerializer(data=request_data[0])
                TargetSerializerOne.is_valid(raise_exception=True)
                TargetSerializerOne.save()
                
                # Calculate RateWithGST using raw SQL query with PartyType condition
                RateQuery = """SELECT RateCalculationFunction1(0, item_id, party_id, 1, 0, 0, 0, 1) AS RateWithGST
                    FROM T_TargetUploads 
                    INNER JOIN M_Parties ON T_TargetUploads.Party_id = M_Parties.id
                    WHERE T_TargetUploads.id = party_id AND M_Parties.PartyType_id = party_type_id;"""
                RateData = {
                    'item_id': request_data[0]['Item'],
                    'party_id': request_data[0]['Party'],
                    'party_type_id': request_data[0]['PartyType']
                }

                query = T_TargetUploads.objects.raw(RateQuery, RateData)[0].RateWithGST

                # Save data with calculated RateWithGST to the T_TargetUploads model
                request_data[0]['RateWithGST'] = query
                TargetSerializerOne = self.TargetSerializer(data=request_data[0])
                TargetSerializerOne.is_valid(raise_exception=True)
                TargetSerializerOne.save()

                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Target Data Uploaded Successfully', 'Data': []})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Sheet has already been created.', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})




class GetTargetUploadsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            TargetData = JSONParser().parse(request)       
            month = TargetData['Month']   
            year = TargetData['Year']  
            party_id = TargetData['Party'] 

            if party_id:
                query = T_TargetUploads.objects.raw(
                    """SELECT T_TargetUploads.id, Month, Year, Party_id, 
                       M_Parties.Name, SheetNo
                       FROM T_TargetUploads
                       JOIN M_Parties ON M_Parties.id = T_TargetUploads.Party_id
                       WHERE Month = %s AND Year = %s AND Party_id = %s
                       GROUP BY Party_id, SheetNo""",
                    [month, year, party_id]
                )
            else:
                query = T_TargetUploads.objects.raw(
                    """SELECT T_TargetUploads.id, Month, Year, Party_id, 
                       M_Parties.Name, SheetNo
                       FROM T_TargetUploads
                       JOIN M_Parties ON M_Parties.id = T_TargetUploads.Party_id
                       WHERE Month = %s AND Year = %s
                       GROUP BY Party_id, SheetNo""",
                    [month, year]
                )
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
            return Response({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


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

 