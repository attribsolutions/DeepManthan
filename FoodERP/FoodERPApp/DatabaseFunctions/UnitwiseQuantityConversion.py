'''CREATE DEFINER=`pk`@`%` FUNCTION `UnitwiseQuantityConversion`(ItemID int,InputQuantity decimal(20,10),MCItemUnit int,MUnits int,ConversionMCItemUnit int,ConversionMUnits int,ShowDeletedUnitAlso int) RETURNS decimal(20,10)
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE IsDeletedFlag INT;
    DECLARE BaseUnitQuantityy DECIMAL(20, 10);
    DECLARE UnitID INT;
	DECLARE MCItemUnitID INT;
    declare ConversionUnitBaseQuantity decimal(20, 10);
    declare QuantityInBase decimal(20, 10);
    declare ConvertedQuantity decimal(20, 10);
    
		SELECT BaseUnitQuantity into BaseUnitQuantityy  from MC_ItemUnits where Item_id=ItemID and IsDeleted=0 and (id=MCItemUnit or UnitID_id=MUnits) ;
        
        SELECT BaseUnitQuantity into ConversionUnitBaseQuantity  from MC_ItemUnits where Item_id=ItemID and IsDeleted=0 and (id=ConversionMCItemUnit or UnitID_id=ConversionMUnits) ;
		if 	ConversionUnitBaseQuantity is not null  THEN
			set ConversionUnitBaseQuantity = ConversionUnitBaseQuantity;
        else
			set ConversionUnitBaseQuantity = 0;
		END IF;
        
        set QuantityInBase = InputQuantity * BaseUnitQuantityy;
        if ConversionUnitBaseQuantity = 0 THEN
			set ConvertedQuantity = 0;
        else
			 set ConvertedQuantity = (QuantityInBase/ConversionUnitBaseQuantity);
        
		END IF;
RETURN ConvertedQuantity;
END'''