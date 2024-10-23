'''CREATE DEFINER=`pk`@`%` FUNCTION `GetTodaysDateMargin`(ItemID int,EffectiveDatee Date,PriceListID int,PartyID int,Modee int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE Marginn DECIMAL(20, 10);
    DECLARE PriceListt INT;
    DECLARE DiscountTypee DECIMAL(20, 10);
    DECLARE result varchar(50);
	
        if PartyID > 0 then
			select Margin into Marginn from M_MarginMaster 
where Item_id=ItemID and PriceList_id=PriceListID and IsDeleted=0 and Party_id=PartyID and EffectiveDate <= EffectiveDatee order by EffectiveDate desc ,id desc limit 1;
        else
			select Margin into Marginn from M_MarginMaster 
where Item_id=ItemID and PriceList_id=PriceListID and IsDeleted=0 and Party_id is null  and EffectiveDate <= EffectiveDatee order by EffectiveDate desc ,id desc limit 1;
        END IF;
        
        if Marginn is null then
			select Margin into Marginn from M_MarginMaster 
where Item_id=ItemID and PriceList_id=PriceListID and IsDeleted=0 and Party_id is null  and EffectiveDate <= EffectiveDatee order by EffectiveDate desc ,id desc limit 1;
		END if;
        if Marginn  is null then
			set result = 0;
        else
			set result = Marginn;
         END IF;
RETURN result;
END'''