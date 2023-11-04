from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Cluster import *
from ..models import *

class ClusterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                Cluster_data = JSONParser().parse(request)
                Cluster_data_serializer = ClusterSerializer(data=Cluster_data)
                if Cluster_data_serializer.is_valid():
                    Cluster_data_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Uploaded Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Cluster_data_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                
                Cluster_data = M_Cluster.objects.all()
         
                Cluster_data_serializer = ClusterSerializer(Cluster_data,many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Cluster_data_serializer.data})
        except  M_Cluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  ' Cluster Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
    
class ClusterViewsecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = M_Cluster.objects.get(id=id)
                Cluster_data_serializer = ClusterSerializer(Cluster_data)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Cluster_data_serializer.data})
        except  M_Cluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Cluster Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = JSONParser().parse(request)
                Cluster_datadataByID = M_Cluster.objects.get(id=id)
                Cluster_data_serializer = ClusterSerializer(
                    Cluster_datadataByID, data=Cluster_data)
                if Cluster_data_serializer.is_valid():
                    Cluster_data_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Cluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def patch(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = JSONParser().parse(request)
                Cluster_datadataByID = M_Cluster.objects.get(id=id)
                Cluster_data_serializer = ClusterSerializer(
                Cluster_datadataByID, data=Cluster_data, partial=True)  # Set partial=True
                if Cluster_data_serializer.is_valid():
                   Cluster_data_serializer.save()
                   return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Updated Successfully','Data' :[]})
                else:
                   transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Cluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = M_Cluster.objects.get(id=id)
                Cluster_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Deleted Successfully','Data':[]})
        except M_Cluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Cluster Data Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Cluster Data used in another table', 'Data': []})
        

    
class SubClusterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                SubCluster_data = JSONParser().parse(request)
                SubCluster_data_serializer = SubClusterSerializer(data=SubCluster_data)
                if SubCluster_data_serializer.is_valid():
                    SubCluster_data_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Uploaded Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubCluster_data_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_SubCluster.objects.all()
                if query.exists():
                    Groupdata = SubClusterSerializerSecond(query, many=True).data
                    GroupList=list()
                    for a in Groupdata:
                        GroupList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "Cluster": a['Cluster']['id'],
                            "ClusterName": a['Cluster']['Name'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': GroupList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SubCluster Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
        
    
class SubClusterViewsecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_SubCluster.objects.filter(id=id)
                Subclusterdata = SubClusterSerializerSecond(query, many=True).data
                SubclusterList=list()
                for a in Subclusterdata:
                    SubclusterList.append({
                        "id": a['id'],
                        "Name": a['Name'],
                        "Cluster": a['Cluster']['id'],
                        "ClusterName": a['Cluster']['Name'],
                        "CreatedBy": a['CreatedBy'],
                        "CreatedOn": a['CreatedOn'],
                        "UpdatedBy": a['UpdatedBy'],
                        "UpdatedOn": a['UpdatedOn']
                    })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubclusterList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Sub Cluster Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

# class SubClusterViewsecond(CreateAPIView):
#     permission_classes = (IsAuthenticated,)
#     @transaction.atomic()
#     def get(self, request, id=0):
#         try:
#             with transaction.atomic():
#                 query = M_SubCluster.objects.filter(id=id)
#                 Subclusterdata = SubClusterSerializerSecond(query, many=True).data

#                 SubclusterList = list(map(lambda a: {
#                     "id": a['id'],
#                     "Name": a['Name'],
#                     "Cluster": a['Cluster']['id'],
#                     "ClusterName": a['Cluster']['Name'],
#                     "CreatedBy": a['CreatedBy'],
#                     "CreatedOn": a['CreatedOn'],
#                     "UpdatedBy": a['UpdatedBy'],
#                     "UpdatedOn": a['UpdatedOn']
#                 }, Subclusterdata))

#                 if SubclusterList:
#                     return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubclusterList[0]})
#                 else:
#                     return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Sub Cluster Not available ', 'Data': []})

#         except Exception as e:
#             return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = JSONParser().parse(request)
                SubCluster_datadataByID = M_SubCluster.objects.get(id=id)
                SubCluster_data_serializer = SubClusterSerializer(
                   SubCluster_datadataByID, data=SubCluster_data)
                if SubCluster_data_serializer.is_valid():
                    SubCluster_data_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubCluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def patch(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = JSONParser().parse(request)
                SubCluster_datadataByID = M_SubCluster.objects.get(id=id)
                SubCluster_data_serializer = SubClusterSerializer(
                SubCluster_datadataByID, data=SubCluster_data, partial=True)  # Set partial=True
                if SubCluster_data_serializer.is_valid():
                   SubCluster_data_serializer.save()
                   return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Updated Successfully','Data' :[]})
                else:
                   transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubCluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = M_SubCluster.objects.get(id=id)
                SubCluster_data.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Deleted Successfully','Data':[]})
        except M_SubCluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'SubCluster Data Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'SubCluster Data used in another table', 'Data': []})
        

class GetSubClusterOnclusterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = M_SubCluster.objects.filter(Cluster=id)
                SubCluster_data_serializer = SubClusterSerializer(SubCluster_data,many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': SubCluster_data_serializer})
        except  M_SubCluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Cluster Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})  

class GetPartydetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, Employee=0,Group=0):
        try:
            with transaction.atomic():
                
                # if int(Employee) > 0:
                if Employee.isdigit() and int(Employee) > 0:

                    EmpParties = MC_ManagementParties.objects.filter(Employee=Employee).values('Party')
                    party_values = [str(record['Party']) for record in EmpParties]

                    # if Group > 0:
                    if Group.isdigit() and int(Group) > 0:

                        query = "Group_id = %s"
                        
                    else:
                        query = "Group_id IS NULL"
                        

                    PartydetailsOnclusterdata = (f'''select 1 as id, Party, PartyName, Group_id, Cluster_id, ClusterName, SubCluster_id, SubClusterName, Supplier_id, SupplierName from 
(select id Party,Name PartyName from M_Parties where PartyType_id in (9,10) and id in %s)a
left join 
(select  Party_id,M_PartyDetails.Group_id,M_PartyDetails.Cluster_id,M_Cluster.Name ClusterName,M_PartyDetails.SubCluster_id,M_SubCluster.Name SubClusterName,M_PartyDetails.Supplier_id ,a.Name SupplierName
from M_PartyDetails 
LEFT JOIN
    M_Cluster ON M_PartyDetails.Cluster_id = M_Cluster.id
        LEFT JOIN
    M_SubCluster ON M_PartyDetails.SubCluster_id = M_SubCluster.id
        LEFT JOIN
    M_Parties a ON a.id = M_PartyDetails.Supplier_id where {query})b 
on a.party=b.Party_id ''',(party_values, Group))
                    

                else:
                    
                    PartydetailsOnclusterdata = M_PartyDetails.objects.raw('''select 1 as id, Party, PartyName, Group_id, Cluster_id, ClusterName, SubCluster_id, SubClusterName, Supplier_id, SupplierName from 
(select id Party,Name PartyName from M_Parties where PartyType_id in (9,10) and id in %s)a
left join 
(select  Party_id,M_PartyDetails.Group_id,M_PartyDetails.Cluster_id,M_Cluster.Name ClusterName,M_PartyDetails.SubCluster_id,M_SubCluster.Name SubClusterName,M_PartyDetails.Supplier_id ,a.Name SupplierName
from M_PartyDetails 
LEFT JOIN
    M_Cluster ON M_PartyDetails.Cluster_id = M_Cluster.id
        LEFT JOIN
    M_SubCluster ON M_PartyDetails.SubCluster_id = M_SubCluster.id
        LEFT JOIN
    M_Parties a ON a.id = M_PartyDetails.Supplier_id where Group_id =%s)b 
on a.party=b.Party_id''',(party_values, Group))
                # print(PartydetailsOnclusterdata.query)
                if not PartydetailsOnclusterdata:
                    return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'Partydetails Not available', 'Data': []})
                PartydetailsOncluster_serializer =  GetPartydetailsSerializer(PartydetailsOnclusterdata, many=True).data
                # print(PartydetailsOncluster_serializer)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PartydetailsOncluster_serializer})
                
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []}) 
        

             
         


