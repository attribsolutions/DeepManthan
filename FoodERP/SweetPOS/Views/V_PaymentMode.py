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

class PaymentModeAPIView(APIView):
    authentication_classes = [BasicAuthentication, JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, party_id): 
        try:
            with transaction.atomic():
                if not party_id:
                    return Response({
                        "StatusCode": 400,
                        "Status": False,
                        "Message": "PartyId is required for fetch PaymentModes!"
                    }, status=status.HTTP_400_BAD_REQUEST)
                if not M_Parties.objects.filter(id=party_id).exists():
                    return Response({
                        "StatusCode": 404,
                        "Status": False,
                        "Message": "Party not found!"
                    }, status=status.HTTP_404_NOT_FOUND)
                party_modes = MC_PaymentModeDetails.objects.filter(PartyId=party_id)
                if party_modes.exists():
                    serializer = MC_PaymentModeDetailsSerializer(party_modes, many=True)
                else:
                    modes = M_PaymentModes.objects.all()
                    serializer = M_PaymentModesSerializer(modes, many=True)

                return Response({
                    "StatusCode": 200,
                    "Status": True,
                    "Data": serializer.data
                }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "StatusCode": 500,
                "Status": False,
                "Message": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
