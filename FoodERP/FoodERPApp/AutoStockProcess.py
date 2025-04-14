from datetime import datetime, timedelta
import time
from django.http import JsonResponse
from django.db import transaction
from rest_framework.parsers import JSONParser
import requests

from .models import M_Settings
from .Views.V_CommFunction import *
from .Serializer.S_Reports import *
from .models import *

def autostockprocess():
    print("autostockprocess Function Call")
    url_query = M_Settings.objects.filter(id=66).values('DefaultValue')
    API_URL = url_query[0]['DefaultValue']
    
    headers = {
        "Content-Type": "application/json"  
    }
    auth = ("superadmin", "1234")

    try:
        response = requests.get(API_URL, auth=auth, headers=headers, timeout=10)
        response_data = response.json()
        
        if response_data.get("StatusCode") == 200:
            print("API call success:", response_data.get("Message"))
        else:
            print("API call issue:", response_data.get("Message"))

    except requests.exceptions.RequestException as e:
        print("API request failed:", str(e))
        return JsonResponse({
            'StatusCode': 500,
            'Status': False,
            'Message': 'API request failed',
            'Data': []
        })
