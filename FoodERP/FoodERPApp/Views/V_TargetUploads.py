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
                ExistingSheet = T_TargetUploads.objects.filter( Month=request_data[0]['Month'], Year=request_data[0]['Year'], Party=request_data[0]['Party'] ).first()
                
                if ExistingSheet:
                    return JsonResponse({'StatusCode': 226,'Status': True,'Message': 'Sheet has already been created.','Data': [] })
   
                MaxSheetNo = T_TargetUploads.objects.aggregate(Max('SheetNo'))['SheetNo__max']
                NextSheetNo = MaxSheetNo + 1 if MaxSheetNo is not None else 1
                self.SheetNoUpdated = True

                request_data[0]['SheetNo'] = NextSheetNo
                ItemID = request_data[0]['Item']
                PartyID = request_data[0]['Party']

                query = T_TargetUploads.objects.raw("""SELECT T_TargetUploads.id, RateCalculationFunction1(0, %s, %s, 2, 0, 0, 0, 1) AS RateWithGST
                                                        FROM T_TargetUploads 
                                                        WHERE Party_id = %s;""",[ItemID, PartyID, PartyID])

                if query:
                    request_data[0]['RateWithGST'] = query[0].RateWithGST
                else:
                    request_data[0]['RateWithGST'] = None

                TargetSerializerOne = self.TargetSerializer(data=request_data[0])
                TargetSerializerOne.is_valid(raise_exception=True)
                TargetSerializerOne.save()
                
                for data in request_data[1:]:
                    data['SheetNo'] = NextSheetNo
        
                TargetSerializerTwo = self.TargetSerializer(data=request_data[1:], many=True)
                TargetSerializerTwo.is_valid(raise_exception=True)
                TargetSerializerTwo.save()

                return JsonResponse({'StatusCode': 200,'Status': True,'Message': 'Target Data Uploaded Successfully','Data': [] })
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406,'Status': True,'Message': 'Sheet has already been created.','Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400,'Status': True, 'Message': str(e),'Data': [] })


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
               

class TargetVSAchievementView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():
                query = T_TargetUploads.objects.raw('''SELECT T_TargetUploads.id, Month,Year, M_Parties.id AS PartyID, M_Parties.Name AS PartyName,
                                                        M_Items.id AS ItemId, M_Items.Name AS ItemName, M_Group.Name AS ItemGroup, 
                                                        MC_SubGroup.Name AS ItemSubGroup,
                                                        M_Cluster.Name AS Cluster, M_SubCluster.Name AS SubCluster, SheetNo
                                                        FROM T_TargetUploads 
                                                        JOIN M_Parties ON T_TargetUploads.Party_id = M_Parties.id
                                                        JOIN M_Items  ON T_TargetUploads.Item_id = M_Items.id
                                                        JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id
                                                        JOIN M_Group ON MC_ItemGroupDetails.Group_id = M_Group.id
                                                        JOIN MC_SubGroup  ON MC_ItemGroupDetails.SubGroup_id = MC_SubGroup.id
                                                        LEFT JOIN M_PartyDetails  ON M_PartyDetails.Party_id = M_Parties.id
                                                        LEFT JOIN M_Cluster ON M_PartyDetails.Cluster_id = M_Cluster.id
                                                        LEFT JOIN M_SubCluster  ON M_PartyDetails.SubCluster_id = M_SubCluster.id
                                                        Where M_Group.GroupType_id=1 and M_PartyDetails.Group_id is null''')
                                                  
                if query:
                    Target_Achievement_Serializer = TargetAchievementSerializer(query, many=True).data
                    Target_Achievement_List = list()
                    for a in Target_Achievement_Serializer:
                        Target_Achievement_List.append({
                            "id" : a["id"],
                            "Month":a['Month'],
                            "Year":a['Year'],
                            "PartyID": a['id'],  
                            "PartyName": a['PartyName'], 
                            "ItemName" : a['ItemName'],
                            "ItemGroup" :a ['ItemGroup'],
                            "ItemSubGroup":a['ItemSubGroup'],
                            "Cluster":a['Cluster'],
                            "SubCluster":a['SubCluster'],
                            "SheetNo":a['SheetNo']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Target_Achievement_List})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Unit not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]}) 
        
        
