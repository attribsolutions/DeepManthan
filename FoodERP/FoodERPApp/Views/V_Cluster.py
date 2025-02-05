from django.http import JsonResponse
from django.http import HttpResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Views.V_CommFunction import *
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from ..Serializer.S_Cluster import *
from ..models import *
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

class ClusterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        Cluster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Cluster_data_serializer = ClusterSerializer(data=Cluster_data)
                if Cluster_data_serializer.is_valid():
                    Cluster_data_serializer.save()
                    log_entry = create_transaction_logNew(request, Cluster_data,0,'',327,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Uploaded Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, Cluster_data,0,'CategorySave:'+str(Cluster_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Cluster_data_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Cluster_data, 0,'ClusterSave:'+str(e),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                
                Cluster_data = M_Cluster.objects.all()
                Cluster_data_serializer = ClusterSerializer(Cluster_data,many=True)
                log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',328,0)
                return JsonResponse({'StatusCode': 999, 'Status': True,'Message': '', 'Data': Cluster_data_serializer.data})
        except  M_Cluster.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Cluster Data Does Not Exist',328,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Cluster Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
    
class ClusterViewsecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = M_Cluster.objects.get(id=id)
                Cluster_data_serializer = ClusterSerializer(Cluster_data)
                log_entry = create_transaction_logNew(request, Cluster_data_serializer,0,'',329,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Cluster_data_serializer.data})
        except  M_Cluster.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'Cluster Data Does Not Exist',329,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Cluster Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETSingleCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        


    @transaction.atomic()
    def put(self, request, id=0):
        Cluster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Cluster_datadataByID = M_Cluster.objects.get(id=id)
                Cluster_data_serializer = ClusterSerializer(
                    Cluster_datadataByID, data=Cluster_data)
                if Cluster_data_serializer.is_valid():
                    Cluster_data_serializer.save()
                    log_entry = create_transaction_logNew(request, Cluster_data,0,'ClusterID:'+str(id),330,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, Cluster_data,0,'ClusterEdit:'+str(Cluster_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Cluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Cluster_data, 0,'ClusterEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def patch(self, request, id=0):
        Cluster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                Cluster_datadataByID = M_Cluster.objects.get(id=id)
                Cluster_data_serializer = ClusterSerializer(
                Cluster_datadataByID, data=Cluster_data, partial=True)  # Set partial=True
                if Cluster_data_serializer.is_valid():
                   Cluster_data_serializer.save()
                   log_entry = create_transaction_logNew(request, Cluster_data,0,'ClusterID:'+str(id),331,0)
                   return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Partially Updated Successfully','Data' :[]})
                else:
                   log_entry = create_transaction_logNew(request, Cluster_data,0,'ClusterPartialEdit:'+str(Cluster_data_serializer.errors),34,0)
                   transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Cluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, Cluster_data, 0,'ClusterPartialEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Cluster_data = M_Cluster.objects.get(id=id)
                Cluster_data.delete()
                log_entry = create_transaction_logNew(request, 0,0,'ClusterID:'+str(id),332,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Cluster Data Deleted Successfully','Data':[]})
        except M_Cluster.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'Cluster Data Not available',332,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Cluster Data Not available', 'Data': []})
        except IntegrityError:  
            log_entry = create_transaction_logNew(request, 0,0,'Cluster Data used in another table',8,0)    
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Cluster Data used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'ClusterDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})   

        

    
class SubClusterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        SubCluster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                SubCluster_data_serializer = SubClusterSerializer(data=SubCluster_data)
                if SubCluster_data_serializer.is_valid():
                    SubCluster_data_serializer.save()
                    log_entry = create_transaction_logNew(request, SubCluster_data,0,'',333,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Uploaded Successfully', 'Data': []})
                else:
                    log_entry = create_transaction_logNew(request, SubCluster_data,0,'SubClusterSave:'+str(SubCluster_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubCluster_data_serializer.errors, 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, SubCluster_data, 0,'SubClusterSave:'+str(e),33,0)
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                query = M_SubCluster.objects.all()
                if query.exists():
                    SubCluster_data = SubClusterSerializerSecond(query, many=True).data
                    SubclusterList=list()
                    for a in SubCluster_data:
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
                        log_entry = create_transaction_logNew(request, SubCluster_data,0,'',334,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubclusterList})
                log_entry = create_transaction_logNew(request,0,0,'SubCluster Data Does Not Exist',334,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'SubCluster Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETAllSubCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
    
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
                    log_entry = create_transaction_logNew(request, Subclusterdata,0,'',335,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': SubclusterList[0]})
                log_entry = create_transaction_logNew(request,0,0,'Subcluster Data Does Not Exist',335,0)
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Sub Cluster Not available ', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GETSingleSubCluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
#USE OF MAP FUNCTION 

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
        SubCluster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                SubCluster_datadataByID = M_SubCluster.objects.get(id=id)
                SubCluster_data_serializer = SubClusterSerializer(
                   SubCluster_datadataByID, data=SubCluster_data)
                if SubCluster_data_serializer.is_valid():
                    SubCluster_data_serializer.save()
                    log_entry = create_transaction_logNew(request, SubCluster_data,0,'SubClusterID:'+str(id),336,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Updated Successfully','Data' :[]})
                else:
                    log_entry = create_transaction_logNew(request, SubCluster_data,0,'SubClusterEdit:'+str(SubCluster_data_serializer.errors),34,0)
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubCluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, SubCluster_data, 0,'SubClusterEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def patch(self, request, id=0):
        SubCluster_data = JSONParser().parse(request)
        try:
            with transaction.atomic():
                SubCluster_datadataByID = M_SubCluster.objects.get(id=id)
                SubCluster_data_serializer = SubClusterSerializer(
                SubCluster_datadataByID, data=SubCluster_data, partial=True)  # Set partial=True
                if SubCluster_data_serializer.is_valid():
                   SubCluster_data_serializer.save()
                   log_entry = create_transaction_logNew(request, SubCluster_data,0,'SubClusterID:'+str(id),337,0)
                   return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Partially Updated Successfully','Data' :[]})
                else:
                   log_entry = create_transaction_logNew(request, SubCluster_data,0,'SubClusterPartialEdit:'+str(SubCluster_data_serializer.errors),34,0)
                   transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': SubCluster_data_serializer.errors, 'Data' :[]})
        except Exception as e:
            log_entry = create_transaction_logNew(request, SubCluster_data, 0,'SubClusterPartialEdit:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = M_SubCluster.objects.get(id=id)
                SubCluster_data.delete()
                log_entry = create_transaction_logNew(request, 0,0,'SubClusterID:'+str(id),338,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'SubCluster Data Deleted Successfully','Data':[]})
        except M_SubCluster.DoesNotExist:
            log_entry = create_transaction_logNew(request, 0,0,'SubCluster Data Not available',338,0)
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'SubCluster Data Not available', 'Data': []})
        except IntegrityError: 
            log_entry = create_transaction_logNew(request, 0,0,'SubCluster Data used in another table',8,0)      
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'SubCluster Data used in another table', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'SubClusterDeleted:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})   
       

class GetSubClusterOnclusterView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = M_SubCluster.objects.filter(Cluster=id)
                SubCluster_data_serializer = SubClusterSerializer(SubCluster_data,many=True).data
                log_entry = create_transaction_logNew(request, SubCluster_data_serializer,0,'',339,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': SubCluster_data_serializer})
        except  M_SubCluster.DoesNotExist:
            log_entry = create_transaction_logNew(request,0,0,'SubCluster Does Not Exist',339,0)
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'SubCluster Data Not available', 'Data': []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,'GetSubClusterOncluster:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})    




         