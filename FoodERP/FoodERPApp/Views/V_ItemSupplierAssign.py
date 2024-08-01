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
                query = M_ItemSupplier.objects.raw('''SELECT M_Items.id, M_Items.Name ItemName ,
                M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName,
                M_Parties.Name  AS Suppliers,M_Parties.id PartyId
                FROM M_Items
                LEFT JOIN M_ItemSupplier ON M_ItemSupplier.ItemID_id=M_Items.id
                LEFT JOIN  M_Parties ON M_Parties.Id=M_ItemSupplier.SupplierID_id
                LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id  AND GroupType_id=5
                LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id  
                ORDER BY M_Group.Sequence,MC_SubGroup.Sequence,M_Items.Sequence ''')                
                if query:                    
                    ItemSupplierSerializer = GETItemSupplierSerializer(query, many=True).data    
                    # CustomPrint(ItemSupplierSerializer)             
                    Supplier_List=list()
                    for a in  ItemSupplierSerializer: 
                        Supplier_List.append({                        
                            "ItemID":a["id"],
                            "ItemName":a["ItemName"],
                            "GroupName":a["GroupName"],
                            "SubGroupName":a["SubGroupName"],
                            "SupplierName":a["Suppliers"],
                            "SupplierId":a["PartyId"]
                        })  
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Supplier_List}) 
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Not available', 'Data' : []})               
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
