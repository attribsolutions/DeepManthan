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
    # authentication_classes = [BasicAuthentication]
    # parser_classes = (MultiPartParser, FormParser)

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
    # authentication_classes = [BasicAuthentication]
    # parser_classes = (MultiPartParser, FormParser)

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
    def get(self, request):
        try:
            with transaction.atomic():
                SubCluster_data = M_SubCluster.objects.all()
         
                SubCluster_data_serializer = ClusterSerializer(SubCluster_data,many=True)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': SubCluster_data_serializer.data})
        except  M_SubCluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'SubCluster Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        
    
class SubClusterViewsecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)

    

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                SubCluster_data = M_SubCluster.objects.get(id=id)
                SubCluster_data_serializer = SubClusterSerializer(SubCluster_data)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': SubCluster_data_serializer.data})
        except  M_SubCluster.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Cluster Data Not available', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        


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
        
         


