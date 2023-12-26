# yourapp/management/commands/my_cron_job.py

from datetime import date
from django.core.management.base import BaseCommand
from django.utils import timezone

from models import Transactionlog

class Command(BaseCommand):
    help = 'Your description of the cron job'
    print(help)
    def handle(self, *args, **kwargs):
        # Your cron job logic here
        log_entry = Transactionlog.objects.create(
        TranasactionDate=date.today(),
        User=1, PartyID=1, IPaddress='10.4.5.64', TransactionDetails=1, JsonData=1, TransactionType=1, TransactionID=1
    )
    # return log_entry
        self.stdout.write(self.style.SUCCESS(f'Cron job executed at {timezone.now()}'))
