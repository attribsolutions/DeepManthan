# OLD VERSION OF FUNCTION

'''CREATE DEFINER=`pk`@`%` FUNCTION `GetTodaysDateMRP`(ItemID int,EffectiveDate1 Date,Modee int ,DivisionID int,PartyID int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
     DECLARE IDD INT;
    DECLARE MRPP DECIMAL(20, 10);
    DECLARE result varchar(50);
	
    
		SELECT id, MRP into IDD,MRPP FROM M_MRPMaster where Item_id=ItemID and EffectiveDate<=EffectiveDate1 order by EffectiveDate desc, id desc limit 1;
        if Modee = 1 then
			set result=IDD;
        ELSE 
			set result=MRPP;
        END IF;
        
RETURN result;
END'''


# NEW VERSION OF FUNCTION -> Changes for Chitale Americas -> add PartyType condition

'''CREATE DEFINER=`pk`@`%` FUNCTION `GetTodaysDateMRP`(ItemID int,EffectiveDate1 Date,Modee int ,DivisionID int,PartyID int,PartyTypeID int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE IDD INT;
    DECLARE MRPP DECIMAL(20, 10);
    DECLARE result varchar(50);
	declare PT_ID int(10);
    declare PartyType int(10);
    declare EffectiveDatee date;
        
		if PartyID > 0 then 
			select PartyType_id into PT_ID from M_Parties where id=PartyID;
            set PartyType = PT_ID;
		else
			set PartyType = PartyTypeID;
        end if;
        
        
        if PartyID > 0 then
			SELECT id, MRP,EffectiveDate into IDD,MRPP,EffectiveDatee FROM M_MRPMaster where Item_id=ItemID
            and EffectiveDate<=EffectiveDate1 and Party_id=PartyID and PartyType_id is null and IsDeleted=0 order by EffectiveDate desc, id desc limit 1;
		end if;  
        
        if MRPP is null  then
            
			if PartyType > 0 then
				SELECT id, MRP, EffectiveDate into IDD,MRPP,EffectiveDatee FROM M_MRPMaster where Item_id=ItemID
				and EffectiveDate<=EffectiveDate1 and Party_id is null and PartyType_id = PartyType and IsDeleted=0 order by EffectiveDate desc, id desc limit 1;	
			end if;
            if MRPP is null  then
				SELECT id, MRP, EffectiveDate into IDD,MRPP,EffectiveDatee FROM M_MRPMaster where Item_id=ItemID
				and EffectiveDate<=EffectiveDate1 and Party_id is null and PartyType_id is null and IsDeleted=0 order by EffectiveDate desc, id desc limit 1;
			END IF;
        
        end if;    
       
        
        if Modee = 1 then
			set result=IDD;
        elseif Modee = 2 then
			set result=MRPP;
        elseif  Modee = 3 then  
			set result = EffectiveDatee;
        END IF;
        
RETURN result;
END'''