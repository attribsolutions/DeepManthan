from ..models import *
from django.http import JsonResponse
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from ..Serializer.S_TallyLedger import *
from django.db import IntegrityError, transaction
from rest_framework.parsers import JSONParser
from django.db.models import Q
from datetime import datetime
from django.db import connection
from django.db.models import Max
from django.db import transaction
from rest_framework.response import Response
from ..Views.V_CommFunction import *
import calendar


class LedgerListView(CreateAPIView):
    permission_classes = (IsAuthenticated,)
    
    @transaction.atomic()
    def get(self, request ):
        try:
            with transaction.atomic():
                Ledger_data = M_Ledger.objects.all()
                Ledger_data_serializer = TallyLedgerSerializer(Ledger_data,many=True)                
                log_entry = create_transaction_logNew(request, Ledger_data_serializer,0,'',458,0)
                return JsonResponse({'StatusCode': 200, 'Status': True,'Message': '', 'Data': Ledger_data_serializer.data})        
        except Exception as e:
            log_entry = create_transaction_logNew(request, 0, 0,str(e),33,0)
            return JsonResponse({'StatusCode': 400, 'Status': True, 'Message':  str(e), 'Data':[]})
        
        
@transaction.atomic
def insert_voucher_with_details(full_voucher_number, voucher_number, voucher_type, voucher_date, grn_id, details):   

    
    voucher = T_Voucher.objects.create(
        FullVoucherNumber=full_voucher_number,
        VoucherNumber=voucher_number,
        VoucherType=voucher_type,
        VoucherDate=voucher_date,
        GRN_id=grn_id
    )
   
    voucher_details = [
        TC_VoucherDetails(
            DrAmt=item.get('DrAmt', 0),
            CrAmt=item.get('CrAmt', 0),
            LedgerId_id=item['LedgerId_id'],
            Voucher=voucher
        )
        for item in details
    ]
    TC_VoucherDetails.objects.bulk_create(voucher_details)

    return voucher