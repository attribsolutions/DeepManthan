from rest_framework.views import APIView
from django.http import JsonResponse
from ..models import M_ERPUrls, MC_ERPUrlsDetails
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from ..Serializer.S_PosSettings import *
from FoodERPApp.models import *
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

class ERPUrlsByPartyView(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request, party_id):
        try:
            with transaction.atomic():
                if not M_Parties.objects.filter(id=party_id).exists():
                    return JsonResponse({
                        "StatusCode": 404,
                        "Status": False,
                        "Message": "Party ID not found!",
                        "Data": []
                    }, status=404)
                # Fetch all base URLs
                all_urls = M_ERPUrls.objects.all()

                # Fetch override URLs for given party
                overrides = MC_ERPUrlsDetails.objects.filter(PartyId=party_id)
                override_map = {o.ERPUrls_id: o.Urls for o in overrides}
 
                final_data = []
                for url in all_urls:
                    final_data.append({
                        "ID": url.id,
                        "Name": url.Name,
                        "Urls": override_map.get(url.id, url.Urls)
                    })

                return JsonResponse({
                    "StatusCode": 200,
                    "Status": True,
                    "Message": "ERP URLs fetched successfully",
                    "Data": final_data
                }, status=200)

        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)
