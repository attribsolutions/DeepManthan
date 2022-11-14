from django.http import JsonResponse
from rest_framework.generics import CreateAPIView, RetrieveAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, connection, transaction
from rest_framework.parsers import JSONParser

from ..Serializer.S_PartyTypes import PartyTypeSerializer

from ..Serializer.S_Parties import *

from ..models import *


class DivisionsView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Divisiondata =  M_PartyType.objects.filter(IsDivision=id)
                aa=M_Parties.objects.filter(PartyType__in=Divisiondata).values('id','Name')
                if aa.exists():
                    Division_serializer = DivisionsSerializer(aa, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Division_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True, 'Message': 'Division Not available ', 'Data': []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []}) 

class AddressTypesView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                Address_data = M_AddressTypes.objects.all()
                if Address_data.exists():
                    Address_serializer = AddressTypesSerializer(Address_data, many=True)
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Address_serializer.data})
                return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Role Not available', 'Data': []})
        except Exception :
            raise JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Execution Error', 'Data':[]})

  
class M_PartiesView(CreateAPIView):
    
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query=M_Parties.objects.all()
                # return JsonResponse({'StatusCode': 204, 'Status': True,'Data':str(query.query)}) 
                if not query:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(query, many=True).data
                    # return JsonResponse({'StatusCode': 204, 'Status': True,'Data':M_Parties_serializer})
                    PartyData=list()
                    for a in M_Parties_serializer:
                        id =  a['id']
                        query1=MC_PartyAddress.objects.filter(Party=id,IsDefault=1)
                        # return JsonResponse({'StatusCode': 204, 'Status': True,'Data':str(query1.query)})
                        Partyaddress_serializer = PartyAddressSerializerSecond(query1,many=True).data
                        PartyData.append({
                            "id":a['id'],
                            "Name": a['Name'],
                            "isActive":a['isActive'],
                            "PriceListName":a['PriceList']['Name'],
                            "PartyTypeName":a['PartyType']['Name'],
                            # "PartyAddress":Partyaddress_serializer[0]            
                        })
                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': PartyData})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic(): 
                M_Partiesdata = JSONParser().parse(request)
                M_Parties_Serializer = M_PartiesSerializer(data=M_Partiesdata)
            if M_Parties_Serializer.is_valid():
                M_Parties_Serializer.save()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Save Successfully','Data' :[]})
            else:
                transaction.set_rollback(True)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' :[]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

class M_PartiesViewSecond(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self, request, id=0):
        try:
            with transaction.atomic():
                M_Parties_data=M_Parties.objects.filter(id=id)
                if not M_Parties_data:
                    return JsonResponse({'StatusCode': 204, 'Status': True,'Message':  'Records Not available', 'Data': []}) 
                else:
                    M_Parties_serializer = M_PartiesSerializerSecond(M_Parties_data, many=True).data
                    PartiesData=list()
                    for a in M_Parties_serializer:
                        PartyAddresslist=list()
                        for b in a['PartyAddress']:
                            PartyAddresslist.append({
                                "id": b['id'],
                                "Address": b['Address'],
                                "FSSAINo": b['FSSAINo'],
                                "FSSAIExipry": b['FSSAIExipry'],
                                "PIN": b['PIN'],
                                "IsDefault": b['IsDefault'],
                                # "AddressType": b['AddressType']['id'],
                                # "AddressTypeName": b['AddressType']['Name'],
                            })
                        
                        PartiesData.append({
                            "id": a['id'],
                            "Name": a['Name'],
                            "Email": a['Email'],
                            "MobileNo": a['MobileNo'],
                            "AlternateContactNo": a['AlternateContactNo'],
                            "Taluka": a['Taluka'],
                            "City": a['City'],
                            "GSTIN": a['GSTIN'],
                            "PAN": a['PAN'],
                            "isActive":a['isActive'] ,
                            "IsDivision": a['IsDivision'],
                            "MkUpMkDn":a['MkUpMkDn'],
                            "CreatedBy": a['CreatedBy'],
                            "CreatedOn": a['CreatedOn'],
                            "UpdatedBy": a['UpdatedBy'],
                            "UpdatedOn": a['UpdatedOn'],
                            "PriceList":a['PriceList']['id'],
                            "PriceListName":a['PriceList']['Name'],
                            "PartyType":a['PartyType']['id'],
                            "PartyTypeName":a['PartyType']['Name'],
                            "Company":a['Company']['id'],
                            "CompanyName":a['Company']['Name'],
                            "State":a['State']['id'],
                            "StateName":a['State']['Name'],
                            "District":a['District']['id'],
                            "DistrictName":a['District']['Name'],
                            "PartyAddress":PartyAddresslist
                        })

                    return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': PartiesData[0]})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data': []})

    @transaction.atomic()
    def put(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = JSONParser().parse(request)
                M_PartiesdataByID = M_Parties.objects.get(id=id)
                M_Parties_Serializer = M_PartiesSerializer(
                    M_PartiesdataByID, data=M_Partiesdata)
                if M_Parties_Serializer.is_valid():
                    M_Parties_Serializer.save()
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party Updated Successfully','Data' : []})
                else:
                    transaction.set_rollback(True)
                    return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': M_Parties_Serializer.errors,'Data' : []})
        except Exception :
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': 'Exception Found','Data' : []})

    @transaction.atomic()
    def delete(self, request, id=0):
        try:
            with transaction.atomic():
                M_Partiesdata = M_Parties.objects.get(id=id)
                M_Partiesdata.delete()
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Party  Deleted Successfully', 'Data':[]})
        except M_Parties.DoesNotExist:
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party Not available', 'Data': []})    
        except IntegrityError:   
            return JsonResponse({'StatusCode': 204, 'Status': True, 'Message':'Party used in another table', 'Data': []})


                