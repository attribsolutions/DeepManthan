from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Pages import *
from ..models import M_Pages
from django.db.models import OuterRef, Subquery
from rest_framework.authentication import BasicAuthentication
from SweetPOS.Views.V_SweetPosRoleAccess import BasicAuthenticationfunction


class GetNewPageEntry(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_classes = [BasicAuthentication]
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                user=BasicAuthenticationfunction(request)
                if user is not None:
                    subquery = M_PageType.objects.filter(id=OuterRef('PageType')).values('Name')[:1]
                    subquery1 = M_Pages.objects.filter(id=OuterRef('RelatedPageID')).values('Name')[:1]

                    # Fetch all pages where Is_New is 1
                    HPagesdata = M_Pages.objects.select_related('Module').filter(Is_New=1
                    ).annotate(PageTypeName=Subquery(subquery)).annotate(RelatedPageName=Subquery(subquery1)).values(
                        'id', 'Name', 'PageHeading', 'PageDescription', 'PageDescriptionDetails', 
                        'isActive', 'DisplayIndex', 'Icon', 'ActualPagePath', 'Module__id', 
                        'Module__Name', 'PageType', 'PageTypeName', 'RelatedPageID', 
                        'RelatedPageName', 'IsDivisionRequired', 'IsEditPopuporComponent', 
                        'CountLabel', 'ShowCountLabel', 'CreatedBy', 'CreatedOn', 'UpdatedBy', 
                        'UpdatedOn', 'IsSweetPOSPage' 
                    )

                    if not HPagesdata:
                        return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Records Not Available', 'Data': []})

                    PageListData = []
                    for a in HPagesdata:
                        # Fetching Page Access Data
                        bb = MC_PagePageAccess.objects.filter(Page_id=a['id']).select_related('Access').values(
                            'Access_id', 'Access__Name'
                        )

                        # PageAccessListData = [{"Access": b['Access_id'], "AccessName": b['Access__Name']} for b in bb]
                        PageAccessListData = [{"Access": b['Access_id']} for b in bb]

                        # Handling Related Page ID
                        related_page = M_Pages.objects.filter(id=a['id']).values('RelatedPageID').first()
                        bb = a['id'] if related_page and related_page['RelatedPageID'] == 0 else related_page['RelatedPageID']

                        # Fetching Page Field Master Data
                        MasterPageFieldQuery = MC_PageFieldMaster.objects.filter(Page_id=bb).select_related(
                            'ControlType', 'FieldValidation'
                        ).values(
                            'id', 'ControlID', 'FieldLabel', 'IsCompulsory', 'DefaultSort', 
                            'ListPageSeq', 'ShowInListPage', 'ShowInDownload', 
                            'DownloadDefaultSelect', 'InValidMsg', 'ControlType__id', 
                            'ControlType__Name', 'FieldValidation__id', 'FieldValidation__Name', 
                            'FieldValidation__RegularExpression', 'Alignment'
                        )

                        MC_PageFieldMasterListData = [{
                            "ControlID": c['ControlID'], "ControlType": c['ControlType__id'], 
                            "ControlTypeName": c['ControlType__Name'], "FieldLabel": c['FieldLabel'], 
                            "IsCompulsory": c['IsCompulsory'], "DefaultSort": c['DefaultSort'], 
                            "FieldValidation": c['FieldValidation__id'], "FieldValidationName": c['FieldValidation__Name'], 
                            "ListPageSeq": c['ListPageSeq'], "ShowInListPage": c['ShowInListPage'], 
                            "ShowInDownload": c['ShowInDownload'], "ShownloadDefaultSelect": c['DownloadDefaultSelect'], 
                            "RegularExpression": c['FieldValidation__RegularExpression'], "InValidMsg": c['InValidMsg'], 
                            "Alignment": c['Alignment']
                        } for c in MasterPageFieldQuery]

                        PageListData.append({
                            "id": a['id'], "Name": a['Name'], "PageHeading": a['PageHeading'],
                            "PageDescription": a['PageDescription'], "PageDescriptionDetails": a['PageDescriptionDetails'],
                            "Module": a['Module__id'], "ModuleName": a['Module__Name'], "isActive": a['isActive'],
                            "DisplayIndex": a['DisplayIndex'], "Icon": a['Icon'], "ActualPagePath": a['ActualPagePath'],
                            "PageType": a['PageType'], "PageTypeName": a['PageTypeName'],
                            "RelatedPageID": a['RelatedPageID'], "RelatedPageName": a['RelatedPageName'],
                            "IsDivisionRequired": a['IsDivisionRequired'], "IsEditPopuporComponent": a['IsEditPopuporComponent'],
                            "CountLabel": a['CountLabel'], "ShowCountLabel": a['ShowCountLabel'],
                            "PagePageAccess": PageAccessListData, "PageFieldMaster": MC_PageFieldMasterListData,
                            "CreatedBy": a['CreatedBy'], "CreatedOn": a['CreatedOn'], "UpdatedBy": a['UpdatedBy'], 
                            "UpdatedOn": a['UpdatedOn'], "IsSweetPOSPage": a['IsSweetPOSPage']
                        })

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageListData})

        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

