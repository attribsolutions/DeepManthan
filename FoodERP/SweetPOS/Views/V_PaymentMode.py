from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..models import M_PaymentModes, MC_PaymentModeDetails
from ..Serializer.S_PaymentMode import  M_PaymentModesSerializer, MC_PaymentModeDetailsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from FoodERPApp.models import *
from django.http import JsonResponse

class PaymentModeAPIView(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, party_id): 
        try:
            with transaction.atomic():
                if not party_id:
                    return JsonResponse({
                        "StatusCode": 400,
                        "Status": False,
                        "Message": "PartyId is required for fetch PaymentModes!",
                        "Data": []
                    }, status=400)
                if not M_Parties.objects.filter(id=party_id).exists():
                    return JsonResponse({
                        "StatusCode": 404,
                        "Status": False,
                        "Message": "Party not found!",
                        "Data": []
                    }, status=404)

                party_modes = MC_PaymentModeDetails.objects.filter(PartyId=party_id)
                if party_modes.exists():
                    serializer = MC_PaymentModeDetailsSerializer(party_modes, many=True)
                else:
                    modes = M_PaymentModes.objects.all()
                    serializer = M_PaymentModesSerializer(modes, many=True)

                return JsonResponse({
                    "StatusCode": 200,
                    "Status": True,
                    "Message": "Payment Modes fetched successfully",
                    "Data": serializer.data
                }, status=200)

        except Exception as e:
            return JsonResponse({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e),
                "Data": []
            }, status=500)
