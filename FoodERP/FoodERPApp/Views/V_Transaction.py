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
from FoodERPDBLog.models import L_Transactionlog


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


                Transactionquery_sql = f'''SELECT X.id, Transactiontime as TransactionDate, concat(M_Employees.Name,' (',M_Users.LoginName,')') UserName, IPaddress, M_TransactionType.Name as TransactionType, TransactionID, A.Name PartyName, B.Name AS CustomerName,TransactionDetails
FROM TransactionLog.L_Transactionlog X
LEFT JOIN M_Users ON X.User = M_Users.id
LEFT JOIN M_Employees ON M_Users.Employee_id = M_Employees.id
LEFT JOIN M_TransactionType ON TransactionType = M_TransactionType.id
LEFT JOIN M_Parties A ON X.PartyID = A.id 
LEFT JOIN M_Parties B ON X.CustomerID = B.id
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
            log_entry = create_transaction_logNew(request, 0, 0,'TransactionLogDetails:'+str(Exception(e)),33,0)
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
                    FROM TransactionLog.L_Transactionlog Transactionlog
                    left JOIN  TransactionLog.L_TransactionLogJsonData TransactionLogJsonData 
                    ON Transactionlog.id = TransactionLogJsonData.Transactionlog_id 
                    WHERE Transactionlog.id = %s
                ''',[id])

                if not Transactiondata:
                    return JsonResponse({'StatusCode': 404, 'Status': False, 'Message': 'Transaction Not available', 'Data': []})

                Transaction_serializer = TransactionJsonSerializer(Transactiondata, many=True).data
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': Transaction_serializer})
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': False, 'Message': str(e), 'Data': []})

  
class TransactionTypeAddView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def post(self, request):
        try:
            with transaction.atomic():
                Type_data = request.data  
                TypesList = []
                
                for a in Type_data:
                    Type_serializer = TransactionTypeSerializer(data=a)
                    
                    if Type_serializer.is_valid():
                        Type = Type_serializer.save()
                        TypesList.append(Type)
                        LastInsertID = Type.id
                        log_entry = create_transaction_logNew(request, Type_data,0,'TransactionID:'+str(LastInsertID),378,LastInsertID)    
                    else:
                        log_entry = create_transaction_logNew(request, Type_data,0,'TypeSave:'+str(Type_serializer.errors),34,0)
                        transaction.set_rollback(True)
                        return JsonResponse({'StatusCode': 406, 'Status': True, 'Message':  Type_serializer.errors, 'Data':[]})
                return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': 'Type Save Successfully', 'Data':[]})   
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0,0,'TypeSave:'+str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data':[]})
        

        
        
        
class LogsOnDashboardView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
           
    @transaction.atomic()
    def get(self, request):
        try:
            with transaction.atomic():
                query = """ SELECT L_Transactionlog.id, L_Transactionlog.TranasactionDate AS TransactionDate, L_Transactionlog.Transactiontime, 
                            M_Users.LoginName AS UserName, L_Transactionlog.IPaddress, M_Parties.Name AS PartyName, 
                            L_Transactionlog.TransactionDetails, L_Transactionlog.JsonData, M_TransactionType.Name AS TransactionType,
                            L_Transactionlog.TransactionID, L_Transactionlog.FromDate, L_Transactionlog.ToDate, P.Name AS CustomerName
                            FROM TransactionLog.L_Transactionlog 
                            LEFT JOIN FoodERP.M_Users  ON L_Transactionlog.User = M_Users.id
                            LEFT JOIN FoodERP.M_Parties ON L_Transactionlog.PartyID = M_Parties.id
                            LEFT JOIN FoodERP.M_Parties P ON L_Transactionlog.CustomerID = P.id
                            LEFT JOIN FoodERP.M_TransactionType  ON L_Transactionlog.TransactionType = M_TransactionType.id
                            WHERE M_TransactionType.TransactionCategory = 92
                            ORDER BY L_Transactionlog.Transactiontime DESC LIMIT 20"""

            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()

            LogList = []
            for row in rows:
                LogList.append({
                    "id": row[0],
                    "TransactionDate": row[1],
                    "Transactiontime": row[2],
                    "UserName": row[3],
                    "IPaddress": row[4],
                    "PartyName": row[5],
                    "TransactionDetails": row[6],
                    "JsonData": row[7],
                    "TransactionType": row[8],
                    "TransactionID": row[9],
                    "FromDate": row[10],
                    "ToDate": row[11],
                    "CustomerName": row[12],
                })

            return JsonResponse({'StatusCode': 200, 'Status': True, 'Message': '', 'Data': LogList})
        
        except Exception as e:
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message': str(e), 'Data': []})






