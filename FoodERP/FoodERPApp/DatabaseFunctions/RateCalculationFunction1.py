#OLD FUNCTION CODE

'''CREATE DEFINER=`pk`@`%` FUNCTION `RateCalculationFunction1`(BatchID int,ItemID int,PartyID int,MUnit int,MCItemUnit int,PriceList int,selectedMRP int,WithGSTRate int) RETURNS decimal(20,10)
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE MRPValuee DECIMAL(20, 10);
    DECLARE GSTPercentagee DECIMAL(20, 10);
    
    DECLARE BaseUnitQuantityForselectedUnit DECIMAL(20, 10);
    declare PriceList1 int;
    declare PriceListt int;
    declare CalculationPathh varchar(100);
    declare BaseUnitQuantityForNoUnit decimal(20, 10);
    declare ConvertedQuantity decimal(20, 10);
    declare Rate decimal(20, 10);
    
		SELECT GetTodaysDateMRP(ItemID,CURDATE(),2,0,0,0)MRPValue,GSTHsnCodeMaster(ItemID,CURDATE(),2,0,0)GSTPercentage into MRPValuee, GSTPercentagee   from M_Items where id=ItemID;
		if selectedMRP !=0 then
			set MRPValuee = selectedMRP;
        else
			set MRPValuee = MRPValuee;
        end if;
        
        if MCItemUnit > 0 then
			select BaseUnitQuantity into BaseUnitQuantityForselectedUnit from MC_ItemUnits where Item_id=ItemID and MC_ItemUnits.id=MCItemUnit;
		else
			select BaseUnitQuantity into BaseUnitQuantityForselectedUnit from MC_ItemUnits where Item_id=ItemID and IsDeleted=0 AND MC_ItemUnits.UnitID_id=MUnit;
		end if;
        
        select BaseUnitQuantity into BaseUnitQuantityForNoUnit  from MC_ItemUnits where Item_id=ItemID and IsDeleted=0 and UnitID_id=1;
        
        
        if PriceList > 0 then
            set PriceList1 = PriceList;
        else
            select PriceList_id into PriceListt from M_Parties where id=PartyID;
            set PriceList1 = PriceListt;
        end if;
         
        SELECT CalculationPath into CalculationPathh from M_PriceList where id = PriceList1;
        
        SELECT SplitAndPrint(CalculationPathh ,ItemID ,PartyID ,MRPValuee ,GSTPercentagee,BaseUnitQuantityForselectedUnit,BaseUnitQuantityForNoUnit ,WithGSTRate ) Rate into Rate;
				 
		RETURN Rate;
END'''



#NEW FUNCTION CODE -> ADD MRP AND GST FUNCTION CONDITIONS

'''CREATE DEFINER=`pk`@`%` FUNCTION `RateCalculationFunction1`(BatchID int,ItemID int,PartyID int,MUnit int,MCItemUnit int,PriceList int,selectedMRP int,WithGSTRate int) RETURNS decimal(20,10)
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE MRPValuee DECIMAL(20, 10);
    DECLARE GSTPercentagee DECIMAL(20, 10);
    
    DECLARE BaseUnitQuantityForselectedUnit DECIMAL(20, 10);
    declare PriceList1 int;
    declare PriceListt int;
    declare CalculationPathh varchar(100);
    declare BaseUnitQuantityForNoUnit decimal(20, 10);
    declare ConvertedQuantity decimal(20, 10);
    declare Rate decimal(20, 10);
    
		SELECT GetTodaysDateMRP(ItemID,CURDATE(),2,0,PartyID,0)MRPValue,GSTHsnCodeMaster(ItemID,CURDATE(),2,PartyID,0)GSTPercentage into MRPValuee, GSTPercentagee   from M_Items where id=ItemID;
		if selectedMRP !=0 then
			set MRPValuee = selectedMRP;
        else
			set MRPValuee = MRPValuee;
        end if;
        
        if MCItemUnit > 0 then
			select BaseUnitQuantity into BaseUnitQuantityForselectedUnit from MC_ItemUnits where Item_id=ItemID and MC_ItemUnits.id=MCItemUnit;
		else
			select BaseUnitQuantity into BaseUnitQuantityForselectedUnit from MC_ItemUnits where Item_id=ItemID and IsDeleted=0 AND MC_ItemUnits.UnitID_id=MUnit;
		end if;
        
        select BaseUnitQuantity into BaseUnitQuantityForNoUnit  from MC_ItemUnits where Item_id=ItemID and IsDeleted=0 and UnitID_id=1;
        
        
        if PriceList > 0 then
            set PriceList1 = PriceList;
        else
            select PriceList_id into PriceListt from M_Parties where id=PartyID;
            set PriceList1 = PriceListt;
        end if;
         
        SELECT CalculationPath into CalculationPathh from M_PriceList where id = PriceList1;
        
        SELECT SplitAndPrint(CalculationPathh ,ItemID ,PartyID ,MRPValuee ,GSTPercentagee,BaseUnitQuantityForselectedUnit,BaseUnitQuantityForNoUnit ,WithGSTRate ) Rate into Rate;
				 
		RETURN Rate;
END'''