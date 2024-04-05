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
from ..Views.V_CommFunction import *



class TargetUploadsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
        
    @transaction.atomic
    def post(self, request):
        TargetDataDetails = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                Month = TargetDataDetails[0]['Month']
                Year = TargetDataDetails[0]['Year']

                ExistingSheet = T_TargetUploads.objects.filter(Month=Month, Year=Year)
                if ExistingSheet:
                    return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'Target Data has already been uploaded for the Month :'+ str(Month) +', Year :'+ str(Year), 'Data': [] })
                else:
                    MaxSheetNo = T_TargetUploads.objects.aggregate(Max('SheetNo'))['SheetNo__max']
                    NextSheetNo = MaxSheetNo + 1 if MaxSheetNo is not None else 1
                
                for TargetData in TargetDataDetails:
                    
                    TargetData['SheetNo'] = NextSheetNo
                    ItemID = TargetData['Item']
                    Party = TargetData['Party']
                    TargetQuantity = TargetData['TargetQuantity']
                    Unit = TargetData['Unit']
                    
                    Item = M_Items.objects.filter(id=ItemID).values("BaseUnitID","Name")
                    
                    TargetData['ItemName'] = Item[0]["Name"]
                    BaseUnitID = Item[0]["BaseUnitID"]
                    BaseUnitQuantity = UnitwiseQuantityConversion(ItemID, TargetQuantity, 0, Unit, 0, BaseUnitID, 0).GetBaseUnitQuantity()
                    TargetData['TargetQuantityInBaseUnit'] = float(BaseUnitQuantity)
                    QtyInNo = UnitwiseQuantityConversion(ItemID, TargetQuantity, 0, Unit, 0, 1, 0).ConvertintoSelectedUnit()
                    TargetData['QtyInNo'] = float(QtyInNo)

                    QtyInKg = UnitwiseQuantityConversion(ItemID, TargetQuantity, 0, Unit, 0, 2, 0).ConvertintoSelectedUnit()
                    
                    TargetData['QtyInKg'] = float(QtyInKg)

                    QtyInBox = UnitwiseQuantityConversion(ItemID, TargetQuantity, 0, Unit, 0, 4, 0).ConvertintoSelectedUnit()
                    TargetData['QtyInBox'] = float(QtyInBox)
                        
                    query = T_TargetUploads.objects.raw("""SELECT 1 as id, RateCalculationFunction1(0, %s, %s, %s, 0, 0, 0, 1) AS RateWithGST """, [ItemID, Party,BaseUnitID])
                    
                    if query:
                         
                        for row in query:
                            Rate = row.RateWithGST
                        
                        TargetData['Rate'] = float(Rate)
                        
                        Amount = float(BaseUnitQuantity) * float(Rate)
                        
                        Amount = round(Amount, 2)
                        TargetData['Amount'] = Amount
                        
                    else:
                        # ItemName = Item[0]["Name"]
                        # log_entry = create_transaction_logNew(request, TargetDataDetails, 0, 'TargetDataUpload:' + str(TargetSerializer.errors), 34, 0)
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':' TargetSerializer.errors', 'Data': [] })
                    
                    
                # return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': '', 'Data': TargetDataDetails })
                
                TargetSerializer = TargetUploadsOneSerializer(data=TargetDataDetails , many=True)
                if TargetSerializer.is_valid():
                    TargetSerializer.save()
                    
                    log_entry = create_transaction_logNew(request, TargetDataDetails, 0, 'TargetSheetUploaded', 353, 0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Target Data Uploaded Successfully', 'Data': [] })
                else:
                   
                    log_entry = create_transaction_logNew(request, TargetDataDetails, 0, 'TargetDataUpload:' + str(TargetSerializer.errors), 34, 0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': TargetSerializer.errors, 'Data': [] })
        except Exception as e:
            
            log_entry = create_transaction_logNew(request, TargetDataDetails, 0, 'TargetDataUpload: ' + str(e), 33, 0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': (e), 'Data': [] })


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
                log_entry = create_transaction_logNew(request, TargetData,party_id,'',354,0)
                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetList})
            else:
                log_entry = create_transaction_logNew(request,0,0,'TargetData Does Not Exist',354,0)
                return Response({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'TargetData:'+str(Exception(e)),33,0)
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
                log_entry = create_transaction_logNew(request, Targetrdata,0,'',355,0)
                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetList})
            log_entry = create_transaction_logNew(request,0,0,'Targetrdata Does Not Exist',355,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'Targetrdata:'+str(Exception(e)),33,0)
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
                log_entry = create_transaction_logNew(request, target_data,0,f'Month: {months} Year: {years} Party: {party_ids}Deleted Successfully',356,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Targets Delete Successfully', 'Data': []})
        except IntegrityError:
            log_entry = create_transaction_logNew(request, 0,0,'Targets Data used in another table',8,0)     
            return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': 'This Transaction used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'TargetsNotDeleted:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
        

class TargetVSAchievementView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            TargetData = request.data
            Month = TargetData.get('Month')
            Year = TargetData.get('Year')
            Party = TargetData.get('Party')
            Employee = TargetData.get('Employee')            
             
            if Employee > 0 and Party == 0:
                    EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[Employee])
                    for row in EmpPartys:
                        p=row.id
                    Party_ID = p.split(",")
                    dd=Party_ID[:-1]
                    Party=', '.join(dd)
                    
            query = T_TargetUploads.objects.raw(f'''
            SELECT 1 id,CONCAT(DATE_FORMAT(CONCAT({Year}, '-', {Month}, '-01'), '%%b'), '-', {Year}) AS Year,
            (CASE WHEN {Month} >= 4 THEN CONCAT({Year}, '-', {Year} + 1) ELSE CONCAT({Year} - 1, '-', {Year}) END) AS FY,D.Party_id PartyID,Item, M_Items.Name ItemName,M_Group.Name ItemGroupName,
            MC_SubGroup.Name SubGroupName,M_Cluster.Name ClusterName,
            M_SubCluster.Name SubClusterName,M_Parties.SAPPartyCode,M_Parties.Name PartyName ,
            Round(IFNULL(TargetQuantity,0),3)TargetQuantityInKG,Round(IFNULL(TargetAmount,0),2)TargetAmount,Round(IFNULL(Quantity,0),3)AchQuantity,
            Round(IFNULL(Amount,0),2)AchAmount,Round(IFNULL(CRNoteQuantity,0),3)CRNoteQuantity,Round(IFNULL(CRNoteAmount,0),2)CRNoteAmount 
            FROM
  
  (SELECT I.Party_id,I.Item,TargetQuantity,TargetAmount,Quantity,Amount,CRNoteQuantity,CRNoteAmount,Month,Year from 
  (SELECT Item,Party Party_id from (select distinct Item_id Item  from M_ChannelWiseItems where PartyType_id =9)s ,
(SELECT id Party, Name from M_Parties where PartyType_id in (9) and id in (SELECT Distinct SubParty_id from MC_PartySubParty WHERE Party_id in (select id from M_Parties WHERE Company_id=2 AND PartyType_id = 12)))P )I 

left join 
  
  (select  Month,Year,Party_id,Item_id,Sum(QtyInKg) TargetQuantity,Sum(Amount) TargetAmount from T_TargetUploads
   where  Month={Month} and Year={Year} group by item_id,Party_id )A
   on I.Item = A.Item_id and I.Party_id = A.Party_id
            
left join 
(select Customer_id ,Item_id ,Sum(TC_InvoiceItems.QtyInKg)Quantity,Sum(Amount)Amount from T_Invoices
 join TC_InvoiceItems ON TC_InvoiceItems.invoice_id=T_Invoices.id
 where Month(invoiceDate)={Month} and year(invoiceDate)={Year} and DeletedFromSAP=0 group by item_id,customer_id )B
 on I.Item = B.Item_id and I.Party_id = B.Customer_id
 left join 
(SELECT Customer_id ,Item_id ,Sum(TC_CreditDebitNoteItems.Quantity)CRNoteQuantity,Sum(Amount)CRNoteAmount
FROM T_CreditDebitNotes
JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id=T_CreditDebitNotes.id
WHERE Month(CRDRNoteDate)={Month} and year(CRDRNoteDate)={Year} group by item_id,customer_id)C 
on I.Item = C.Item_id and I.Party_id = C.Customer_id WHERE (TargetQuantity>0 OR Quantity>0 OR  CRNoteQuantity >0)
Order By I.Party_id,Item)D
join  M_Items ON M_Items.id=D.Item
join MC_ItemGroupDetails  ON MC_ItemGroupDetails.Item_id=M_Items.id
join  M_Group  ON M_Group.id=MC_ItemGroupDetails.Group_id
join  MC_SubGroup ON MC_SubGroup.id=MC_ItemGroupDetails.SubGroup_id
join M_PartyDetails ON M_PartyDetails.Party_id=D.Party_id
join M_Cluster ON M_Cluster.id=M_PartyDetails.Cluster_id
join M_SubCluster ON  M_SubCluster.id=M_PartyDetails.SubCluster_id
join M_Parties  ON M_Parties.id=D.Party_id
  where MC_ItemGroupDetails.GroupType_id=1  and M_PartyDetails.Group_id is null
            ''')
            TargetAchievementList = []   
           
            if query:   
                for a in query:
                    TargetAchievementList.append({
                    "id": a.id,
                    "Year": a.Year,
                    "Fy":a.FY,
                    "TargetQuantity": a.TargetQuantity,
                    "TargetAmount" : a.TargetAmount,
                    "Quantity":a.Quantity,
                    "Amount":a.Amount,
                    "PartyID": a.PartyID,
                    "PartyName": a.PartyName,
                    "ItemName": a.ItemName,
                    "ItemGroup": a.ItemGroupName,
                    "ItemSubGroup": a.SubGroupName,
                    "Cluster": a.ClusterName,
                    "SubCluster": a.SubClusterName,
                    "SAPPartyCode":a.SAPPartyCode 
                      
                })
           
                # log_entry = create_transaction_logNew(request,TargetData, PartyDetails, f'TargetVSAchievement of Month: {Month} Year: {Year} Party: {PartyDetails} Employee: {Employee}', 357, 0)
                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetAchievementList})
            else:
                log_entry = create_transaction_logNew(request,0,0,'TargetVSAchievement Does Not Exist',357,0)
                return Response({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'TargetVSAchievement:'+str(e),33,0)
            return Response({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
