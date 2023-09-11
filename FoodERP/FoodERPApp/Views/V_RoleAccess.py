from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_RoleAccess import *
from ..models import *
from ..Serializer.S_Orders import *
from ..Views.V_CommFunction import *


def GetRelatedPageID(id):
    a=M_Pages.objects.filter(id=id).values('RelatedPageID')
    aa=M_Pages.objects.filter(id=a[0]['RelatedPageID']).values('ActualPagePath')
    
    if(a[0]['RelatedPageID']  == 0):
        b=M_Pages.objects.filter(RelatedPageID=id).values('id','ActualPagePath')
       
        if not b:
           
            return str(0) +','+ str(0)
            
        else:
            
            return str(b[0]['id']) +','+ b[0]['ActualPagePath']
    else:
        return str(a[0]['RelatedPageID']) +','+ aa[0]['ActualPagePath']



class RoleAccessView(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    def get(self, request, PartyID=0, EmployeeID=0,CompanyID=0):    
        
        CompanyIDQuery=M_Employees.objects.filter(id=EmployeeID).values('Company')
        CompanyID=CompanyIDQuery[0]['Company']
        Division=PartyID
        # print(request.session.get('UserName'))
      
        if (int(PartyID) > 0)  : 
            Division="M_RoleAccess.Division_id = "+PartyID
            Role=MC_UserRoles.objects.raw('''SELECT Role_id id FROM MC_UserRoles join M_Users on M_Users.id=MC_UserRoles.User_id where Party_id= %s and M_Users.Employee_id=%s''',[PartyID,EmployeeID])
        else:
            Division="M_RoleAccess.Division_id is null "
            Role=MC_UserRoles.objects.raw('''SELECT Role_id id FROM MC_UserRoles join M_Users on M_Users.id=MC_UserRoles.User_id where Party_id IS NULL and M_Users.Employee_id=%s ''',[EmployeeID])
           
        # return Response(str(Role.query))
        qq = M_RoleAccessSerializerforRole(Role, many=True).data
        # print(qq)
       
        if(len(qq) == 1):
            roles=list()
            roles.append(qq[0]['id'])
            roles.append(0)
            y=tuple(roles)
            
        else:     
            roles=list()
            for a in qq:
                roles.append(a['id'])
            y=tuple(roles)

        if (int(PartyID) > 0)  :
       
            modules= M_RoleAccess.objects.filter(Division=PartyID ,Company=CompanyID, Role_id__in=y).values('Modules_id').distinct() 
            if modules.count() ==0:
                modules= M_RoleAccess.objects.filter(Division__isnull=True ,Company=CompanyID, Role_id__in=y).values('Modules_id').distinct()   
        else:
            modules= M_RoleAccess.objects.filter(Division__isnull=True ,Company=CompanyID, Role_id__in=y).values('Modules_id').distinct()   

        queryset=H_Modules.objects.filter(id__in=modules).order_by("DisplayIndex")
        serializerdata = H_ModulesSerializer(queryset, many=True).data
        # print(modules.query)
        
        Moduledata = list()
               
        for a in serializerdata:
            id = a['id']
            Modulesdata = H_Modules.objects.get(id=id)
            Modules_Serializer = H_ModulesSerializer(Modulesdata).data
             
            if (int(PartyID) > 0)  :

                query=M_RoleAccess.objects.all().filter(Role_id__in=y,Modules_id=id,Division_id=PartyID,Company=CompanyID,).select_related('Pages').order_by('Pages__DisplayIndex')
                if query.count() == 0:
                    query=M_RoleAccess.objects.all().filter(Role_id__in=y,Modules_id=id,Division_id__isnull=True,Company=CompanyID,).select_related('Pages').order_by('Pages__DisplayIndex')
            else :
                query=M_RoleAccess.objects.all().filter(Role_id__in=y,Modules_id=id,Division_id__isnull=True,Company=CompanyID).select_related('Pages').order_by('Pages__DisplayIndex')

            # print(str(query.query) )  
          
            PageSerializer = RoleAccessserializerforsidemenu(query,  many=True).data
            # return Response(PageSerializer ) 
            Pagesdata = list()
            for a1 in PageSerializer:
                id = a1['id']
               
                RolePageAccess = MC_RolePageAccess.objects.raw(''' SELECT MC_RolePageAccess.PageAccess_id id,Name  FROM MC_RolePageAccess 
                JOIN H_PageAccess ON H_PageAccess.id=MC_RolePageAccess.PageAccess_id  WHERE MC_RolePageAccess.RoleAccess_id=%s ''', [id])
                RolePageAccessSerializer = MC_RolePageAccessSerializer(
                    RolePageAccess,  many=True).data
                # print(str(RolePageAccess.query))
               
                GetRelatedPageIDData=GetRelatedPageID(a1['Pages']['id'])
                vvv=GetRelatedPageIDData.split(',')
                
                Pagesdata.append({
                    "id": a1['Pages']['id'], 
                    "RelatedPageID": int(vvv[0]),
                    "RelatedPageIDPath": vvv[1],
                    "Name": a1['Pages']['Name'],
                    "PageType" : a1['Pages']['PageType'],
                    "CountLabel" : a1['Pages']['CountLabel'],
                    "ShowCountLabel" : a1['Pages']['ShowCountLabel'],
                    "PageHeading": a1['Pages']['PageHeading'],
                    "PageDescription": a1['Pages']['PageDescription'],
                    "PageDescriptionDetails": a1['Pages']['PageDescriptionDetails'],
                    "DisplayIndex": a1['Pages']['DisplayIndex'],
                    "Icon": a1['Pages']['Icon'],
                    "ActualPagePath": a1['Pages']['ActualPagePath'],
                    "RolePageAccess": RolePageAccessSerializer
                })
           
            response1 = {
                "ModuleID": a['id'],
                "ModuleName":a["Name"],
                "ModuleIcon":a["Icon"],
                "ModuleData": Pagesdata,

            }
         
            Moduledata.append(response1)
             
        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        # log_entry = create_transaction_logNew(request, {'RoleAccessID':id},CompanyID, "Role Access",127,0,0,0,PartyID)
        return Response(response)

    # Role Access POST Method first delete record on role,company,division and then Insert data

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                RoleAccessdata = JSONParser().parse(request)
                
                RoleAccessSerialize_data = M_RoleAccessSerializer(
                    data=RoleAccessdata, many=True)
               
                if RoleAccessSerialize_data.is_valid():
                    # return JsonResponse({'Data':RoleAccessSerialize_data.data[0]['Role']})
                    RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                        Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                    RoleAccessdata.delete()
                    RoleAccessSerialize_data.save()
                    Party=RoleAccessSerialize_data.data[0]['Company']

                    # log_entry = create_transaction_logNew(request, {'RoleAccessDetails':RoleAccessSerialize_data},Party, "Role Access Save Successfully",128,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Role Access Save Successfully', 'Data': []})
                # log_entry = create_transaction_logNew(request, {'RoleAccessDetails':RoleAccessSerialize_data},0, RoleAccessSerialize_data.errors,34,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
        except Exception as e :
            # log_entry = create_transaction_logNew(request, {'RoleAccessDetails':RoleAccessSerialize_data},0, e,33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   e, 'Data': []})


class RoleAccessViewList(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID'] 
                
                if(RoleID == 1):
                    query = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id,M_RoleAccess.Role_id,M_Roles.Name RoleName,M_RoleAccess.Division_id,M_Parties.Name DivisionName,M_RoleAccess.Company_id,C_Companies.Name CompanyName,M_RoleAccess.CreatedBy
    FROM M_RoleAccess
    join M_Roles ON M_Roles.id=M_RoleAccess.Role_id
    left join M_Parties  ON M_Parties.id=M_RoleAccess.Division_id
    left join C_Companies  ON C_Companies.id=M_RoleAccess.Company_id where M_RoleAccess.CreatedBy=%s  group by Role_id,Division_id,Company_id''',[UserID])
                else:
                    query = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id,M_RoleAccess.Role_id,M_Roles.Name RoleName,M_RoleAccess.Division_id,M_Parties.Name DivisionName,M_RoleAccess.Company_id,C_Companies.Name CompanyName,M_RoleAccess.CreatedBy
    FROM M_RoleAccess
    join M_Roles ON M_Roles.id=M_RoleAccess.Role_id
    left join M_Parties  ON M_Parties.id=M_RoleAccess.Division_id
    left join C_Companies  ON C_Companies.id=M_RoleAccess.Company_id where M_RoleAccess.CreatedBy=%s  group by Role_id,Division_id,Company_id''',[UserID]) 

                
                if not query:
                    # log_entry = create_transaction_logNew(request, Logindata,CompanyID, 'Data Not Found',7,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    M_Items_Serializer = M_RoleAccessSerializerGETList(
                        query, many=True).data
                    # log_entry = create_transaction_logNew(request, Logindata,CompanyID, 'RoleAccess List',129,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': M_Items_Serializer})

        except Exception as e :
            # log_entry = create_transaction_logNew(request, Logindata,0, e,33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  e, 'Data': []})


class RoleAccessViewNewUpdated(RetrieveAPIView):

    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    def get(self, request,Role=0,Division=0 ,Company=0):
        if int(Division) > 0:
            roleaccessquery = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id id, H_Modules.id moduleid, H_Modules.Name ModuleName,M_Pages.id pageid,M_Pages.RelatedPageID, M_Pages.name PageName,M_Pages.PageType  FROM M_RoleAccess JOIN M_Pages ON M_Pages.id=M_RoleAccess.Pages_id JOIN H_Modules ON H_Modules.id=M_RoleAccess.Modules_id Join M_PageType on M_PageType.id= M_Pages.PageType  WHERE M_PageType.IsAvailableForAccess=1 AND Role_id=%s AND Division_id=%s AND Company_id=%s Order By M_Pages.name ''',([Role],[Division],[Company]))
        else:
            roleaccessquery = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id id, H_Modules.id moduleid, H_Modules.Name ModuleName,M_Pages.id pageid,M_Pages.RelatedPageID, M_Pages.name PageName,M_Pages.PageType  FROM M_RoleAccess JOIN M_Pages ON M_Pages.id=M_RoleAccess.Pages_id JOIN H_Modules ON H_Modules.id=M_RoleAccess.Modules_id Join M_PageType on M_PageType.id= M_Pages.PageType  WHERE M_PageType.IsAvailableForAccess=1 AND Role_id=%s AND Division_id is null AND Company_id=%s Order By M_Pages.name   ''',([Role],[Company]))            
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_RoleAccessSerializerNewUpdated(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
       
        Moduledata = list()
        
        for a in RoleAccessdata:
            id = a['id']
            pageid=a['pageid']
            if a['RelatedPageID']== 0:
                RelatedPageID=a['pageid']
            else:
                RelatedPageID=a['RelatedPageID']
            
            
            if int(Division) > 0:
                RelatedPageroleaccessquery = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id id,'a' as Name FROM M_RoleAccess WHERE  Pages_id=%s and  Role_id=%s AND Division_id=%s AND Company_id=%s   ''',([RelatedPageID],[Role],[Division],[Company]))
            else:
               
                RelatedPageroleaccessquery = M_RoleAccess.objects.raw('''SELECT M_RoleAccess.id id,'a' as Name FROM M_RoleAccess WHERE  Pages_id=%s and  Role_id=%s AND Division_id is null AND Company_id=%s   ''',([RelatedPageID],[Role],[Company]))
            # print(pageid)
            # print('vvvvvvvvvvvvvv',RelatedPageroleaccessquery.query)
            RelatedPageRoleAccessdata = MC_RolePageAccessSerializerNewUpdated(RelatedPageroleaccessquery, many=True).data
            # print(RelatedPageRoleAccessdata)
            
            rolepageaccessqueryforlistPage =  H_PageAccess.objects.raw('''SELECT H_PageAccess.Name,ifnull(MC_RolePageAccess.PageAccess_id,0) id from H_PageAccess left JOIN MC_RolePageAccess ON MC_RolePageAccess.PageAccess_id=H_PageAccess.id AND MC_RolePageAccess.RoleAccess_id=%s ''', [id])
            # # return JsonResponse({'query':  str(rolepageaccessquery.query)})
            RolePageAccessSerializerforListPAge = MC_RolePageAccessSerializerNewUpdated(rolepageaccessqueryforlistPage,  many=True).data
            # # return JsonResponse({'query':  RolePageAccessSerializerforListPAge})
            
            roleaccessID=0
            for d in RelatedPageRoleAccessdata:
                
                roleaccessID=d['id']
            # print(roleaccessID)   
            rolepageaccessquery =  H_PageAccess.objects.raw('''SELECT H_PageAccess.Name,ifnull(MC_RolePageAccess.PageAccess_id,0) id from H_PageAccess left JOIN MC_RolePageAccess ON MC_RolePageAccess.PageAccess_id=H_PageAccess.id AND MC_RolePageAccess.RoleAccess_id=%s ''', [roleaccessID])
            # print(rolepageaccessquery.query)
            # return JsonResponse({'query':  str(rolepageaccessquery.query)})
            RolePageAccessSerializer = MC_RolePageAccessSerializerNewUpdated(rolepageaccessquery,  many=True).data
            # return JsonResponse({'data':  RolePageAccessSerializer})
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT H_PageAccess.Name,ifnull(MC_PagePageAccess.Access_id,0) id from H_PageAccess left JOIN MC_PagePageAccess ON MC_PagePageAccess.Access_id=H_PageAccess.id AND MC_PagePageAccess.Page_id=%s order by Sequence''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerNewUpdated(pageaccessquery,  many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['pageid'],
                "RelatedPageID": a['RelatedPageID'],
                "PageName": a['PageName'],
                "PageType" : a['PageType'],
                "RoleAccess_IsShowOnMenuForMaster": RolePageAccessSerializer[0]['id'],
                "RoleAccess_IsShowOnMenuForList": RolePageAccessSerializerforListPAge[0]['id'],
                "RoleAccess_IsSave": RolePageAccessSerializer[1]['id'],
                "RoleAccess_IsView": RolePageAccessSerializer[2]['id'],
                "RoleAccess_IsEdit": RolePageAccessSerializer[3]['id'],
                "RoleAccess_IsDelete": RolePageAccessSerializer[4]['id'],
                "RoleAccess_IsEditSelf": RolePageAccessSerializer[5]['id'],
                "RoleAccess_IsDeleteSelf": RolePageAccessSerializer[6]['id'],
                "RoleAccess_IsPrint": RolePageAccessSerializer[7]['id'],
                "RoleAccess_IsTopOfTheDivision": RolePageAccessSerializer[8]['id'],
                "RoleAccess_Pdfdownload": RolePageAccessSerializer[9]['id'],
                "RoleAccess_Exceldownload": RolePageAccessSerializer[10]['id'],
                "RoleAccess_IsCopy": RolePageAccessSerializer[11]['id'],
                "RoleAccess_IsMultipleInvoicePrint": RolePageAccessSerializer[12]['id'],
                "PageAccess_IsShowOnMenu": PageAccessSerializer[0]['id'],
                "PageAccess_IsSave": PageAccessSerializer[1]['id'],
                "PageAccess_IsView": PageAccessSerializer[2]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[3]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[4]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[5]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[6]['id'],
                "PageAccess_IsPrint": PageAccessSerializer[7]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[8]['id'],
                "PageAccess_Pdfdownload": PageAccessSerializer[9]['id'],
                "PageAccess_Exceldownload": PageAccessSerializer[10]['id'],
                "PageAccess_IsCopy": PageAccessSerializer[11]['id'],
                "PageAccess_IsMultipleInvoicePrint": PageAccessSerializer[12]['id']

            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        # log_entry = create_transaction_logNew(request, 0,Company,"RoleAccessNewUpdated",130,0)
        return Response(response)
    
    @transaction.atomic()
    def delete(self, request, Role=0,Division=0,Company=0):
        try:
            with transaction.atomic():
                if int(Division) > 0:
                    RoleAccessdata = M_RoleAccess.objects.filter(Role=Role,Division=Division,Company=Company).values('id')
                else:
                    RoleAccessdata = M_RoleAccess.objects.filter(Role=Role,Division_id__isnull=True,Company=Company).values('id')      
                for a in RoleAccessdata:
                    RoleAccessID = a['id']
                    RoleAccessDeletedata = M_RoleAccess.objects.get(id=RoleAccessID)
                    RoleAccessDeletedata.delete()
                # log_entry = create_transaction_logNew(request,0,Company,"RoleAccess Deleted Successfully",131,0)
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'RoleAccess Deleted Successfully','Data':[]}) 
        except Exception as e:
            # log_entry = create_transaction_logNew(request, 0,0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]}) 

class RoleAccessViewAddPage(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    def get(self, request, pageid=0):
        roleaccessquery = M_Pages.objects.raw('''SELECT H_Modules.id moduleid, H_Modules.Name ModuleName,M_Pages.id id,M_Pages.RelatedPageID, M_Pages.name PageName ,M_Pages.PageType FROM M_Pages JOIN H_Modules ON H_Modules.id=M_Pages.Module_id WHERE M_Pages.id=%s''',[pageid])
        # return JsonResponse({'query':  str(roleaccessquery.query)})
        RoleAccessdata = M_PageSerializerAddPage(roleaccessquery, many=True).data
        # return JsonResponse({'data':  RoleAccessdata})
        Moduledata = list()
        for a in RoleAccessdata:
            pageaccessquery =  H_PageAccess.objects.raw('''SELECT H_PageAccess.Name,ifnull(MC_PagePageAccess.Access_id,0) id from H_PageAccess left JOIN MC_PagePageAccess ON MC_PagePageAccess.Access_id=H_PageAccess.id AND MC_PagePageAccess.Page_id=%s order by Sequence''', [pageid])
            # return JsonResponse({'query':  str(pageaccessquery.query)})
            PageAccessSerializer = M_PageAccessSerializerAddPage(pageaccessquery,many=True).data
            Moduledata.append({
                "ModuleID": a['moduleid'],
                "ModuleName": a['ModuleName'],
                "PageID": a['id'],
                "RelatedPageID": a['RelatedPageID'],
                "PageName": a['PageName'],
                "PageType" : a['PageType'],
                "RoleAccess_IsShowOnMenu": 0,
                "RoleAccess_IsSave": 0,
                "RoleAccess_IsView": 0,
                "RoleAccess_IsEdit": 0,
                "RoleAccess_IsDelete": 0,
                "RoleAccess_IsEditSelf": 0,
                "RoleAccess_IsDeleteSelf": 0,
                "RoleAccess_IsPrint": 0,
                "RoleAccess_IsTopOfTheDivision": 0,
                "RoleAccess_Pdfdownload": 0,
                "RoleAccess_Exceldownload": 0,
                "RoleAccess_IsCopy": 0,
                "RoleAccess_IsMultipleInvoicePrint":0,
                "RoleAccess_IsShowOnMenuForList":0,
                "RoleAccess_IsShowOnMenuForMaster":0,
                "PageAccess_IsShowOnMenu": PageAccessSerializer[0]['id'],
                "PageAccess_IsSave": PageAccessSerializer[1]['id'],
                "PageAccess_IsView": PageAccessSerializer[2]['id'],
                "PageAccess_IsEdit": PageAccessSerializer[3]['id'],
                "PageAccess_IsDelete": PageAccessSerializer[4]['id'],
                "PageAccess_IsEditSelf": PageAccessSerializer[5]['id'],
                "PageAccess_IsDeleteSelf": PageAccessSerializer[6]['id'],
                "PageAccess_IsPrint": PageAccessSerializer[7]['id'],
                "PageAccess_IsTopOfTheDivision": PageAccessSerializer[8]['id'],
                "PageAccess_Pdfdownload": PageAccessSerializer[9]['id'],
                "PageAccess_Exceldownload": PageAccessSerializer[10]['id'],
                "PageAccess_IsCopy": PageAccessSerializer[11]['id'],
                "PageAccess_IsMultipleInvoicePrint": PageAccessSerializer[12]['id']
                   
            })

        response = {
            "StatusCode": 200,
            "Status": True,
            "Message": " ",
            "Data": Moduledata,
        }
        # log_entry = create_transaction_logNew(request, {'RoleAccessID':a['id']},0,"RoleAccessAddPage",132,0)
        return Response(response)    

class RoleAccessGetPagesOnModule(RetrieveAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication
    
    def get(self, request, moduleid=0,Division=0):
        try:
            with transaction.atomic():
                
                if int(Division) > 0:
                    query = M_Pages.objects.raw('''Select M_Pages.id,M_Pages.Name FROM M_Pages Join M_PageType on M_PageType.id= M_Pages.PageType   WHERE M_PageType.IsAvailableForAccess=1 and M_Pages.IsDivisionRequired IN(1,0) and  Module_id=%s''',[moduleid])
                    
                else:
                    query = M_Pages.objects.raw('''Select M_Pages.id,M_Pages.Name FROM M_Pages join M_PageType on M_PageType.id= M_Pages.PageType  WHERE M_PageType.IsAvailableForAccess=1  and M_Pages.IsDivisionRequired=0 and Module_id=%s''',[moduleid])      
                   
                if not query:
                    # log_entry = create_transaction_logNew(request,0,0,"Data Not Found",7,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Records Not Found', 'Data': []})
                else:
                    PageSerializer = M_PageSerializerNewUpdated(
                        query, many=True).data
                    # log_entry = create_transaction_logNew(request,0,0,"RoleAccessGetPagesOnModule",133,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': PageSerializer})
        except Exception  :
            # log_entry = create_transaction_logNew(request, 0,0,"Execution Error",135,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  'Execution Error', 'Data': []})
        
      
class CopyRoleAccessView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    # authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def post(self, request):       
        Role = request.data['Role']
        Division  = request.data['Division']
        NewRole = request.data['NewRole']
        NewDivision = request.data['NewDivision']
        try:
            with transaction.atomic():
                if int(Division) > 0:
                    CopyRoleAccessdata = M_RoleAccess.objects.filter(Role_id= Role,Division_id =Division)
                else:
                    CopyRoleAccessdata = M_RoleAccess.objects.filter(Role_id= Role,Division_id__isnull=True)
                if CopyRoleAccessdata.exists():
                    serializersdata = CopyRoleAccessSerializer(CopyRoleAccessdata, many=True)
                    additionaldata=list()
                    for a in serializersdata.data:
                        if int(NewDivision) > 0:
                            a.update({'Role': NewRole,'Division':NewDivision})
                        else:   
                            a.update({'Role': NewRole,'Division':''})
                        additionaldata.append(a)
                    # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':additionaldata})    
                    RoleAccessSerialize_data = InsertCopyRoleAccessSerializer(data=additionaldata, many=True)
                    if RoleAccessSerialize_data.is_valid():
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':RoleAccessSerialize_data.data}) 
                        RoleAccessdata = M_RoleAccess.objects.filter(Role=RoleAccessSerialize_data.data[0]['Role']).filter(
                            Company=RoleAccessSerialize_data.data[0]['Company']).filter(Division=RoleAccessSerialize_data.data[0]['Division'])
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  '0', 'Data':str(RoleAccessdata.query)}) 
                        RoleAccessdata.delete()
                        RoleAccessSerialize_data.save()

                        # log_entry = create_transaction_logNew(request, 0,NewDivision,"Copy Role Access Save Successfully",134,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Copy Role Access Save Successfully', 'Data': []})
                    # log_entry = create_transaction_logNew(request, 0,0,RoleAccessSerialize_data.errors,34,0)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': RoleAccessSerialize_data.errors, 'Data': []})
                # log_entry = create_transaction_logNew(request, 0,0,"Execution Error",135,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Execution Error', 'Data': []})
        except Exception :
            # log_entry = create_transaction_logNew(request, 0,0,"Execution Error",135,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':   'Execution Error', 'Data': []})
        

           