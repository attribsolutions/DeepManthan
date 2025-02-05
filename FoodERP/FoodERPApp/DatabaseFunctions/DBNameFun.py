'''CREATE DEFINER=`pk`@`%` FUNCTION `DBNameFun`(A VARCHAR(50)) RETURNS varchar(50) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE DBName VARCHAR(50);
	
    if A = 'default' then 
		select DefaultValue into DBName from M_Settings where id=36;
        return DBName;
    end if ;
    if A = 'TransactionLog' then 
		select DefaultValue into DBName from M_Settings where id=37;
        return DBName;
    end if ;
    if A = 'SweetPOS' then 
		select DefaultValue into DBName from M_Settings where id=38;
        return DBName;
    end if ;


END'''