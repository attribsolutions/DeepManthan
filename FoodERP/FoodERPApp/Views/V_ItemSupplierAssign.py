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
        try:
            with transaction.atomic():  
                Item_data = JSONParser().parse(request)                
                ItemSupplierData = M_ItemSupplier.objects.filter()
                ItemSupplierData.delete()         
                ItemSerializer = ItemSupplierSerializer(data=Item_data,many=True) 
                if ItemSerializer.is_valid():                    
                    ItemSerializer.save()              
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Supplier saved successfully', 'Data': []})
                else:                
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': ItemSerializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': Exception(e), 'Data': []})


    def get(self,request):
        try:
            with transaction.atomic():
                query = M_ItemSupplier.objects.raw('''SELECT 1 id ,M_Items.id ItemID, M_Items.Name ItemName ,
                M_Group.Name AS GroupName,MC_SubGroup.Name AS SubGroupName,
                M_Parties.Name AS Suppliers,M_Parties.id PartyId
                FROM M_Items
                JOIN M_ChannelWiseItems ON M_ChannelWiseItems.Item_id=M_Items.ID and PartyType_id=19
                LEFT JOIN M_ItemSupplier ON M_ItemSupplier.Item_id=M_Items.id
                LEFT JOIN  M_Parties ON M_Parties.Id=M_ItemSupplier.Supplier_id
                LEFT JOIN MC_ItemGroupDetails ON MC_ItemGroupDetails.Item_id = M_Items.id   AND GroupType_id=5
                LEFT JOIN M_Group ON M_Group.id  = MC_ItemGroupDetails.Group_id 
                LEFT JOIN MC_SubGroup ON MC_SubGroup.id  = MC_ItemGroupDetails.SubGroup_id  
                ORDER BY M_Group.Sequence,MC_SubGroup.Sequence,MC_ItemGroupDetails.ItemSequence''') 
                # CustomPrint(query.query)                               
                if query:                    
                    ItemSupplierSerializer = GETItemSupplierSerializer(query, many=True).data                                  
                    Supplier_List=list()  
                    suppliers = []
                    TempItemID=0 
                    for a in  ItemSupplierSerializer:  
                        
                        if TempItemID==a["ItemID"]:                            
                            if a["PartyId"]:
                                suppliers.append({                                  
                                                "SupplierName": a["Suppliers"], 
                                                "SupplierId": a["PartyId"]
                                            })
                        else:                            
                            suppliers = []
                            TempItemID=a["ItemID"] 
                            if a["PartyId"]:
                                suppliers.append({                                  
                                                "SupplierName": a["Suppliers"], 
                                                "SupplierId": a["PartyId"]
                                            })
                            
                            Supplier_List.append({                        
                            "ItemID":a["ItemID"],
                            "ItemName":a["ItemName"],
                            "GroupName":a["GroupName"],
                            "SubGroupName":a["SubGroupName"],                            
                            "SupplierDetails":suppliers
                            })    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Supplier_List}) 
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Not available', 'Data' : []})               
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':Exception(e), 'Data':[]})
        
class OrderItemSupplier(CreateAPIView):
    permission_classes=(IsAuthenticated,)        
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                ItemSupplier_Data=JSONParser().parse(request)
                FromDate = ItemSupplier_Data['FromDate']
                ToDate = ItemSupplier_Data['ToDate']
                Company = ItemSupplier_Data['CompanyID']
                Party = ItemSupplier_Data['PartyID']

                ItemSupplierquery= T_Orders.objects.raw('''SELECT 1 id ,ifNULL(s.id,0)itemSupplierid,TC_OrderItems.Unit_id as UnitID,
                M_Items.Name MaterialName,s.Name ItemSupplierName, M_Items.id ItemID,SUM(TC_OrderItems.Quantity) AS Quantity,
                SUM(TC_OrderItems.QtyInNo)QtyInNo,SUM(TC_OrderItems.QtyInKg)QtyInKg,SUM(TC_OrderItems.QtyInBox)QtyInBox
                FROM T_Orders
                join TC_OrderItems on T_Orders.id=TC_OrderItems.Order_id 
                join M_Items on M_Items.id=TC_OrderItems.Item_id  
                LEFT JOIN M_ItemSupplier I ON I.item_id=M_Items.id 
                left join M_Parties s on I.Supplier_id=s.id                 
                where  OrderDate between %s and %s  And T_Orders.Supplier_id=%s And IsDeleted=0 And IsConfirm=1
                Group By M_Items.id,s.id,TC_OrderItems.Unit_id
                order by s.id desc''',[FromDate,ToDate,Party])            
                if ItemSupplierquery:                   
                    Supplier_List=list()  
                    ItemData = []
                    TempItemSupplierID="" 
                                  
                    for row in  ItemSupplierquery:
                        # print(TempItemSupplierID ,row.itemSupplierid)
                        if TempItemSupplierID == row.itemSupplierid:                            
                            # if row.PartyId:
                            ItemData.append({  
                                    "SKUName": row.MaterialName,                                    
                                    "QtyInNo": float(row.QtyInNo),
                                    "QtyInKg": float(row.QtyInKg),
                                    "QtyInBox": float(row.QtyInBox),   
                                        })
                        else:                            
                            ItemData = []
                            TempItemSupplierID=row.itemSupplierid 
                            # if row.PartyId:
                            ItemData.append({
                                    "SKUName": row.MaterialName,                                    
                                    "QtyInNo": float(row.QtyInNo),
                                    "QtyInKg": float(row.QtyInKg),
                                    "QtyInBox": float(row.QtyInBox)                                    
                                    
                                        })
                                                        
                        
                            Supplier_List.append({  
                                                                                
                                "SupplierName": row.ItemSupplierName,                                     
                                "ItemDetails":ItemData 
                            })          
                    
                    log_entry = create_transaction_logNew(request, ItemSupplier_Data, Party, 'From:'+FromDate+','+'To:'+ToDate,31,0,FromDate,ToDate,0)    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Supplier_List})
                log_entry = create_transaction_logNew(request, ItemSupplier_Data, Party, "Order Summary Not available",31,0) 
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Not available', 'Data' : []})   
        except Exception as e:
            return JsonResponse({'StatusCode':400,'Status':True,'Message':Exception(e), 'Data':[]})




        


