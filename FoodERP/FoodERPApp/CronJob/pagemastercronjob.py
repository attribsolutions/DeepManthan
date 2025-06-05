from datetime import datetime, timedelta
import time
from django.http import JsonResponse
from django.db import transaction
from rest_framework.parsers import JSONParser
import requests


from ..models import M_Settings
from ..Views.V_CommFunction import *
from ..Serializer.S_Reports import *
from ..models import *

def pagemastercronjob():
    print("pagemastercronjob Function Call")
    url_query = MC_CronJobSettings.objects.filter(id=1).values('URL')
    if not url_query:
        print("Error: No URL found in MC_CronJobSettings for id=1")
        return JsonResponse({
            'StatusCode': 404,
            'Status': False,
            'Message': 'URL not found in MC_CronJobSettings for id=1',
            'Data': []
        })
    API_URL= url_query[0]['URL']
  
    
    headers = {
        # 'Authorization': f'Bearer {TOKEN}',
        "Content-Type": "application/json"  
    }
    auth = ("superadmin", "1234")

    try:
        response = requests.get(API_URL,auth=auth, headers=headers)  # API call
        response_data = response.json()  # Convert response to JSON
        if response_data.get("StatusCode") == 200 and "Data" in response_data:
            print("successfull called api!!!")
            pages_data = response_data["Data"]
            
            with transaction.atomic():
                for page_data in pages_data:
                    page_id = page_data.get("id")
                    existing_page = M_Pages.objects.filter(id=page_id).first()
                    
                    if existing_page:
                        serializer = M_PagesSerializer1(existing_page, data=page_data)
                        if serializer.is_valid():
                            serializer.save()
                            print(f"Page {page_id} saved successfully!")
                        else:
                            print(f"Error saving page {page_id}: {serializer.errors}")
                    else:
                        # print(page_data)
                        # serializer = M_PagesSerializer1(data=page_data)
                        with connection.cursor() as cursor:
                           
                            page_data['CreatedOn'] = datetime.now()
                            page_data['UpdatedOn'] = datetime.now()
                            page_data['Is_New'] = False
                            # Insert into M_Pages
                            insert_page_query = '''
                                INSERT INTO M_Pages (
                                    id, PageHeading, Name, PageDescription, PageDescriptionDetails, isActive,
                                    DisplayIndex, Icon, ActualPagePath, IsDivisionRequired, IsEditPopuporComponent,
                                    PageType, RelatedPageID, CountLabel, ShowCountLabel, CreatedBy, CreatedOn,
                                    UpdatedBy, UpdatedOn, Module_id, IsSweetPOSPage, Is_New
                                ) VALUES (
                                    %(id)s, %(PageHeading)s, %(Name)s, %(PageDescription)s, %(PageDescriptionDetails)s, %(isActive)s,
                                    %(DisplayIndex)s, %(Icon)s, %(ActualPagePath)s, %(IsDivisionRequired)s, %(IsEditPopuporComponent)s,
                                    %(PageType)s, %(RelatedPageID)s, %(CountLabel)s, %(ShowCountLabel)s, %(CreatedBy)s, %(CreatedOn)s,
                                    %(UpdatedBy)s, %(UpdatedOn)s, %(Module)s, %(IsSweetPOSPage)s, %(Is_New)s
                                )
                            '''

                            cursor.execute(insert_page_query, page_data)

                            # Insert into MC_PagePageAccess for each access
                            insert_access_query = '''
                                INSERT INTO MC_PagePageAccess (Access_id, Page_id) VALUES (%s, %s)
                            '''
                            for access in page_data.get('PagePageAccess', []):
                                cursor.execute(insert_access_query, [access['Access'], page_data['id']])

                            # Insert into MC_PageFieldMaster for each field
                            insert_field_query = '''
                                INSERT INTO MC_PageFieldMaster (
                                    ControlID, ControlType_id, FieldLabel, IsCompulsory, DefaultSort,
                                    FieldValidation_id, ListPageSeq, ShowInListPage, ShowInDownload,
                                    DownloadDefaultSelect, InValidMsg, Alignment, Page_id
                                ) VALUES (
                                    %(ControlID)s, %(ControlType)s, %(FieldLabel)s, %(IsCompulsory)s, %(DefaultSort)s,
                                    %(FieldValidation)s, %(ListPageSeq)s, %(ShowInListPage)s, %(ShowInDownload)s,
                                    %(DownloadDefaultSelect)s, %(InValidMsg)s, %(Alignment)s, %(Page_id)s
                                )
                            '''
                            for field in page_data.get('PageFieldMaster', []):
                                cursor.execute(insert_field_query, {**field, 'Page_id': page_data['id']})

                        print(f"Page {page_data['id']} inserted successfully with related access and field master records.")


            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Pages saved successfully', 'Data': []})
        
        return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': 'Invalid API response', 'Data': []})

    except requests.exceptions.RequestException as e:
        print("API request failed:", str(e))
        return JsonResponse({'StatusCode': 500, 'Status': False, 'Message': 'API request failed', 'Data': []})
	

