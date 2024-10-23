'''CREATE DEFINER=`pk`@`%` FUNCTION `GetTodaysDateDiscount`(ItemID int,EffectiveDate Date,Modee int ,Customer int,PartyID int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE Discountt INT;
    DECLARE PriceListt INT;
    DECLARE DiscountTypee DECIMAL(20, 10);
    DECLARE result varchar(50);
	
        SELECT PriceList_id into PriceListt FROM M_Parties where id=Customer;
			set PriceListt = PriceListt;
            
        if Customer > 0 then
			SELECT Discount ,DiscountType into Discountt,DiscountTypee  FROM M_DiscountMaster where Item_id=ItemID and PriceList_id=PriceListt and Party_id=PartyID and 
FromDate<=EffectiveDate  and ToDate >= EffectiveDate and Customer_id=Customer and IsDeleted=0 order by id desc limit 1;
        else
			SELECT Discount,DiscountType into Discountt,DiscountTypee  FROM M_DiscountMaster where Item_id=ItemID and PriceList_id=PriceListt and Party_id=PartyID and 
FromDate<=EffectiveDate  and ToDate >= EffectiveDate and Customer_id is null and IsDeleted=0 order by id desc limit 1;
        end if;
        
        if Discountt is null then
			SELECT Discount,DiscountType into Discountt,DiscountTypee  FROM M_DiscountMaster where Item_id=ItemID and PriceList_id=PriceListt and Party_id=PartyID and 
FromDate<=EffectiveDate  and ToDate >= EffectiveDate and Customer_id is null and IsDeleted=0 order by id desc limit 1;
        end if;
        if Discountt is null then
			set result= '';
        else    
            if Modee = 1 then
				set result=Discountt;
			ELSE 
				set result=DiscountTypee;
			END IF;
        end if;
RETURN result;
END'''