from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyDetails import *
from ..models import *
from django.http import HttpResponse
from django.views import View
import requests
import os
from ..Views.V_CommFunction import *
from django.http import JsonResponse, FileResponse
from django.conf import settings


class FileDownloadView(View):
    permission_classes = (IsAuthenticated,)
    # authentication_classes = [JSONWebTokenAuthentication]

    def get(self, request, id=0, table=0):
        try:
            url_prefix = NewURLPrefix()

            # Map of table codes to model classes and image field names
            table_config = {
                1: (M_PartySettingsDetails, 'Image'),
                2: (T_ClaimTrackingEntry, 'CreditNoteUpload'),
                3: (TC_PurchaseReturnItemImages, 'Image'),
                4: (MC_PartyAddress, 'fssaidocumenturl')
            }

            model_class, field_name = table_config.get(int(table), (None, None))
            if not model_class:
                create_transaction_logNew(request, {'TableID': table}, id, 'Invalid table selection in FileDownloadView', 467)
                return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid table selection.', 'Data': []}, status=400)

            query = model_class.objects.filter(id=id).values(field_name)
            if not query.exists():
                create_transaction_logNew(request, {'TableID': table}, id, 'Image not found for given ID in FileDownloadView', 467)
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'No image found for the given ID.', 'Data': []}, status=404)

            image_path = query[0][field_name]
            if not image_path:
                create_transaction_logNew(request, {'TableID': table}, id, 'Image path is empty in FileDownloadView', 467)
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'No file found for the given ID.', 'Data': []}, status=404)

            # Build full file path from media root
            file_path = os.path.join(settings.MEDIA_ROOT, image_path)

            if not os.path.exists(file_path):
                create_transaction_logNew(request, {'TableID': table}, id, 'File not found on disk in FileDownloadView', 467)
                return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'File not found on server.', 'Data': []}, status=404)

            filename = os.path.basename(file_path)

            # Serve file directly from disk using FileResponse
            response = FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'

            create_transaction_logNew(request, {'TableID': table}, id, 'FileDownloadView file download successful', 467)
            return response

        except Exception as e:
            create_transaction_logNew(request, {'TableID': table}, id, f'FileDownloadView Exception: {str(e)}', 33)
            return JsonResponse({'StatusCode': 500, 'Status': False, 'Message': str(e), 'Data': []}, status=500)
        
# OLD API -> REMOVE THIS CODE AFTER SOME DAYS OF PROPER EXECUTION OF ABOVE NEW API CODE
# class FileDownloadView(View):
#     def get(self, request,id=0,table=0):
#         # Imagedata = JSONParser().parse(request)
#         # link = Imagedata['link']
#         # # Replace 'image_url' with the actual URL of the image you want to download.
#         # image_url = link
        
#         url_prefix = NewURLPrefix()
        
#         if int(table)==1: #M_PartySettingsDetails table
#             query = M_PartySettingsDetails.objects.filter(id=id).values('Image')
#             Image = query[0]['Image']

#             image_url = f"{url_prefix}/media/{Image}"
#             # image_url = f'https://cbmfooderp.com/api/media/{Image}'

#             # image_url = f'http://192.168.1.114:8000/media/{Image}'
            
#         elif int(table)==2:  #T_ClaimTrackingEntry
#             query = T_ClaimTrackingEntry.objects.filter(id=id).values('CreditNoteUpload')
#             Image = query[0]['CreditNoteUpload']
#             image_url = f"{url_prefix}/media/{Image}"
#             # image_url = f'https://cbmfooderp.com/api/media/{Image}'
#             # image_url = f'http://192.168.1.114:8000/media/{Image}'
            
#         else: # 3 TC_PurchaseReturnItemImages
#             '''check serializer PurchaseReturnItemImageSerializer2'''
#             query = TC_PurchaseReturnItemImages.objects.filter(id=id).values('Image')
#             Image = query[0]['Image']
#             image_url = f"{url_prefix}/media/{Image}"
#             # image_url = f'https://cbmfooderp.com/api/media/{Image}'
#             # image_url = f'http://192.168.1.114:8000/media/{Image}'  
            
#         try:
#             response = requests.get(image_url, verify=False)
#             response.raise_for_status()
#         except requests.exceptions.RequestException as e:
#             return HttpResponse(f"Error: {e}", status=500)

#         # Set the content type of the response to match the image type (e.g., image/jpeg).
#         content_type = response.headers.get('content-type', 'application/octet-stream')
#         response_headers = {
#             'Content-Type': content_type,
#         }
       
#         # Create an HttpResponse and set the filename in the Content-Disposition header.
#         filename = os.path.basename(image_url)
#         response = HttpResponse(response.content, content_type=content_type)
#         # response['Content-Disposition'] = 'attachment; filename="{filename}"'
#         response['Content-Disposition'] = f'attachment; filename="{filename}"'
#         # Return the HttpResponse object.
#         return response   


class PartyDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        PartyDetails_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                
         
                PartyDetails_serializer = PartyDetailsSerializer(data=PartyDetails_data, many=True)
               
                if PartyDetails_serializer.is_valid():
                    
                    party_ids = [entry['Party'] for entry in PartyDetails_data]

                    PartyDetailsdata = M_PartyDetails.objects.filter(Group=PartyDetails_data[0]['Group'],Party__in =party_ids)
                    # print(PartyDetailsdata.query)
                    PartyDetailsdata.delete()   
                    PartyDetails_serializer.save() 
                    log_entry = create_transaction_logNew(request, PartyDetails_data,0,'GroupID:'+str(PartyDetails_data[0]['Group']),446,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyDetails Data Updated Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, PartyDetails_data,0,'PartyDetails_Save:'+str(PartyDetails_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyDetails_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, PartyDetails_data, 0,'PartyDetailsSave:'+str(e),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
  


    # @transaction.atomic()
    # def put(self, request, id=0):
    #     PartyDetails_data = JSONParser().parse(request)
    #     try:
    #         with transaction.atomic():
                
    #             PartyDetails_datadataByID = M_PartyDetails.objects.get(id=id)
    #             PartyDetails_serializer = PartyDetailsSerializer(
    #                 PartyDetails_datadataByID, data=PartyDetails_data)
    #             if PartyDetails_serializer.is_valid():
    #                 PartyDetails_serializer.save()
    #                 log_entry = create_transaction_logNew(request, PartyDetails_data,0,'PartyDetailsID:'+str(id),447,0)
    #                 return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyDetails Data Updated Successfully','Data' :[]})
    #             else:
    #                 log_entry = create_transaction_logNew(request, PartyDetails_data,0,'PartyDetailsEdit:'+str(PartyDetails_serializer.errors),34,0)
    #                 transaction.set_rollback(True)
    #                 return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyDetailsSerializer.errors, 'Data' :[]})
    #     except Exception as e:
    #         log_entry = create_transaction_logNew(request, PartyDetails_data, 0,'PartyDetailsEdit:'+str(e),33,0)
    #         return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
def SalesTeamData(ID):
    if ID:
        EmpIDs=ID.split(',')
        query=M_Employees.objects.raw('''Select id ,Name from M_Employees where id in %s ''',([EmpIDs]))
        SalesTeamData=list()
        
        for emp in query:
            SalesTeamData.append({
                "value" : emp.id,
                "label" : emp.Name
            })            
        
        return SalesTeamData
    else:
        return ID

class GetPartydetailsView(CreateAPIView): 
    permission_classes = (IsAuthenticated,)
    def post(self, request):
        PartyDetails_data = JSONParser().parse(request)
        Employee=PartyDetails_data['employeeID']
        Party=PartyDetails_data['Party']
        Group=PartyDetails_data['groupID']
        Cluster=PartyDetails_data['Cluster']       
        
        try:
            with transaction.atomic():
                PartyDetailData= list()
                if Party==0:
                    # EmpParties = MC_ManagementParties.objects.filter(Employee=Employee).values('Party')                
                    # party_values = [str(record['Party']) for record in EmpParties]
                    party_values=""
                else:
                    party_values =f"AND M_Parties.id={Party}"                     
                    
                if Cluster==0:
                    Cluster_value=""
                else:
                    Cluster_value=f"AND M_Cluster.id ={Cluster}"               
                    
                
                if int(Group) > 0:
                    Group_value=f" Group_id = {Group}"
                else:
                    Group_value="Group_id IS NULL"                    
                                  
                PartydetailsOnclusterdata = M_PartyDetails.objects.raw(f'''select 1 as id, PartyID, PartyName, Group_id, Cluster_id, ClusterName, SubCluster_id, SubClusterName, Supplier_id, SupplierName, GM, NH, RH, ASM, SE, SO, SR, MT from 
                                                                            (select id PartyID,Name PartyName from M_Parties where PartyType_id in (9,10,15,19) {party_values})a
                                                                             join 
                                                                            (select  Party_id,M_PartyDetails.Group_id,M_PartyDetails.Cluster_id,M_Cluster.Name ClusterName,M_PartyDetails.SubCluster_id,
                                                                            M_SubCluster.Name SubClusterName,M_PartyDetails.Supplier_id ,a.Name SupplierName, M_PartyDetails.GM, M_PartyDetails.NH,
                                                                            M_PartyDetails.RH, M_PartyDetails.ASM, M_PartyDetails.SE, M_PartyDetails.SO, M_PartyDetails.SR, M_PartyDetails.MT
                                                                            from M_PartyDetails 
                                                                            LEFT JOIN M_Cluster ON M_PartyDetails.Cluster_id = M_Cluster.id
                                                                            LEFT JOIN M_SubCluster ON M_PartyDetails.SubCluster_id = M_SubCluster.id
                                                                            LEFT JOIN M_Employees ON M_PartyDetails.id = M_Employees.id
                                                                            LEFT JOIN M_Parties a ON a.id = M_PartyDetails.Supplier_id
                                                                            where {Group_value} {Cluster_value} )b on a.partyID=b.Party_id  ''')
                
                # print(PartydetailsOnclusterdata.query)
                if PartydetailsOnclusterdata:
                    
                    for row in PartydetailsOnclusterdata:
                        supplierData=list()
                        
                        supplierDataQuery=MC_PartySubParty.objects.raw('''Select M_Parties.id,M_Parties.Name from MC_PartySubParty join M_Parties on M_Parties.id=MC_PartySubParty.Party_id where SubParty_id=%s''',([row.PartyID]))
                        for a in supplierDataQuery:
                            seletedSupplier=0
                            if a.id == row.Supplier_id:
                                seletedSupplier=1
                            supplierData.append({
                                "Supplier_id" : a.id,
                                "SupplierName" : a.Name,
                                "seletedSupplier" : seletedSupplier
                            })                              
                        PartyDetailData.append({
                                "id": row.id,
                                "PartyID": row.PartyID,
                                "PartyName": row.PartyName,
                                "Group_id": row.Group_id,
                                "Cluster_id": row.Cluster_id,
                                "ClusterName": row.ClusterName,
                                "SubCluster_id": row.SubCluster_id,
                                "SubClusterName": row.SubClusterName,
                                "Supplier": supplierData,
                                # "SupplierName": row.SupplierName,
                                "GM": SalesTeamData(row.GM),
                                "NH": SalesTeamData(row.NH),
                                "RH": SalesTeamData(row.RH),
                                "ASM": SalesTeamData(row.ASM),
                                "SE": SalesTeamData(row.SE),
                                "SO": SalesTeamData(row.SO),
                                "SR": SalesTeamData(row.SR),
                                "MT": SalesTeamData(row.MT),
                                })
                    
                    log_entry = create_transaction_logNew(request, PartyDetailData,0,'GroupID:'+str(Group),445,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartyDetailData})
                else:  
                    log_entry = create_transaction_logNew(request,0,0,'PartyDetailData Does Not Exist',445,0)
                    return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'Partydetails Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'PartyDetailData:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': (e), 'Data': []}) 
        
  