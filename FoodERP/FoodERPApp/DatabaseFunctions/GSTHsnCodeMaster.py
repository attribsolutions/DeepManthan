# OLD VERSION OF FUNCTION

'''CREATE DEFINER=`pk`@`%` FUNCTION `GSTHsnCodeMaster`(ItemID int,EffectiveDate Date,Modee int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE IDD INT;
    DECLARE GSTPercentagee DECIMAL(20, 10);
    DECLARE HSNCodee varchar(50);
    DECLARE result varchar(50);
	
    
		SELECT id,GSTPercentage,HSNCode into IDD,GSTPercentagee,HSNCodee FROM M_GSTHSNCode where Item_id=ItemID and EffectiveDate <= EffectiveDate order by  EffectiveDate desc,id desc limit 1;
        if Modee = 1 then
			set result=IDD;
        ELSEIF Modee = 2 then
			set result=GSTPercentagee;
        else  
			set result=HSNCodee;
        END IF;
        
RETURN result;
END'''

# NEW VERSION OF FUNCTION -> Changes for Chitale Americas -> add PartyType condition

'''CREATE DEFINER=`pk`@`%` FUNCTION `GSTHsnCodeMaster`(ItemID int,EffectiveDate Date,Modee int,PartyID int,PartyTypeID int) RETURNS varchar(200) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
    DECLARE IDD INT;
    DECLARE GSTPercentagee DECIMAL(20, 10);
    DECLARE HSNCodee varchar(50);
    DECLARE result varchar(50);
    declare PT_ID int(10);
    declare PartyType int(10);
    
		if PartyID > 0 then 
			select PartyType_id into PT_ID from M_Parties where id=PartyID;
            set PartyType = PT_ID;
		else
			set PartyType = PartyTypeID;
        end if;
        
        if PartyType > 0 then
			SELECT id,GSTPercentage,HSNCode into IDD,GSTPercentagee,HSNCodee FROM M_GSTHSNCode 
            where Item_id=ItemID and EffectiveDate <= EffectiveDate  and PartyType_id = PartyType  
            and IsDeleted=0
            order by  EffectiveDate desc,id desc limit 1;
        end if;
        
        if GSTPercentagee is null then
			SELECT id,GSTPercentage,HSNCode into IDD,GSTPercentagee,HSNCodee FROM M_GSTHSNCode 
            where Item_id=ItemID and EffectiveDate <= EffectiveDate and PartyType_id is null 
            and IsDeleted=0
            order by  EffectiveDate desc,id desc limit 1;
        END IF;
        
        if Modee = 1 then
			set result=IDD;
        ELSEIF Modee = 2 then
			set result=GSTPercentagee;
        ELSEIF Modee = 3 then  
			set result=HSNCodee;
       
        END IF;
        
RETURN result;
END'''