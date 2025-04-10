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

def my_cron_job():
    print("my_cron_job Function Call")
    url_query = M_Settings.objects.filter(id=65).values('DefaultValue')
    API_URL= url_query[0]['DefaultValue']
    
    headers = {
        # 'Authorization': f'Bearer {TOKEN}',
        "Content-Type": "application/json"  
    }
    auth = ("superadmin", "1234")

    try:
        response = requests.get(API_URL,auth=auth, headers=headers, timeout=10)  # API call
        response_data = response.json()  # Convert response to JSON
        
        if response_data.get("StatusCode") == 200 and "Data" in response_data:
            print("successfull called api!!!")
            pages_data = response_data["Data"]
            
            with transaction.atomic():
                for page_data in pages_data:
                    page_id = page_data.get("id")
                    # Check if the page already exists
                    existing_page = M_Pages.objects.filter(id=page_id).first()
                    
                    if existing_page:
                        serializer = M_PagesSerializer1(existing_page, data=page_data)
                    else:
                        serializer = M_PagesSerializer1(data=page_data)
                       
                    if serializer.is_valid():
                        serializer.save()
                        print(f"Page {page_id} saved successfully!")
                    else:
                        print(f"Error saving page {page_id}: {serializer.errors}")
                    

            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Pages saved successfully', 'Data': []})
        
        return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid API response', 'Data': []})

    except requests.exceptions.RequestException as e:
        print("API request failed:", str(e))
        return JsonResponse({'StatusCode': 500, 'Status': False, 'Message': 'API request failed', 'Data': []})
	

