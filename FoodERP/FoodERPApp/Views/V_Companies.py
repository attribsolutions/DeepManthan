from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_EmployeeTypes import M_EmployeeTypeSerializer

from ..Serializer.S_Companies import *

from ..models import C_Companies


class C_CompaniesViewFilter(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
                   
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Logindata = JSONParser().parse(request)
                UserID = Logindata['UserID']   
                RoleID=  Logindata['RoleID']  
                CompanyID=Logindata['CompanyID']
                PartyID=Logindata['PartyID'] 

                if(RoleID == 1 ):
                    Groupquery = C_Companies.objects.all()
                else:
                    Groupquery = C_Companies.objects.filter(id=CompanyID)
               
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = C_CompanySerializerSecond(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "IsSCM" : a['IsSCM'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})                


class C_CompaniesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
                   
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.all()
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = C_CompanySerializerSecond(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "IsSCM" : a['IsSCM'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})                

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                AdminDivisionDatalist=list()
                Companiesdata = JSONParser().parse(request)


                AdminDivisionDatalist.append({
                        "Name": Companiesdata['Name']+' AdminDivision',
                        "PartyType": 5,
                        "Company": 1,
                        "PAN": "AAAAA1234A",
                        "Email": Companiesdata['EmailID'],
                        "MobileNo": Companiesdata['PhoneNo'],
                        "AlternateContactNo": "",
                        "State": 22,
                        "District": 1,
                        "Taluka": 0,
                        "City": 0,
                        "GSTIN": Companiesdata['GSTIN'],
                        "MkUpMkDn": False,
                        "isActive": True,
                        "IsDivision": True,
                        "CreatedBy": 1,
                        "UpdatedBy": 1,
                        "IsRetailer" : 0
                        
              })
                # Companiesdata.update({"AdminDivisionDatalist" : AdminDivisionDatalist})
                # print(Companiesdata)
                Companies_Serializer = C_CompanySerializer(data=Companiesdata)
                AdminDivisionDatalist_Serializer=M_PartySerializer(data=AdminDivisionDatalist[0])
                # print(Companies_Serializer)
                if Companies_Serializer.is_valid() and AdminDivisionDatalist_Serializer.is_valid():
                    Companies_Serializer.save()
                    ff=Companies_Serializer.data['id']
                    AdminDivisionDatalist_Serializer.save()
                    party=AdminDivisionDatalist_Serializer.data['id']
                    M_Parties.objects.filter(id=party).update(Company=ff)

                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Save Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  AdminDivisionDatalist_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
            


class C_CompaniesViewSecond(CreateAPIView):

    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request,id=0):
        try:
            with transaction.atomic():
                Groupquery = C_Companies.objects.filter(id=id)
                if Groupquery.exists():
                    # return JsonResponse({'query':  str(Itemsquery.query)})
                    Companydata = C_CompanySerializerSecond(Groupquery, many=True).data
                    CompanyList=list()
                    for a in Companydata:
                        CompanyList.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "CompanyGroup": a['CompanyGroup']['id'],
                            "CompanyGroupName": a['CompanyGroup']['Name'],
                            "Address": a['Address'],
                            "GSTIN": a['GSTIN'],
                            "PhoneNo": a['PhoneNo'],
                            "CompanyAbbreviation": a['CompanyAbbreviation'],
                            "EmailID": a['EmailID'],
                            "IsSCM" : a['IsSCM'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn']
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Data': CompanyList[0]})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Group Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})



    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = JSONParser().parse(request)
                CompaniesdataByID = C_Companies.objects.get(id=id)
                Companies_Serializer = C_CompanySerializer(
                    CompaniesdataByID, data=Companiesdata)
                if Companies_Serializer.is_valid():
                    Companies_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Updated Successfully', 'Data':[]})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': Companies_Serializer.errors, 'Data':[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   
        

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                Companiesdata = C_Companies.objects.get(id=id)
                Companiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Company Deleted Successfully', 'Data':[]})
        except C_Companies.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company Not available', 'Data': []})
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Company used in another table', 'Data': []})   



''' Below class used on Party Master Company Dropdown Populate Here we Check Division is IsSCM Or not. If IsSCM Then We show IsSCM Company Else Other'''
class GetCompanyByDivisionType(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                PartyType = M_PartyType.objects.filter(id=id).values('id','Name','IsSCM','IsDivision')
                # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data':str(PartyType.query) })
                if PartyType.exists():
                    PartyTypedata_Serializer = PartyTypeserializer(PartyType, many=True).data
                    # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data': PartyTypedata_Serializer[0]['IsSCM'] })
                    CompaniesData = C_Companies.objects.filter(IsSCM=PartyTypedata_Serializer[0]['IsSCM'])
                    if CompaniesData.exists():
                        C_Companiesdata_Serializer = C_CompanySerializer(CompaniesData, many=True).data
                        # return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data': C_Companiesdata_Serializer })
                        return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': ' ' , 'Data':C_Companiesdata_Serializer })
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Party Types Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})               

class GetCompanyByEmployeeType(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication_class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                EmployeeTypesdata = M_EmployeeTypes.objects.get(id=id)
                EmployeeTypesdata_Serializer = M_EmployeeTypeSerializer(EmployeeTypesdata).data
                
                Companiesdata = C_Companies.objects.filter(IsSCM=EmployeeTypesdata_Serializer['IsSCM'])
                Companiesdata_Serializer = C_CompanySerializer(Companiesdata, many=True)
                
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message':'', 'Data': Companiesdata_Serializer.data})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})   