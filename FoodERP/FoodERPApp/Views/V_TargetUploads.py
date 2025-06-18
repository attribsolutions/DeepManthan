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
import calendar


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
                    month_name = calendar.month_name[Month]
                    message = f"Target Data has already been uploaded for {month_name} {Year}"
                    return JsonResponse({'StatusCode': 226, 'Status': True, 'Message': message, 'Data': [] })
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
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': [] })


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
            log_entry = create_transaction_logNew(request, 0, 0,'TargetData:'+str(e),33,0)
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
            log_entry = create_transaction_logNew(request, 0, 0,'Targetrdata:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})


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
            log_entry = create_transaction_logNew(request, 0,0,'TargetsNotDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})
        

def TargetVsAchiQurey(Party,Month,Year):
    TvaAQuery=f''' (SELECT I.Party_id,I.ItemID,TargetQuantity,TargetAmount,Quantity,Amount,CXQuantity,CXAmount,CXQuantity2,CXAmount2,CRNoteQuantity,CRNoteAmount,Month,Year 
  from 
(SELECT ItemID,Party Party_id from 
(select distinct Item_id ItemID  from M_ChannelWiseItems where PartyType_id in(SELECT distinct PartyType_id from M_Parties where id in ({Party}) and  M_Parties.SAPPartyCode is not null))s ,
(SELECT id Party, Name from M_Parties where id in ({Party}) and PartyType_id !=19 and  M_Parties.SAPPartyCode is not null)P )I 

left join 
  
  (select  Month,Year,Party_id,Item_id,Sum(QtyInKg) TargetQuantity,Sum(Amount) TargetAmount from T_TargetUploads
   where  Month={Month} and Year={Year} group by Item_id,Party_id )A
   on I.ItemID = A.Item_id and I.Party_id = A.Party_id
            
left join 
(select Customer_id ,Item_id ,Sum(TC_InvoiceItems.QtyInKg)Quantity,Sum(Amount)Amount from T_Invoices
 join TC_InvoiceItems ON TC_InvoiceItems.invoice_id=T_Invoices.id
 where Month(invoiceDate)={Month} and year(invoiceDate)={Year} and DeletedFromSAP=0 and Party_id in(select M_Parties.id from M_Parties join M_PartyType on M_PartyType.id=PartyType_id where M_PartyType.IsDivision=1 and M_PartyType.Company_id in(2,3)
 ) group by item_id,customer_id )B
 on I.ItemID = B.Item_id and I.Party_id = B.Customer_id
 
 left join 
(SELECT Customer_id ,Item_id ,Sum(TC_CreditDebitNoteItems.QtyInKg)CRNoteQuantity,Sum(Amount)CRNoteAmount
FROM T_CreditDebitNotes
JOIN TC_CreditDebitNoteItems ON TC_CreditDebitNoteItems.CRDRNote_id=T_CreditDebitNotes.id
WHERE Month(CRDRNoteDate)={Month} and year(CRDRNoteDate)={Year} and Party_id in(select M_Parties.id from M_Parties join M_PartyType on M_PartyType.id=PartyType_id where M_PartyType.IsDivision=1 and M_PartyType.Company_id in(2,3)
 ) group by item_id,customer_id)C 
on I.ItemID = C.Item_id and I.Party_id = C.Customer_id 

left join
(select Party_id ,Item_id ,Sum(TC_InvoiceItems.QtyInKg)CXQuantity,Sum(Amount)CxAmount from T_Invoices
 join TC_InvoiceItems ON TC_InvoiceItems.invoice_id=T_Invoices.id
 join M_Parties on M_Parties.id=T_Invoices.Customer_id and M_Parties.PartyType_id = 15
 where Month(invoiceDate)={Month} and year(invoiceDate)={Year} and DeletedFromSAP=0 group by item_id,Party_id )E
 on I.ItemID = E.Item_id and I.Party_id = E.Party_id

 left join
(select Customer_id ,Item_id ,Sum(TC_InvoiceItems.QtyInKg)CXQuantity2,Sum(Amount)CxAmount2 from T_Invoices
 join TC_InvoiceItems ON TC_InvoiceItems.invoice_id=T_Invoices.id
 join M_Parties on M_Parties.id=T_Invoices.Customer_id and M_Parties.PartyType_id = 15
 where Month(invoiceDate)={Month} and year(invoiceDate)={Year} and DeletedFromSAP=0 group by item_id,Customer_id )EE
 on I.ItemID = EE.Item_id and I.Party_id = EE.Customer_id

WHERE (TargetQuantity>0 OR Quantity>0 OR  CRNoteQuantity >0)
Order By I.Party_id,ItemID)D'''
    return TvaAQuery



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
            Cluster =TargetData.get('Cluster')
            SubCluster = TargetData.get('SubCluster') 
            
            if Party == 0:
                Party=GetPartyOnSubclusterandclusterAndEmployee(Cluster,SubCluster,Employee,1)
            else :
                Party=Party
            
            # if Employee > 0 and Party == 0:
            #         EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[Employee])
            #         for row in EmpPartys:
            #             p=row.id
            #         Party_ID = p.split(",")
            #         dd=Party_ID[:-1]
            #         Party=', '.join(dd)
            
            # wherecondition = ""        
            
            
            # if int(Cluster) > 0:
                
            #     wherecondition = f"""and M_Cluster.id={Cluster}  """
            
            # if int(SubCluster) > 0:
                
            #     wherecondition = f"""and M_Cluster.id={Cluster} and  M_SubCluster.id={SubCluster} """
            

            
            
            query = T_TargetUploads.objects.raw(f''' select id,Year,FY,PartyID,ItemID,ItemName,ItemGroupName,SubGroupName,ClusterName,SubClusterName,
            SAPPartyCode,PartyName, (AchQuantity-CRNoteQuantity) AchQuantity,(AchAmount-CRNoteAmount)AchAmount,TargetQuantityInKG,TargetAmount,
            CXQuantity,CXAmount,CRNoteQuantity,CRNoteAmount,SAPItemCode ,
            ((AchQuantity-CRNoteQuantity)-CXQuantity)GTAchQuantity,
            ((AchAmount- CRNoteAmount)-CXAmount)GTAchAmount
            
            from 
            (SELECT 1 id,CONCAT(DATE_FORMAT(CONCAT({Year}, '-', {Month}, '-01'), '%%b'), '-', {Year}) AS Year,
            (CASE WHEN {Month} >= 4 THEN CONCAT({Year}, '-', {Year} + 1) ELSE CONCAT({Year} - 1, '-', {Year}) END) AS FY,D.Party_id PartyID,ItemID, M_Items.Name ItemName,M_Group.Name ItemGroupName,
            MC_SubGroup.Name SubGroupName,M_Cluster.Name ClusterName,
            M_SubCluster.Name SubClusterName,M_Parties.SAPPartyCode,M_Parties.Name PartyName ,
            Round(IFNULL(TargetQuantity,0),3)TargetQuantityInKG,Round(IFNULL(TargetAmount,0),2)TargetAmount,Round(IFNULL(Quantity,0),3)AchQuantity,
            Round(IFNULL(Amount,0),2)AchAmount,Round(IFNULL(CXQuantity,0)+IFNULL(CXQuantity2,0),3)CXQuantity,
            Round(IFNULL(CXAmount,0)+IFNULL(CXAmount2,0),2)CXAmount,Round(IFNULL(CRNoteQuantity,0),3)CRNoteQuantity,Round(IFNULL(CRNoteAmount,0),2)CRNoteAmount 
            ,M_Items.SAPItemCode
            FROM
  
  {TargetVsAchiQurey(Party,Month,Year)}

join  M_Items ON M_Items.id=D.ItemID
join MC_ItemGroupDetails  ON MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1
join  M_Group  ON M_Group.id=MC_ItemGroupDetails.Group_id
join  MC_SubGroup ON MC_SubGroup.id=MC_ItemGroupDetails.SubGroup_id
join M_PartyDetails ON M_PartyDetails.Party_id=D.Party_id
join M_Cluster ON M_Cluster.id=M_PartyDetails.Cluster_id
join M_SubCluster ON  M_SubCluster.id=M_PartyDetails.SubCluster_id
join M_Parties  ON M_Parties.id=D.Party_id
where MC_ItemGroupDetails.GroupType_id=1  and M_PartyDetails.Group_id is null  )v
            ''')
            TargetAchievementList = []   
            
            # print(query)

            if query:   
                for a in query:
                    
                    TargetAchievementList.append({
                    "id": a.id,
                    "Year": a.Year,
                    "Fy":a.FY,
                    "TargetQuantityInKG": a.TargetQuantityInKG,
                    "TargetAmountWithGST" : a.TargetAmount,
                    "AchQuantityInKG":a.AchQuantity,
                    "AchAmountWithGST":a.AchAmount,
                    "CXQuantityInKG":a.CXQuantity,
                    "CXAmountWithGST":a.CXAmount,
                    "CreditNoteQuantityInKG" : a.CRNoteQuantity,
                    "CreditNoteAmountWithGST" :a.CRNoteAmount,
                    "GTAchQuantityInKG" : a.GTAchQuantity,
                    "GTAchAmountWithGST" : a.GTAchAmount,
                    "PartyName": a.PartyName,
                    "ItemName": a.ItemName,
                    "ItemGroup": a.ItemGroupName,
                    "ItemSubGroup": a.SubGroupName,
                    "Cluster": a.ClusterName,
                    "SubCluster": a.SubClusterName,
                    "PartyID": a.PartyID,
                    "SAPPartyCode":a.SAPPartyCode ,
                    "ItemID" : a.ItemID,
                    "SAPItemCode" : a.SAPItemCode

                      
                })
           
                log_entry = create_transaction_logNew(request,TargetData, 0, f'TargetVSAchievement of Month: {Month} Year: {Year} Employee: {Employee}', 357, 0)
                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetAchievementList})
            else:
                log_entry = create_transaction_logNew(request,0,0,'TargetVSAchievement Does Not Exist',357,0)
                return Response({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'TargetVSAchievement:'+str(e),33,0)
            return Response({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


class TargetVSAchievementGroupwiseView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request, id=0):
        try:
            TargetData = request.data
            Month = TargetData.get('Month')
            Year = TargetData.get('Year')
            Party = TargetData.get('Party')
            Employee = TargetData.get('Employee')     
                
            Cluster =TargetData.get('Cluster')
            SubCluster = TargetData.get('SubCluster')       

            if Party == 0:

                Party=GetPartyOnSubclusterandclusterAndEmployee(Cluster,SubCluster,Employee,1) 
            else :
                Party=Party
            # if Employee > 0 and Party == 0:
            #         EmpPartys=MC_EmployeeParties.objects.raw('''select EmployeeParties(%s) id''',[Employee])
            #         for row in EmpPartys:
            #             p=row.id
            #         Party_ID = p.split(",")
            #         dd=Party_ID[:-1]
            #         Party=', '.join(dd)

            # wherecondition = ""        
            # if int(Cluster) > 0:
                
            #     wherecondition = f"""and M_PartyDetails.Cluster_id={Cluster}  """
            
            # if int(SubCluster) > 0:
                
            #     wherecondition = f"""and M_PartyDetails.Cluster_id={Cluster} and  M_PartyDetails.SubCluster_id={SubCluster} """        
                    
            query = T_TargetUploads.objects.raw(f'''select id,ItemGroupName,(AchQuantity-CRNoteQuantity)AchQuantity, (AchAmount- CRNoteAmount)AchAmount,
        CXQuantity,CXAmount,TargetQuantityInKG,TargetAmount,
        ((AchQuantity-CRNoteQuantity)-CXQuantity)GTAchQuantity,
        ((AchAmount- CRNoteAmount)-CXAmount)GTAchAmount,
        CRNoteQuantity,CRNoteAmount
        
        from (
                                                
            select  1 as id,M_Group.Name ItemGroupName,
            Round(IFNULL(sum(Quantity),0),3)AchQuantity,Round(IFNULL(sum(Amount),0),2)AchAmount,
            Round(IFNULL(sum(CXQuantity),0)+IFNULL(sum(CXQuantity2),0),3)CXQuantity,Round(IFNULL(sum(CXAmount),0)+IFNULL(sum(CXAmount2),0),2)CXAmount,
            Round(IFNULL(sum(TargetQuantity),0),3)TargetQuantityInKG,Round(IFNULL(sum(TargetAmount),0),2)TargetAmount,
            (Round(IFNULL(sum(Quantity),0),3)-Round(IFNULL(sum(CXQuantity),0),3))GTAchQuantity,
            (Round(IFNULL(sum(Amount),0),2)-Round(IFNULL(sum(CXAmount),0),2))GTAchAmount,
            Round(IFNULL(sum(CRNoteQuantity),0),3)CRNoteQuantity,Round(IFNULL(sum(CRNoteAmount),0),2)CRNoteAmount
from 

{TargetVsAchiQurey(Party,Month,Year)}
   
join  M_Items ON M_Items.id=D.ItemID
join MC_ItemGroupDetails  ON MC_ItemGroupDetails.Item_id=M_Items.id and MC_ItemGroupDetails.GroupType_id=1
join  M_Group  ON M_Group.id=MC_ItemGroupDetails.Group_id
join M_PartyDetails ON M_PartyDetails.Party_id=D.Party_id
 
where MC_ItemGroupDetails.GroupType_id=1  and M_PartyDetails.Group_id is null

group by M_Group.id )v
  
            ''')
            TargetAchievementList = []   
            # print(query)
            TotalGTAchQuantity=0
            TotalGTAchAmount=0
            if query:   
                for aa in query:
                  TotalGTAchQuantity = TotalGTAchQuantity + aa.GTAchQuantity
                  TotalGTAchAmount = TotalGTAchAmount + aa.GTAchAmount
                for a in query:
                    
                    TargetAchievementList.append({
                    "id": a.id,
                    "ItemGroup": a.ItemGroupName,
                    "AchQuantityInKG":a.AchQuantity,
                    "AchAmountWithGST":a.AchAmount,
                    "CXQuantityInKG":a.CXQuantity,
                    "CXAmountWithGST":a.CXAmount,
                    "TargetQuantityInKG": a.TargetQuantityInKG,
                    "GTAchQuantityInKG" : a.GTAchQuantity,
                    "AchQty%" :  0 if a.TargetQuantityInKG ==0 else round((a.GTAchQuantity/a.TargetQuantityInKG)*100,2),
                    "ContriQty%" : 0 if TotalGTAchQuantity==0 else  round((a.GTAchQuantity/TotalGTAchQuantity)*100,2),
                    "TargetAmountWithGST" : a.TargetAmount,
                    "GTAchAmountWithGST" : a.GTAchAmount,
                    "AchAmount%" : 0 if a.TargetAmount == 0 else round((a.GTAchAmount/a.TargetAmount)*100,2),
                    "ContriAmount%" : 0 if TotalGTAchAmount == 0 else round((a.GTAchAmount/TotalGTAchAmount)*100,2),
                    "CreditNoteQuantityInKG" : a.CRNoteQuantity,
                    "CreditNoteAmountWithGST" :a.CRNoteAmount,
                    
                      
                })
           
                log_entry = create_transaction_logNew(request,TargetData, 0, f'TargetVSAchievement of Month: {Month} Year: {Year} Employee: {Employee}', 357, 0)
                return Response({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': TargetAchievementList})
            else:
                log_entry = create_transaction_logNew(request,0,0,'TargetVSAchievement Does Not Exist',357,0)
                return Response({'StatusCode': 204, 'Status': True, 'Message': 'Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'TargetVSAchievement:'+str(e),33,0)
            return Response({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


def GetPartyOnSubclusterandclusterAndEmployee(ClusterID,SubClusterID,EmployeeID,Mode):

    wherecondition = ""
    if not ClusterID:
        wherecondition += ""
    else:
        wherecondition +=  f"""and M_PartyDetails.Cluster_id in( {ClusterID})  """
    
    
    if not SubClusterID:
        wherecondition += "" 
    else:
        wherecondition += f""" and  M_PartyDetails.SubCluster_id in( {SubClusterID}) """
    
    
    # isSaleTeamMembrt_result = M_Employees.objects.filter(id=EmployeeID,Designation__TypeID=161,Designation__Name=['ASM','GM','MT','NH','RH','SO', 'SE','SR']).select_related('Designation').values('Designation__Name')
    isSaleTeamMembrt_result = M_Employees.objects.raw(f'''select 1 as id,  M_Employees.Designation,M_GeneralMaster.Name from M_Employees 
left  join M_GeneralMaster on M_GeneralMaster.id=M_Employees.Designation and M_GeneralMaster.TypeID=161
where M_Employees.id={EmployeeID} and M_GeneralMaster.Name in('ASM','GM','MT','NH','RH','SO', 'SE','SR')''')
    
    if isSaleTeamMembrt_result :
        
        
        for row in isSaleTeamMembrt_result:
            designation=row.Name
       
        q2=M_PartyDetails.objects.raw(f'''Select  M_Parties.id,M_Parties.Name from M_PartyDetails 
                                        join M_Parties on M_Parties.id=M_PartyDetails.Party_id 
                                        where Group_id is null and  {designation} = {EmployeeID} {wherecondition}''')
    else:
        
        EmpPartys=MC_EmployeeParties.objects.raw(f'''select EmployeeParties({EmployeeID}) id''')
        for row in EmpPartys:
            p=row.id
        Party_ID = p.split(",")
        dd=Party_ID[:-1]
        Party=', '.join(dd)
        
        if Party:
            
            q2=M_Parties.objects.raw(f'''select M_Parties.id  ,Name from M_Parties
                                    join M_PartyDetails on M_PartyDetails.Party_id=M_Parties.id
                                    where Group_id is null and  M_Parties.id in ({Party}) {wherecondition}''')
        else:
            
            q2=MC_EmployeeParties.objects.raw(f'''SELECT M_Parties.id,M_Parties.Name FROM MC_EmployeeParties 
                                                    join M_Parties on M_Parties.id=MC_EmployeeParties.Party_id 
                                                    where Employee_id={EmployeeID}''')
    
    if Mode == 1:
        PartyList=0
        PartyID_list = [str(a.id) for a in q2]
        PartyList = ','.join(PartyID_list)
    
    else:
        PartyList=list()
        for a in q2:
            PartyList.append({
                "PartyID" : a.id,
                "PartyName" : a.Name

            })
    
    return PartyList;

class GetPartyOnSubclusterandclusterAndEmployeeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        Request_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
                ClusterID= Request_data['ClusterID']
                SubClusterID= Request_data['SubClusterID']
                EmployeeID= Request_data['EmployeeID']

                PartyList=GetPartyOnSubclusterandclusterAndEmployee(ClusterID,SubClusterID,EmployeeID,2)
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyList})  
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0, 0,'ItemSaleReport:'+str(Exception(e)),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data': []})                