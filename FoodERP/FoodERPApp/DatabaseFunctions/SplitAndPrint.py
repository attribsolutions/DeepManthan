'''CREATE DEFINER=`pk`@`%` FUNCTION `SplitAndPrint`(input_string VARCHAR(255),ItemID int,PartyID int,MRP decimal(20,10),GST decimal(20,10) ,BaseUnitQuantityForselectedUnit decimal(20,10),BaseUnitQuantityForNoUnit decimal(20,10),WithGSTRate decimal(20,10)) RETURNS decimal(20,10)
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE value VARCHAR(255);
    DECLARE value_start INT;
    DECLARE value_end INT;
    DECLARE delimiter_length INT;
    DECLARE is_done BOOLEAN;
    declare Marginn DECIMAL(20, 10);
    declare MkUpMkDnn int;
    declare GSTRate DECIMAL(20, 10);
    declare RatewithoutGST DECIMAL(20, 10);
    declare RatewithGSTT decimal(20,10);
    declare RatewithoutGSTT DECIMAL(20, 10);
    declare Rate DECIMAL(20, 10);
    
    SET delimiter_length = LENGTH(',');
    SET value_start = 1;
    SET is_done = FALSE;

    WHILE NOT is_done DO
        SET value_end = IF(LOCATE(',', input_string, value_start) = 0, LENGTH(input_string) + 1, LOCATE(',', input_string, value_start));
        SET value = SUBSTRING(input_string, value_start, value_end - value_start);
        SET value_start = value_end + delimiter_length;

        
        
        select MkUpMkDn into MkUpMkDnn from M_PriceList where id = value;
        select GetTodaysDateMargin(ItemID,CURDATE(),value,PartyID,0)Margin into Marginn;
        if MkUpMkDnn = 0 then
			set GSTRate = MRP /(100+Marginn)*100;
        else
			set GSTRate = MRP - (MRP *(Marginn/100));
        END IF;
        set RatewithoutGST=GSTRate*100/(100+GST) ;
        set MRP = GSTRate;
        
        IF value_end >= LENGTH(input_string) THEN
            SET is_done = TRUE;
        END IF;
    END WHILE;
	
    set RatewithGSTT = (BaseUnitQuantityForselectedUnit/BaseUnitQuantityForNoUnit) * GSTRate  ;
	set RateWithoutGSTT = (BaseUnitQuantityForselectedUnit/BaseUnitQuantityForNoUnit) * RatewithoutGST ;
    
    if WithGSTRate =1 then
		set Rate = round(RatewithGSTT,2);
    else   
		set Rate = round(RateWithoutGSTT,2);
    end if;    

RETURN Rate;
END'''