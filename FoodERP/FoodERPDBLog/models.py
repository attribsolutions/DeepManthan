from django.db import models

# Create your models here.

class L_Transactionlog(models.Model):
    TranasactionDate =  models.DateField()
    Transactiontime = models.DateTimeField(auto_now_add=True)
    User = models.IntegerField()
    IPaddress = models.CharField(max_length=500)
    PartyID = models.IntegerField()
    TransactionDetails =  models.CharField(max_length=2000)
    JsonData = models.TextField(blank = True)
    TransactionType =  models.IntegerField(default=1)
    TransactionID =  models.IntegerField(default=1)
    FromDate = models.DateField(blank=True, null=True)
    ToDate = models.DateField(blank=True, null=True)
    CustomerID = models.IntegerField(default=1)
    # TransactionCategory =  models.IntegerField(blank=True, null=True)
    
    class Meta:
        db_table="L_Transactionlog"

class L_TransactionLogJsonData(models.Model):
    Transactionlog = models.ForeignKey(L_Transactionlog,related_name='Transactionlog', on_delete=models.CASCADE)
    JsonData = models.TextField(blank = True)
    class Meta:
        db_table = "L_TransactionLogJsonData"        
