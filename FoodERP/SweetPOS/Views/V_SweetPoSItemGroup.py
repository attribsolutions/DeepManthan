import base64
from ..models import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework.authentication import BasicAuthentication
from FoodERPApp.models import *
from ..Serializer.S_SweetPoSItemGroup import *
from FoodERPApp.Views.V_CommFunction import create_transaction_logNew

def BasicAuthenticationfunction(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if auth_header:
                    
        # Parsing the authorization header
        auth_type, auth_string = auth_header.split(' ', 1)
        if auth_type.lower() == 'basic':
            
            
            try:
                username, password = base64.b64decode(
                    auth_string).decode().split(':', 1)
            except (TypeError, ValueError, UnicodeDecodeError):
                return Response('Invalid authorization header', status=status.HTTP_401_UNAUTHORIZED)
                
        user = authenticate(request, username=username, password=password)
    return user


class ItemGroupandSubgroupView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]

    def get(self, request):
        try:
            user = BasicAuthenticationfunction(request)
            if user is not None:
                groups = M_Group.objects.all()
                response_data = {"status": True, "status_code": 200, "count": groups.count(),"data": [] }              
                
                for group in groups:
                    sequence = group.Sequence if group.Sequence is not None else 0.00
                    group_data = {
                        "CompanyName": group.Name,
                        "POSCompanyID": group.id,
                        "CompanyDisplayName": group.Name,
                        "CompanyDisplayIndex":sequence,
                        "IsActive": True,
                        "Itemsgroup": []
                    }
                    subgroups = MC_SubGroup.objects.filter(Group=group)
                    for subgroup in subgroups:
                        sequence = group.Sequence if subgroup.Sequence is not None else 0.00
                        subgroup_data = {
                            "GroupID": subgroup.id,
                            "ItemName": None, 
                            "GroupName": subgroup.Name,
                            "GroupDisplayName": subgroup.Name,
                            "GroupDisplayIndex": sequence,
                            "IsActive": True,
                        }
                        group_data["Itemsgroup"].append(subgroup_data)
                    response_data["data"].append(group_data)
                return Response(response_data)
            else:
                return Response({'status': False, 'status_code': 401, 'message': 'Unauthorized'}, status=401)
        except Exception as e:
            return Response({'status': False, 'status_code': 400, 'message': str(e), 'data': []}, status=400)


class ItemListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    
    def get(self, request,DivisionID=0):
        try:
            user = BasicAuthenticationfunction(request)
            if user is not None:
                
                query = f"""SELECT i.CItemID AS CItemID, ifnull(i.BarCode,"")BarCode, 
                ifnull(Round(GSTHsnCodeMaster(i.id, CURDATE(), 3),2),0) AS HSNCode,
                i.Name, i.SAPItemCode AS ItemCode,  
                ifnull(Round(GSTHsnCodeMaster(i.id, CURDATE(), 2),2),0.0)  AS GST,
                ifnull(Round(GetTodaysDateMRP(i.id, CURDATE(), 2, NULL, NULL),2),0.0) AS Rate,
                ifnull(i.BaseUnitID_id,0) AS UnitID, 
                i.IsFranchisesItem,  
                ifnull(Round(GetTodaysDateMRP(i.id, CURDATE(), 2, NULL,NULL),2),0.0) AS FoodERPMRP,
                ifnull(subgroup.id,0) AS ItemGroupID
                FROM M_Items AS i
                LEFT JOIN MC_SubGroup AS subgroup ON i.id = subgroup.id
                LEFT JOIN M_ChannelWiseItems ON i.id = M_ChannelWiseItems.Item_id
                join MC_PartyItems on MC_PartyItems.Item_id=i.id and MC_PartyItems.party_id=(SELECT Party from SweetPOS.M_SweetPOSRoleAccess where Divisionid={DivisionID})
                WHERE M_ChannelWiseItems.PartyType_id = 19 """                  
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                response_data = {"status": True, "status_code": 200, "count": len(rows), "data": [] }
                for row in rows:
                    item_data = {
                        "CItemID": row[0],
                        "BarCode": row[1],
                        "HSNCode": row[2],
                        "Name": row[3],
                        "ItemCode": row[4],
                        "GST": row[5],
                        "Rate": row[6],
                        "UnitID": row[7],
                        "ISChitaleSupplier": True,  
                        "IsFranchisesPOSItem": row[8],
                        "UnitConversion": "",         
                        "FoodERPMRP": row[9],
                        "ItemGroupID": row[10],
                        "FranchisesItemCode": ""      
                    }
                    response_data["data"].append(item_data)

                return Response(response_data)
            else:
                return Response({'status': False, 'status_code': 401, 'message': 'Unauthorized'}, status=401)
        except Exception as e:
            return Response({'status': False, 'status_code': 400, 'message': str(e), 'data': []}, status=400)
