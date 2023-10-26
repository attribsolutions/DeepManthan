from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_PartyDetails import *
from ..models import *

class PartyDetailsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic()
    def post(self, request ):
        try:
            with transaction.atomic():
                PartyDetails_data = JSONParser().parse(request)
                PartyDetails_serializer = PartyDetailsSerializer(data=PartyDetails_data)
                if PartyDetails_serializer.is_valid():
                    PartyDetails_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyDetails Data Uploaded Successfully', 'Data': []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyDetails_serializer.errors, 'Data': []})
        except Exception as e:
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

  


    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                PartyDetails_data = JSONParser().parse(request)
                PartyDetails_datadataByID = M_PartyDetails.objects.get(id=id)
                PartyDetails_serializer = PartyDetailsSerializer(
                    PartyDetails_datadataByID, data=PartyDetails_data)
                if PartyDetails_serializer.is_valid():
                    PartyDetails_serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'PartyDetails Data Updated Successfully','Data' :[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': PartyDetailsSerializer.errors, 'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})
        

  