from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_Orders import Mc_ItemUnitSerializerThird
from ..Serializer.S_StockAdjustment import *
from ..Serializer.S_Parties import *
from ..Serializer.S_ItemSale import *
from ..models import *
from django.db.models import F, Q



class ShowBatchesForItemView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def get(self, request, id=0,Party=0):
        try:
            with transaction.atomic():
                query=O_BatchWiseLiveStock.objects.raw('''SELECT O_BatchWiseLiveStock.id,O_BatchWiseLiveStock.Item_id,M_Items.Name ItemName,OriginalBaseUnitQuantity,BaseUnitQuantity,O_LiveBatches.BatchDate,O_LiveBatches.BatchCode,O_LiveBatches.SystemBatchDate,O_LiveBatches.SystemBatchCode,O_LiveBatches.MRPValue,O_LiveBatches.MRP_id MRPID,M_MRPMaster.MRP,O_LiveBatches.GST_id,M_GSTHSNCode.GSTPercentage,M_Units.id UnitID,M_Units.Name UnitName FROM O_BatchWiseLiveStock JOIN O_LiveBatches ON O_LiveBatches.id=O_BatchWiseLiveStock.LiveBatche_id LEFT JOIN M_MRPMaster ON M_MRPMaster.id= O_LiveBatches.MRP_id JOIN M_GSTHSNCode ON M_GSTHSNCode.id=O_LiveBatches.GST_id  JOIN M_Items ON M_Items.id =O_BatchWiseLiveStock.Item_id JOIN M_Units ON M_Units.id = M_Items.BaseUnitID_id WHERE O_BatchWiseLiveStock.Item_id=%s AND O_BatchWiseLiveStock.Party_id=%s  AND IsDamagePieces =0 order by id desc limit 5''',([id],[Party]))
               
                if query:
                    BatchCodelist = list()
                    Obatchwise_serializer = OBatchWiseLiveStockAdjustmentSerializer(query, many=True).data
                    for a in Obatchwise_serializer:
                        Unitquery = MC_ItemUnits.objects.filter(Item_id=a['Item_id'],IsDeleted=0)
                        if Unitquery.exists():
                            Unitdata = Mc_ItemUnitSerializerThird(Unitquery, many=True).data
                            ItemUnitDetails = list()
                            for c in Unitdata:
                                ItemUnitDetails.append({
                                "Unit": c['id'],
                                "BaseUnitQuantity": c['BaseUnitQuantity'],
                                "IsBase": c['IsBase'],
                                "UnitName": c['BaseUnitConversion'],
                            })
                        BatchCodelist.append({
                            'id':  a['id'],
                            'Item':  a['Item_id'],
                            'ItemName':  a['ItemName'],
                            'OriginalBaseUnitQuantity': a['OriginalBaseUnitQuantity'],
                            'BaseUnitQuantity':  a['BaseUnitQuantity'],
                            'BatchDate':  a['BatchDate'],
                            'BatchCode':  a['BatchCode'],
                            'SystemBatchDate':  a['SystemBatchDate'],
                            'SystemBatchCode':  a['SystemBatchCode'],
                            'MRPValue':  a['MRPValue'],
                            'MRPID':  a['MRPID'],
                            'MRP':  a['MRP'],
                            'GSTID':  a['GST_id'],
                            'GSTPercentage':  a['GSTPercentage'],
                            'UnitID':  a['UnitID'],
                            'UnitName':  a['UnitName'],
                            'UnitOptions' : ItemUnitDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BatchCodelist})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Stock Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})