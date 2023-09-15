from ..models import *
from ..Serializer.S_BankMaster import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
# from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from ..Serializer.S_Transaction import *
from django.db.models import Q
from datetime import datetime

class EmplyoeeListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request,id=0):
        try:
            with transaction.atomic():
                query = M_Users.objects.all()
                if query:
                    serializer = EmplyoeeSerializerSecond(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'Emplyoee not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class TransactionTypeListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    # authentication__Class = JSONWebTokenAuthentication

    @transaction.atomic()
    def get(self,request):
        try:
            with transaction.atomic():
                query = M_TransactionType.objects.all()
                if query:
                    serializer = TransactionTypeSerializer(query, many=True).data
                    return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'TransactionType not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})


class TransactionTypeView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    def post(self, request, id=0):
        try:
            with transaction.atomic():
                Transactiondata = JSONParser().parse(request)
                FromDateStr = Transactiondata['FromDate']
                ToDateStr = Transactiondata['ToDate']
                FromDate = datetime.strptime(FromDateStr, '%Y-%m-%d %H:%M')
                ToDate = datetime.strptime(ToDateStr, '%Y-%m-%d %H:%M')
                TransactionTypes = Transactiondata['TransactionType']
                TransactionTypesIDs = TransactionTypes.split(',')
                Users = Transactiondata['User']
                UsersIDs = Users.split(',')
                Parties = Transactiondata['Party']
                PartyIDs = Parties.split(',')
                
                if TransactionTypes == '' :
                    TT=Q()  
                else:
                    TT=Q(TransactionType__in=TransactionTypesIDs)

                if Users == '' :
                    U=Q()
                else:
                    U=Q(User__in=UsersIDs)
                    

                if Parties == '' :
                    P=Q()
                else:
                    P=Q(PartyID__in=PartyIDs)      
                
                Trasactionquery= Transactionlog.objects.filter(FromDate=FromDate,ToDate=ToDate).filter(TT).filter(P).filter(U)
#                 Trasactionquery= Transactionlog.objects.raw('''SELECT tl.id AS Id, tl.TranasactionDate, tl.IPaddress, (SELECT e.Name FROM M_Employees AS e
# WHERE e.id = tl.User) AS UserName,(SELECT p.Name FROM m_parties AS p WHERE p.id = tl.PartyID)
#  AS PartyName, tl.TransactionType, tl.TransactionID FROM Transactionlog AS tl
# WHERE (tl.FromDate = %s AND tl.ToDate = %s AND tl.TransactionType IN %s AND 
# tl.PartyID  IN %s AND tl.User IN %s)''',([FromDate][ToDate][TransactionTypes],[Parties],[Users]))
                print(Trasactionquery.query)
                if Trasactionquery:
                        Transaction_Serializer = TransactionlogSerializer(Trasactionquery,many=True).data
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Transaction_Serializer})
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'TransactionTypeDetails not available', 'Data' : []})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

                              