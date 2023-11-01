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
from rest_framework.parsers import JSONParser

class FileDownloadView(View):
    def get(self, request,id=0):
        # Imagedata = JSONParser().parse(request)
        # link = Imagedata['link']
        # # Replace 'image_url' with the actual URL of the image you want to download.
        # image_url = link
        query = M_PartySettingsDetails.objects.filter(id=id).values('Image')
        Image = query[0]['Image']
        image_url = f'http://cbmfooderp.com:8000/media/{Image}'
        
        try:
            response = requests.get(image_url)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            return HttpResponse(f"Error: {e}", status=500)

        # Set the content type of the response to match the image type (e.g., image/jpeg).
        content_type = response.headers.get('content-type', 'application/octet-stream')
        response_headers = {
            'Content-Type': content_type,
        }
       
        # Create an HttpResponse and set the filename in the Content-Disposition header.
        filename = os.path.basename(image_url)
        response = HttpResponse(response.content, content_type=content_type)
        # response['Content-Disposition'] = 'attachment; filename="{filename}"'
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        # Return the HttpResponse object.
        return response   


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
        

  