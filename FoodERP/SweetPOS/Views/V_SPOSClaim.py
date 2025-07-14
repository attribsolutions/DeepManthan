from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
import base64
from django.db import transaction
from rest_framework.parsers import JSONParser
from rest_framework.authentication import BasicAuthentication
from rest_framework.response import Response
from django.contrib.auth import authenticate
from FoodERPApp.Views.V_CommFunction import *
from FoodERPApp.models import *
from FoodERPApp.models import  *
from django.db.models import *
from datetime import timedelta
from SweetPOS.Views.SweetPOSCommonFunction import *
from FoodERPApp.Views.V_TransactionNumberfun import *
from django.db.models import Min, Max



class SwiggyZomatoClaimListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)

    @transaction.atomic
    def post(self, request):
        ClaimData = JSONParser().parse(request)
        try:
            with transaction.atomic():
                PartyID = ClaimData['PartyID']
                FromDate = ClaimData['FromDate']
                ToDate = ClaimData['ToDate']

                SZClaimListData = []

                query = f'''SELECT 1 as id,M_Parties.Name AS PartyName,cust.Name AS CustomerName,M_Users.LoginName AS UserName,
                            SUM(II.BasicAmount) AS TotalBasicAmount,(SUM(II.BasicAmount) * (3.5 / 100)) AS ClaimAmount
                            FROM SweetPOS.T_SPOSInvoices I
                            JOIN SweetPOS.TC_SPOSInvoiceItems II ON I.id = II.Invoice_id
                            JOIN FoodERP.M_Items ON M_Items.id = II.Item AND M_Items.IsThirdPartyItem = 1
                            JOIN FoodERP.M_Users ON M_Users.id = I.CreatedBy AND M_Users.POSRateType = 175
                            JOIN FoodERP.M_Parties ON M_Parties.id = I.Party
                            JOIN FoodERP.M_Parties cust ON cust.id = I.Customer
                            WHERE I.InvoiceDate BETWEEN '{FromDate}' AND '{ToDate}'
                        '''

                # Add Party filter only if PartyID > 0
                if PartyID > 0:
                    query += f' AND I.Party = {PartyID}'

                query += ' GROUP BY M_Parties.id, cust.id, M_Users.id'

                SZClaimDataQuery = T_SPOSInvoices.objects.raw(query)

                for record in SZClaimDataQuery:
                    SZClaimListData.append({
                        "PartyName": record.PartyName,
                        "CustomerName": record.CustomerName,
                        "UserName": record.UserName,
                        "TotalBasicAmount": round(float(record.TotalBasicAmount), 2),
                        "ClaimAmount": round(float(record.ClaimAmount), 2),
                    })

                if SZClaimListData:
                    log_entry = create_transaction_logNew(request, ClaimData, PartyID, "SwiggyZomatoClaimData", 487, 0, FromDate, ToDate, 0)
                    return JsonResponse({"StatusCode": 200, "Status": True, "Message": "SwiggyZomatoClaimData", "Data": SZClaimListData})

                log_entry = create_transaction_logNew(request, ClaimData, PartyID, "No SwiggyZomatoClaimData found", 487, 0, FromDate, ToDate, 0)
                return JsonResponse({"StatusCode": 204, "Status": True, "Message": "No SwiggyZomatoClaimData found.", "Data": []})

        except Exception as e:
            log_entry = create_transaction_logNew(request, ClaimData, PartyID, "SwiggyZomatoClaimData Error: " + str(e), 33, 0)
            return JsonResponse({"StatusCode": 400, "Status": False, "Message": str(e), "Data": []})
