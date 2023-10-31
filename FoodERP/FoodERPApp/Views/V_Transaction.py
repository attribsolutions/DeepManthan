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
from django.db import connection
from .V_CommFunction import *


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
                FromDate = datetime.strptime(FromDateStr, '%Y-%m-%d %H:%M:%S')
                ToDate = datetime.strptime(ToDateStr, '%Y-%m-%d %H:%M:%S')
                TransactionTypes = Transactiondata['TransactionType']
                TransactionTypesIDs = TransactionTypes.split(',')
                Users = Transactiondata['User']
                UsersIDs = Users.split(',')
                Parties = Transactiondata['Party']
                PartyIDs = Parties.split(',')
                TransactionCategory = Transactiondata['TransactionCategory']
                TransactionCategoryIDs = TransactionCategory.split(',')
                
                conditions = []

                if TransactionTypes == '' :
                    pass
                else:
                    conditions.append(f"TransactionType IN ({','.join(TransactionTypesIDs)})")
                if Users == '' :
                    pass
                else:
                    conditions.append(f"User IN ({','.join(UsersIDs)})")
                if Parties == '' :
                    pass
                else:
                    conditions.append(f"PartyID IN ({','.join(PartyIDs)})")
                if TransactionCategory == '' :
                    pass
                else:
                    conditions.append(f"TransactionCategory IN ({','.join(TransactionCategoryIDs)})")

                where_clause = " AND ".join(conditions) if conditions else ""


                Transactionquery_sql = f'''SELECT Transactionlog.id, Transactiontime as TransactionDate, concat(M_Employees.Name,' (',M_Users.LoginName,')') UserName, IPaddress, M_TransactionType.Name as TransactionType, TransactionID, A.Name PartyName, B.Name AS CustomerName,TransactionDetails
FROM Transactionlog 
LEFT JOIN M_Users ON Transactionlog.User = M_Users.id
LEFT JOIN M_Employees ON M_Users.Employee_id = M_Employees.id
LEFT JOIN M_TransactionType ON TransactionType = M_TransactionType.id
LEFT JOIN M_Parties A ON Transactionlog.PartyID = A.id 
LEFT JOIN M_Parties B ON Transactionlog.CustomerID = B.id
WHERE Transactiontime BETWEEN %s AND %s'''
                if where_clause:
                    Transactionquery_sql += f' AND {where_clause}'
                Transactionquery_sql += ' ORDER BY Transactiontime DESC'
                Transactionquery = Transactionlog.objects.raw(Transactionquery_sql, [FromDate, ToDate])
                if Transactionquery:
                        Transaction_Serializer = TransactionlogSerializer(Transactionquery,many=True).data
                        log_entry = create_transaction_logNew(request, Transactiondata, 0,'From:'+str(FromDate)+','+'To:'+str(ToDate),196,0,FromDate,ToDate,0)
                        return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data' :Transaction_Serializer})
                log_entry = create_transaction_logNew(request, Transactiondata, 0,'TransactionTypeDetails not available',196,0)
                return JsonResponse({'StatusCode': 406, 'Status': True, 'Message': 'TransactionTypeDetails not available', 'Data' : []})
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,Exception(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  Exception(e), 'Data':[]})

class TransactionJsonView(CreateAPIView):

    permission_classes = (IsAuthenticated,)

    def get(self, request, id=0):
        try:
            with transaction.atomic():
                Transactiondata = Transactionlog.objects.raw('''
                    SELECT Transactionlog.id, Transactionlog.Transactiontime, 
                           Transactionlog.User, Transactionlog.IPaddress,
                           Transactionlog.PartyID,Transactionlog.TransactionDetails, 
                           Transactionlog.TransactionType, Transactionlog.TransactionID, 
                           Transactionlog.FromDate, Transactionlog.ToDate, Transactionlog.CustomerID, 
                           Transactionlog.JsonData,  TransactionLogJsonData.JsonData AS TransactionlogJsondata
                    FROM Transactionlog
                    INNER JOIN TransactionLogJsonData 
                    ON Transactionlog.id = TransactionLogJsonData.Transactionlog_id 
                    WHERE Transactionlog_id = %s
                ''',[id])

                if not Transactiondata:
                    return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'Transaction Not available', 'Data': []})

                Transaction_serializer = TransactionJsonSerializer(Transactiondata, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Transaction_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

  

