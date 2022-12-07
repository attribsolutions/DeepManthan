from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Orders import *
from ..Serializer.S_Bom import *
from ..Serializer.S_WorkOrder import *
from ..models import *


class BomDetailsView(CreateAPIView):
   
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                BomDetailsdata = JSONParser().parse(request)
                BomID = BomDetailsdata['BomID']
                ItemID = BomDetailsdata['ItemID']
                GetQuantity = BomDetailsdata['Quantity']
                Query = M_BillOfMaterial.objects.filter(id=BomID,Item_id=ItemID)
                if Query.exists():
                    BOM_Serializer = M_BOMSerializerSecond(Query,many=True).data
                    BillofmaterialData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    for a in BOM_Serializer:
                        MaterialDetails =list()
                        total=0
                        for b in a['BOMItems']:
                            Item = b['Item']['id']
                            Qty = float(b['Quantity']) /float(a['EstimatedOutputQty'])
                            ActualQty = float(GetQuantity * Qty)
                            total += ActualQty
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['UnitID']['Name'],
                                "BOMQuantity":b['Quantity'],
                                "ActualQty":ActualQty
                            })
                        BillofmaterialData.append({
                            "id": a['id'],
                            "IsActive": a['IsActive'],
                            "Item":a['Item']['id'],
                            "ItemName":a['Item']['Name'],
                            "EstimatedOutputQty": round(total, 2),  
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['UnitID']['Name'],
                            "BOMItems":MaterialDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BillofmaterialData})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})

   