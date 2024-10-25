'''CREATE DEFINER=`pk`@`%` FUNCTION `GetTodaysDateRate`(ItemID int,EffectiveDate1 Date,Party int,PriceList int,Modee int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE IDD INT;
    DECLARE Rates DECIMAL(20, 10);
    DECLARE result varchar(50);
    DECLARE Unit INT;
    declare EffectiveDatee date;
    declare PriceListee int;     
     
  if Party > 0 then          
		 select PriceList_id into PriceListee FROM M_Parties WHERE id=Party;
        
         SELECT id, Rate,UnitID,EffectiveDate into IDD,Rates,Unit,EffectiveDatee FROM M_RateMaster where Party_id=Party and  Item_id=ItemID and EffectiveDate<=EffectiveDate1 and PriceList_id=PriceList and ISDeleted=0 order by EffectiveDate desc, id desc limit 1;
         
         if Rates is null then
				SELECT id, Rate,UnitID,EffectiveDate into IDD,Rates,Unit,EffectiveDatee FROM M_RateMaster where Party_id is Null and   Item_id=ItemID and EffectiveDate<=EffectiveDate1 and PriceList_id=PriceListee and ISDeleted=0 order by EffectiveDate desc, id desc limit 1;		 
		end if;
  else 
	  
	  SELECT id, Rate,UnitID,EffectiveDate into IDD,Rates,Unit,EffectiveDatee FROM M_RateMaster where Party_id is Null and   Item_id=ItemID and EffectiveDate<=EffectiveDate1 and PriceList_id=PriceList and ISDeleted=0 order by EffectiveDate desc, id desc limit 1;         
end if;   
        if Modee = 1 then
			set result=IDD;
		elseif Modee = 2 then
			set result=Rates;  
		elseif Modee = 3 then
			set result=EffectiveDatee;
        elseif Modee = 4 then
			set result=Unit;		
		End if;
 
 
RETURN result;
END'''