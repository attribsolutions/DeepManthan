from decimal import Decimal, InvalidOperation
from ..models import *
from rest_framework import serializers

class FloatDecimalField(serializers.Field):
    def to_representation(self, value):
        return float(value)
    
class GSTWiseSerializer(serializers.Serializer):
    # id = serializers.IntegerField()
    GSTPercentage=FloatDecimalField()
    TaxableValue=FloatDecimalField()
    CGST=FloatDecimalField()
    SGST=FloatDecimalField()
    IGST=FloatDecimalField()
    GSTAmount=FloatDecimalField()
    TotalValue=FloatDecimalField()
    
    
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(GSTWiseSerializer, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("GSTPercentage", 0):
            ret["GSTPercentage"] = 'TotalTCS'
        # if not ret.get("TaxableValue", 0):
        #     ret["TaxableValue"] = None
        # if not ret.get("CGST", 0):
        #     ret["CGST"] = None
        # if not ret.get("SGST", 0):
        #     ret["SGST"] = None 
        # if not ret.get("IGST", 0):
        #     ret["IGST"] = None
        # if not ret.get("GSTAmount", 0):
        #     ret["GSTAmount"] = None                
        # if not ret.get("TotalValue", 0):
        #     ret["TotalValue"] = None     
        return ret 
    
    
    
  
    
class GSTWiseSerializer2(serializers.Serializer):
    id = serializers.CharField(max_length=500)
    TotalTaxableValue =FloatDecimalField()
    TotalCGST =FloatDecimalField()
    TotalSGST =FloatDecimalField()
    TotalIGST =FloatDecimalField()
    TotalGSTAmount =FloatDecimalField()
    GrandTotal =FloatDecimalField()
    
    def to_representation(self, instance):
        # get representation from ModelSerializer
        ret = super(GSTWiseSerializer2, self).to_representation(instance)
        # if parent is None, overwrite
        if not ret.get("TaxableValue", 0):
            ret["TaxableValue"] = None
        if not ret.get("TotalCGST", 0):
            ret["TotalCGST"] = None
        if not ret.get("TotalSGST", 0):
            ret["TotalSGST"] = None 
        if not ret.get("TotalIGST", 0):
            ret["TotalIGST"] = None
        if not ret.get("TotalGSTAmount", 0):
            ret["TotalGSTAmount"] = None                
        if not ret.get("GrandTotal", 0):
            ret["GrandTotal"] = None     
        return ret 
   

###########################################################################################################