from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from ..Serializer.S_PageAccess import H_PageAccessSerializer
from ..models import *
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import HttpResponse
from django.views import View
class H_PageAccessView(CreateAPIView):    
    permission_classes = (IsAuthenticated,)
    @transaction.atomic() 
      
    def get(self, request):
        try:
            with transaction.atomic():
                cached_result = cache.get(request)
                if cached_result is not None:                     
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': cached_result})
                else:                    
                    H_PageAccess_data = H_PageAccess.objects.all().order_by('Sequence')
                    if H_PageAccess_data.exists():
                        H_PageAccess_serializer = H_PageAccessSerializer(H_PageAccess_data, many=True)
                    
                    
                        result = H_PageAccess_serializer.data
                        cache.set(request, result, timeout=3600)  # Cache for 1 hour
                        return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '','Data': H_PageAccess_serializer.data })
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Page Access Not available', 'Data': []})
      
        except Exception as e:
                return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})
                
               