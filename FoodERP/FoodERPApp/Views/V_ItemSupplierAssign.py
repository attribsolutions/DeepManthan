from ..models import  *
from ..Serializer.S_ItemSupplierAssign import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from .V_CommFunction import *



class ItemSupplierView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        Item_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Item = Item_data['Item']
                Supplier = Item_data['Supplier']
                SupplierIDs = Supplier.split(',')

                ItemSupplierList = list()
                for a in SupplierIDs:
                    ItemSupplierList = {
                        'ItemID': Item,
                        'SupplierID': a
                    }
                    ItemSerializer = ItemSupplierSerializer(data=ItemSupplierList)
                    if ItemSerializer.is_valid():
                        ItemSerializer.save()
              
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Supplier saved successfully', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})


    def get(self,request):
        try:
            with transaction.atomic():
                query = M_ItemSupplier.objects.raw('''Select A.Name ItemName, M_Group.Name GroupName, MC_SubGroup.Name SubGroupName, m_parties.Name PartyName
                        from M_ItemSupplier
                        join M_Items A on A.id = M_ItemSupplier.ItemID_id
                        join M_Parties on M_Parties.id = M_ItemSupplier.SupplierID_id
                        join MC_ItemGroupDetails B on B.Item_id = A.id
                        join M_Group on M_Group.id = B.Group_id
                        join MC_SubGroup on MC_SubGroup.id = B.SubGroup_id
                        where M_Parties.PartyType_id = 12''')
                # if query:
                #     ItemSerializer = ItemSupplierSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :ItemSerializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Bank not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})
        

class ItemSupplierUpdateView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def put(self, request, id=0):
        Item_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                ItemdataByID = M_ItemSupplier.objects.get(id=id)
                ItemSerializer = ItemSupplierSerializer(ItemdataByID, data=Item_data)
                if ItemSerializer.is_valid():
                    ItemSerializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bank Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ItemSerializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
