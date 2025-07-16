
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Orders import *
from ..Serializer.S_Bom import *
from ..models import *


'''BOM ---   Bill Of Material'''

class BOMListFilterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        BillOfMaterialdata = JSONParser().parse(request)
        try:            
            with transaction.atomic():
                # FromDate = BillOfMaterialdata['FromDate']
                # ToDate = BillOfMaterialdata['ToDate']
                Company = BillOfMaterialdata['Company']
                Party = BillOfMaterialdata['Party']
                Item=BillOfMaterialdata['ItemID']
                Category = BillOfMaterialdata['Category']
                IsVDCItem=BillOfMaterialdata['IsVDCItem']
                # PartyTypeID=BillOfMaterialdata['PartyTypeID']
                if IsVDCItem==0:
                    IsVDC=f"and IsVDCItem={IsVDCItem}"
                else:
                    IsVDC=""
                
                if Item == '':
                    Icondition= ""
                else:
                    Icondition= f" AND M_BillOfMaterial.Item_id = {Item}"
                
                if Category == 0:
                    Ccondition= ""
                else:
                    Ccondition= f"AND MC_ItemCategoryDetails.CategoryType_id = {Category}"
                PartyItems=""
                PartyId=""
                q1=M_Parties.objects.filter(id=Party).values('PartyType_id')
                PartyTypeID=q1[0]['PartyType_id']
                q2 = M_Settings.objects.filter(id=56).values('DefaultValue')
                DefaultValues = q2[0]['DefaultValue']
                if PartyTypeID==DefaultValues:
                        PartyItems=f"join MC_PartyItems on MC_PartyItems.Item_id=M_BillOfMaterial.Item_id and MC_PartyItems.Party_id={Party}"
                        PartyId=f" Party_id= {Party} and "
                # old query by shruti
                # SELECT M_BillOfMaterial.id, M_BillOfMaterial.BomDate, M_BillOfMaterial.EstimatedOutputQty,
                            #                 M_BillOfMaterial.Comment, M_BillOfMaterial.IsActive, M_BillOfMaterial.IsDelete, 
                            #                 M_BillOfMaterial.CreatedBy, M_BillOfMaterial.CreatedOn, M_BillOfMaterial.ReferenceBom, 
                            #                 M_BillOfMaterial.IsVDCItem, M_BillOfMaterial.Company_id, M_BillOfMaterial.Item_id, 
                            #                 M_BillOfMaterial.Unit_id, MC_ItemUnits.BaseUnitConversion, M_Users.LoginName, 
                            #                 M_Items.Name AS ItemName, C_Companies.Name AS CompanyName
                            # FROM M_BillOfMaterial
                            # JOIN M_Users ON M_Users.id = M_BillOfMaterial.CreatedBy
                            # JOIN MC_ItemCategoryDetails ON MC_ItemCategoryDetails.Item_id = M_BillOfMaterial.Item_id
                            # JOIN M_Items ON M_Items.id = M_BillOfMaterial.Item_id
                            # JOIN MC_ItemUnits ON MC_ItemUnits.Item_id = M_BillOfMaterial.Item_id  and IsBase=1
                            # JOIN C_Companies ON C_Companies.id = M_BillOfMaterial.Company_id
                            # WHERE M_BillOfMaterial.IsDelete = 0 AND M_BillOfMaterial.Company_id = {Company} {Icondition} {Ccondition}
                query = M_BillOfMaterial.objects.raw(f'''select id, BomDate, EstimatedOutputQty, Comment, IsActive, IsDelete, CreatedBy, CreatedOn, ReferenceBom, IsVDCItem, Company_id, a.Item_id, Unit_id, BaseUnitConversion, ItemName, 
ifnull(UnitwiseQuantityConversion(a.Item_id ,b.StockQuantity ,0 ,BaseUnitID_id ,Unit_id ,0 ,0 ),0) StockQuantity from 
(SELECT M_BillOfMaterial.id, M_BillOfMaterial.BomDate, M_BillOfMaterial.EstimatedOutputQty,
                                            M_BillOfMaterial.Comment, M_BillOfMaterial.IsActive, M_BillOfMaterial.IsDelete, 
                                            M_BillOfMaterial.CreatedBy, M_BillOfMaterial.CreatedOn, M_BillOfMaterial.ReferenceBom, 
                                            M_BillOfMaterial.IsVDCItem, M_BillOfMaterial.Company_id, M_BillOfMaterial.Item_id, 
                                            M_BillOfMaterial.Unit_id, MC_ItemUnits.BaseUnitConversion,  
                                            M_Items.Name AS ItemName, M_Items.BaseUnitID_id
                            FROM M_BillOfMaterial
                            {PartyItems}
                            JOIN MC_ItemCategoryDetails ON MC_ItemCategoryDetails.Item_id = M_BillOfMaterial.Item_id
                            JOIN M_Items ON M_Items.id = M_BillOfMaterial.Item_id
                            JOIN MC_ItemUnits ON MC_ItemUnits.Item_id = M_BillOfMaterial.Item_id  and IsBase=1
                            WHERE M_BillOfMaterial.IsDelete = 0 AND M_BillOfMaterial.Company_id ={Company} {IsVDC} {Icondition} {Ccondition} )a
                            left join 
                            (select sum(BaseUnitQuantity) StockQuantity,Item_id from O_BatchWiseLiveStock where {PartyId}  IsDamagePieces=0 group by Item_id )b
                            on a.Item_id=b.Item_id
''')
                
                # print(query)
                BomListData = []
                for a in query:
                    # Stock = float(GetO_BatchWiseLiveStock(a.Item_id, Party))
                    # StockintoSelectedUnit = UnitwiseQuantityConversion(a.Item_id, Stock, 0, 0, a.Unit_id, 0, 1
                    # ).ConvertintoSelectedUnit()
                    
                    BomListData.append({
                        "id": a.id,
                        "BomDate": a.BomDate,
                        "Item": a.Item_id,
                        "ItemName": a.ItemName, 
                        "Unit": a.Unit_id,
                        "UnitName": a.BaseUnitConversion,
                        "StockQty": round(a.StockQuantity,3),
                        "EstimatedOutputQty": a.EstimatedOutputQty,
                        "Comment": a.Comment,
                        "IsActive": a.IsActive,
                        "IsVDCItem": a.IsVDCItem,
                        # "Company": a.Company_id,
                        # "CompanyName": a.CompanyName,
                        "CreatedOn": a.CreatedOn,
                        "CreatedBy": a.CreatedBy,
                        "IsRecordDeleted": a.IsDelete,
                        # "UserName": a.LoginName  
                    }) 
                if BomListData:
                    log_entry = create_transaction_logNew(request, BillOfMaterialdata,Party,'Bill Of Material Data',453,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BomListData})
                else:
                    log_entry = create_transaction_logNew(request,BillOfMaterialdata,Party,'BillOfMaterial Data Does Not Exist',453,0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Record Not Found', 'Data': []})
        
        except Exception as e:
            log_entry = create_transaction_logNew(request, BillOfMaterialdata, 0,'BillOfMaterialData:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

class M_BOMsView(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        BillOfMaterial = JSONParser().parse(request)
        try:
            with transaction.atomic():
                # CustomPrint("Sush")
                ReferenceBOMID = BillOfMaterial['ReferenceBom']                
                Boms_Serializer = M_BOMSerializer(data=BillOfMaterial) 
                ItemID=BillOfMaterial['Item']                            
                BOMCount=M_BillOfMaterial.objects.filter(Item_id=ItemID).count()
                if BOMCount>0:
                    query = M_BillOfMaterial.objects.filter(Item_id=ItemID).update(IsDelete=1)
                if Boms_Serializer.is_valid():
                    Boms_Serializer.save()
                    # CustomPrint(ReferenceBOMID)
                    
                    if(ReferenceBOMID > 0):
                        # CustomPrint("3")
                        query = M_BillOfMaterial.objects.filter(id=ReferenceBOMID).update(IsActive=0,IsDelete=1)
                    log_entry = create_transaction_logNew(request, BillOfMaterial,0,'Bill Of Material Save Successfully',454,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material Save Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, BillOfMaterial,0,'BillOfMaterial Save:'+str(Boms_Serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Boms_Serializer.errors, 'Data': []})
        except Exception as e:
                log_entry = create_transaction_logNew(request, BillOfMaterial, 0,'BillOfMaterialData:'+str(e),33,0)
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})

class M_BOMsViewSecond(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Query = M_BillOfMaterial.objects.filter(id=id)
                # print(Query.query)
                if Query.exists():
                    BOM_Serializer = M_BOMSerializerSecond001(Query,many=True).data
                    BillofmaterialData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    for a in BOM_Serializer:
                        MaterialDetails =list()
                        ParentItem= a['Item']['id']
                        Parentquery = MC_ItemUnits.objects.filter(Item_id=ParentItem,IsDeleted=0)
                        # CustomPrint(query.query)
                        if Parentquery.exists():
                            ParentUnitdata = Mc_ItemUnitSerializerThird(Parentquery, many=True).data
                            ParentUnitDetails = list()
                           
                            for d in ParentUnitdata:
                                ParentUnitDetails.append({
                                   
                                "Unit": d['id'],
                                "UnitName": d['BaseUnitConversion'],
                            })
                        
                        for b in a['BOMItems']:
                            # CustomPrint(b)
                            ChildItem= b['Item']['id']
                            query = MC_ItemUnits.objects.filter(Item_id=ChildItem,IsDeleted=0)
                            # CustomPrint(query.query)
                            if query.exists():
                                Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                                UnitDetails = list()
                               
                                for c in Unitdata:
                                    UnitDetails.append({
                                    "Unit": c['id'],
                                    "UnitName": c['BaseUnitConversion'],
                                    
                                })
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "Quantity":b['Quantity'],
                                # "RemainNumberOfLot":a['RemainNumberOfLot'],
                                # "RemaninQuantity":a['RemaninQuantity'],
                                "UnitDetails":UnitDetails
                            })
                            
                        BillofmaterialData.append({
                            "id": a['id'],
                            "BomDate": a['BomDate'],
                            "Comment": a['Comment'],
                            "IsActive": a['IsActive'],
                            "IsVDCItem": a['IsVDCItem'],
                            "Company": a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "Item":a['Item']['id'],
                            "ItemName":a['Item']['Name'],
                            "EstimatedOutputQty": a['EstimatedOutputQty'],  
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['BaseUnitConversion'],
                            "ParentUnitDetails":ParentUnitDetails,
                            "BOMItems":MaterialDetails
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BillofmaterialData})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})
       
    @transaction.atomic()
    def put(self, request, id=0, Company=0):
        try:
            with transaction.atomic():
                checkitem = T_WorkOrder.objects.filter(Bom_id=id)
                # CustomPrint("shrut")
                # CustomPrint(checkitem)
                
                if checkitem.exists():
                    return JsonResponse({'StatusCode': 100, 'Status': True, 'Message': 'Bill Of Material used in Work Order, Still You Want to Create New Bill Of Material..', 'Data': []})
                else:    
                    Bomsdata = JSONParser().parse(request)
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Bomsdata })
                    BomsdataByID = M_BillOfMaterial.objects.get(id=id,Company_id=Company)                  
                    
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': str(BomsdataByID.query)})
                    Boms_Serializer = M_BOMSerializer(BomsdataByID, data=Bomsdata)
                    if Boms_Serializer.is_valid():
                        Boms_Serializer.save()   
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material Updated Successfully', 'Data': []})
                    else:
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Boms_Serializer.errors, 'Data': []})    
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})
    
    @transaction.atomic()
    def delete(self, request, id=0,Company=0):
        try:
            with transaction.atomic():
                Bomsdata = M_BillOfMaterial.objects.get(id=id)
                Bomsdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Bill Of Material  Deleted Successfully', 'Data': []})
        except M_BillOfMaterial.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Bill Of Material Not available', 'Data': []})
        except IntegrityError:
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Bill Of Material used in another table', 'Data': []})

class BulkBOMView(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request,id=0):
        BillOfMaterialdata = JSONParser().parse(request)
        try:            
            with transaction.atomic():                
                Company = BillOfMaterialdata['Company']
                Party=BillOfMaterialdata['Party']
                ids=BillOfMaterialdata['BOM_ID']  
                # GetQuantity = int(BillOfMaterialdata['Quantity'])              
                BomID = [int(id.strip()) for id in ids.split(',')]
                query = M_BillOfMaterial.objects.filter(id__in=(BomID),Company_id=Company)
                # return JsonResponse({'query': str(query.query)})
                if query:
                   
                    BOM_Serializer = M_BOMSerializerSecond001(query,many=True).data
                    BillofmaterialData = list()
                    # return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': BOM_Serializer})
                    for a in BOM_Serializer:
                        
                        Stock = float(GetO_BatchWiseLiveStock(
                            a['Item']['id'], Party))
                        StockintoSelectedUnit = UnitwiseQuantityConversion(
                            a['Item']['id'], Stock, 0, 0, a['Unit']['id'], 0,1).ConvertintoSelectedUnit()
                        # CustomPrint(StockintoSelectedUnit)
                        MaterialDetails =list()                         
                        
                        ParentItem= a['Item']['id']
                        Parentquery = MC_ItemUnits.objects.filter(Item_id=ParentItem,IsDeleted=0)
                        # CustomPrint(query.query)
                        if Parentquery.exists():
                            ParentUnitdata = Mc_ItemUnitSerializerThird(Parentquery, many=True).data
                            ParentUnitDetails = list()
                           
                            for d in ParentUnitdata:
                                ParentUnitDetails.append({
                                   
                                "Unit": d['id'],
                                "UnitName": d['BaseUnitConversion'],
                            })
                        
                        for b in a['BOMItems']:
                            # CustomPrint(b)
                            Item = b['Item']['id']
                            Stock = float(GetO_BatchWiseLiveStock(
                                b['Item']['id'], Party))

                            StockQty = UnitwiseQuantityConversion(
                                b['Item']['id'], Stock, 0, 0, b['Unit']['id'], 0,1).ConvertintoSelectedUnit()

                            # Qty = float(b['Quantity']) / \
                            #     float(a['EstimatedOutputQty'])
                            # ActualQty = float(Qty)
                            ChildItem= b['Item']['id']
                            query = MC_ItemUnits.objects.filter(Item_id=ChildItem,IsDeleted=0)
                            # CustomPrint(query.query)
                            if query.exists():
                                Unitdata = Mc_ItemUnitSerializerThird(query, many=True).data
                                UnitDetails = list()
                               
                                for c in Unitdata:
                                    UnitDetails.append({
                                    "Unit": c['id'],
                                    "UnitName": c['BaseUnitConversion'],
                                    
                                })
                            MaterialDetails.append({
                                "id": b['id'],
                                "Item":b['Item']['id'],
                                "ItemName":b['Item']['Name'], 
                                "Unit": b['Unit']['id'],
                                "UnitName": b['Unit']['BaseUnitConversion'],
                                "BomQuantity": b['Quantity'],
                                "Quantity": b['Quantity'],   
                                "StockQuantity": StockQty,                            
                                "UnitDetails":UnitDetails
                            })
                            
                        BillofmaterialData.append({
                            "id": a['id'],
                            "BomDate": a['BomDate'],
                            "Comment": a['Comment'],
                            "IsActive": a['IsActive'],
                            "IsVDCItem": a['IsVDCItem'],
                            "Company": a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "Item":a['Item']['id'],
                            "ItemName":a['Item']['Name'],
                            "EstimatedOutputQty": a['EstimatedOutputQty'],                             
                            "Stock": StockintoSelectedUnit,
                            "Unit": a['Unit']['id'],
                            "UnitName": a['Unit']['BaseUnitConversion'],
                            "ParentUnitDetails":ParentUnitDetails,                           
                            "BOMItems":MaterialDetails                            
                        })                       
                        
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'','Data': BillofmaterialData})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Record Not Found','Data': []})
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})


class GetBOMReport(CreateAPIView):
     permission_classes = (IsAuthenticated,) 
 
     @transaction.atomic()
     def post(self, request, *args, **kwargs):
        BOMdata = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Company = BOMdata['Company']
                Party = BOMdata['Party']
                Category = BOMdata['Category']
                Item = BOMdata['Item']  
                where_clause=""    
                if Category>0:
                    where_clause += f''' AND MC_ItemCategoryDetails.Category_id = {Category}'''              

                if Item>0:
                    where_clause += f''' AND M_BillOfMaterial.Item_id = {Item}'''
                
                ItemsGroupJoinsandOrderby = Get_Items_ByGroupandPartytype(Party,0).split('!')
                query = M_BillOfMaterial.objects.raw(f'''
                    SELECT  M_BillOfMaterial.id ,EstimatedOutputQty LOTQuantity,M_Items.id IngredianceID, M_Items.Name Ingrediance, I.id BOMItemID, I.Name BOMItem,
                    M_Category.Name CategoryName,M_Units.id UnitId,M_Units.Name UnitName,M_Parties.id PartyID,M_Parties.Name PartyName, {ItemsGroupJoinsandOrderby[0]} FROM  M_BillOfMaterial 
                    JOIN MC_BillOfMaterialItems ON MC_BillOfMaterialItems.BOM_id=M_BillOfMaterial.id
                    JOIN M_Items ON MC_BillOfMaterialItems.Item_id=M_Items.Id
                    JOIN M_Items I ON I.id=M_BillOfMaterial.Item_id
                    JOIN MC_ItemCategoryDetails ON MC_ItemCategoryDetails.Item_id=M_Items.id
                    JOIN M_Category ON M_Category.id = MC_ItemCategoryDetails.Category_id
                    JOIN MC_ItemUnits ON MC_ItemUnits.id= MC_BillOfMaterialItems.Unit_id
                    JOIN M_Units ON M_Units.id=MC_ItemUnits.UnitID_id 
                    JOIN M_Parties ON M_Parties.id=M_BillOfMaterial.party_id
                    {ItemsGroupJoinsandOrderby[1]}
                    WHERE M_BillOfMaterial.IsDelete=0 and M_BillOfMaterial.Company_id={Company}
                    AND (M_Parties.id={Party} OR {Party}=0 ){where_clause}
                    ''')               
                # print(query)                  
                if query:
                    
                    Bom_serializer = BOMReportSerializer(query, many=True).data 
                    
                   
                    log_entry = create_transaction_logNew(request, BOMdata, 0, '', 406, 0)  
                    
                    
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Bom_serializer})
                else:
                   
                    log_entry = create_transaction_logNew(request, 0, 0, "Get BOM report List:" +" BOM List Not available", 34, 0)
                    return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'No Records Found', 'Data': []})           
                
                  
        except Exception as e:            
            log_entry = create_transaction_logNew(request, BOMdata, 0, "Get Stock Entry Item List:"+str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})
         
         