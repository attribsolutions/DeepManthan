from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated 
from datetime import datetime

class CurrentServerDateTimeView(CreateAPIView):
    permission_classes = [IsAuthenticated] 

    def get(self, request):
        current_datetime = datetime.now()
        return Response({
            "StatusCode": 200,
            "Status": True,
            "Message": "Current server DateTime fetched successfully",
            "ServerDateTime": current_datetime.strftime("%Y-%m-%d %H:%M:%S.%f")
        })
