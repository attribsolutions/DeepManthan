'''CREATE DEFINER=`pk`@`%` FUNCTION `GetAllCompanyIDsFromLoginCompany`(CompanyID int) RETURNS varchar(16383) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE CompanyIDs VARCHAR(16383); 
    DECLARE CompanyID VARCHAR(2000); 
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR select id from C_Companies where CompanyGroup_id in(select CompanyGroup_id CompanyGroupID from C_Companies where id=3)  ;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SET CompanyIDs = '';

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO CompanyID;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET CompanyIDs = CONCAT(CompanyIDs, CompanyID, ',');
    END LOOP;

    CLOSE cur;

    RETURN CompanyIDs;
END'''