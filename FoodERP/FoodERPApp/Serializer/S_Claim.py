
from ..models import *
from rest_framework import serializers

class PartyDetailSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    MobileNo = serializers.CharField(max_length=500)
    Address =serializers.CharField(max_length=500)
    FSSAINo =serializers.CharField(max_length=500)
    GSTIN = serializers.CharField(max_length=500)


class ClaimSummarySerializer(serializers.Serializer):
    
    id = serializers.IntegerField()
    ReturnDate=serializers.DateField()
    FullReturnNumber = serializers.CharField(max_length=500)
    CustomerName=serializers.CharField(max_length=500)
    ItemName = serializers.CharField(max_length=500)
    MRP = serializers.DecimalField(max_digits=10, decimal_places=2)
    Quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    GST = serializers.DecimalField(max_digits=10, decimal_places=2)
    Rate=serializers.DecimalField(max_digits=10, decimal_places=2)       
    CGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    SGST=serializers.DecimalField(max_digits=10, decimal_places=2)
    Amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    ApprovedQuantity =  serializers.DecimalField(max_digits=10, decimal_places=2)
    Discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    DiscountAmount = serializers.DecimalField(max_digits=10, decimal_places=2)
    TaxableAmount= serializers.DecimalField(max_digits=10, decimal_places=2)


class MasterclaimReportSerializer(serializers.Serializer):
    
    id= serializers.IntegerField()
    Item_id = serializers.IntegerField()
    PrimaryAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    secondaryAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    ReturnAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    NetPurchaseValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    Budget=serializers.DecimalField(max_digits=10, decimal_places=2)
    ClaimAgainstNetSale =serializers.DecimalField(max_digits=10, decimal_places=2) 

class MasterclaimReasonReportSerializer(serializers.Serializer):
    
    id= serializers.IntegerField()
    ItemReason_id = serializers.IntegerField()
    PrimaryAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    secondaryAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    ReturnAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    NetPurchaseValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    Budget=serializers.DecimalField(max_digits=10, decimal_places=2)
    ClaimAgainstNetSale =serializers.DecimalField(max_digits=10, decimal_places=2)    


class ReasonwiseMasterClaimSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    ItemReasonName = serializers.CharField(max_length=500)
    PurchaseAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    SaleAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    ReturnAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    NetSaleValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    Budget=serializers.DecimalField(max_digits=10, decimal_places=2)
    ClaimAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    ClaimAgainstNetSale =serializers.DecimalField(max_digits=10, decimal_places=2)    


class ProductwiseMasterClaimSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    Product = serializers.CharField(max_length=500)
    PurchaseAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    SaleAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    ReturnAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    NetSaleValue = serializers.DecimalField(max_digits=10, decimal_places=2)
    Budget=serializers.DecimalField(max_digits=10, decimal_places=2)
    ClaimAmount=serializers.DecimalField(max_digits=10, decimal_places=2)
    ClaimAgainstNetSale =serializers.DecimalField(max_digits=10, decimal_places=2)           


class ClaimlistSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    PartyID = serializers.IntegerField()
    PartyName= serializers.CharField(max_length=500)
    PartyType= serializers.CharField(max_length=500)  
    PrimaryAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    SecondaryAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    ReturnAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    returncnt = serializers.CharField(max_length=500)


class ClaimlistforClaimTrackingSerializer(serializers.Serializer):
    id= serializers.IntegerField()
    ClaimAmount= serializers.DecimalField(max_digits=10, decimal_places=2)
    PartyID = serializers.IntegerField()
    PartyName= serializers.CharField(max_length=500)
    PartyTypeID = serializers.IntegerField()
    PartyTypeName= serializers.CharField(max_length=500)
    
class ClaimTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model =  T_ClaimTrackingEntry
        fields = '__all__'
        
          
class ClaimTrackingSerializerSecond(serializers.Serializer):
    id= serializers.IntegerField()
    Date =  serializers.DateField()
    Month =  serializers.CharField(max_length=500)  
    Year = serializers.CharField(max_length=500) 
    ClaimReceivedSource =  serializers.CharField(max_length=500) 
    Type = serializers.IntegerField()
    TypeName = serializers.CharField(max_length=500)
    ClaimTrade = serializers.IntegerField()
    ClaimTradeName = serializers.CharField(max_length=500)
    TypeOfClaim = serializers.IntegerField()
    TypeOfClaimName = serializers.CharField(max_length=500)
    ClaimAmount =serializers.DecimalField(max_digits=20, decimal_places=2)
    Remark = serializers.CharField(max_length=500) 
    ClaimCheckBy =serializers.IntegerField()
    ClaimCheckByName = serializers.CharField(max_length=500) 
    CreditNotestatus =serializers.IntegerField()
    CreditNotestatusName = serializers.CharField(max_length=500) 
    CreditNoteNo = serializers.CharField(max_length=500) 	
    CreditNoteDate = serializers.DateField()	
    CreditNoteAmount	= serializers.DecimalField(max_digits=20, decimal_places=2)
    ClaimSummaryDate = serializers.DateField()	
    CreditNoteUpload = serializers.CharField(max_length=500)
    Claim_id = serializers.IntegerField()
    Party_id= serializers.IntegerField()
    PartyName = serializers.CharField(max_length=500)
    FullClaimNo=serializers.CharField(max_length=500) 
    PartyType_id= serializers.IntegerField() 
    PartyTypeName = serializers.CharField(max_length=500)
 

    
    
   
        