from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from ..Serializer.S_Units import *
from ..models import *

class M_UnitsView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                UnitNamedata = M_Units.objects.all()
                if UnitNamedata.exists():
                    Units_Serializer = M_UnitsSerializer(UnitNamedata, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': Units_Serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Companies Not Available', 'Data': []})    
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



