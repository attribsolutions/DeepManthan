'''CREATE DEFINER=`pk`@`%` FUNCTION `EmployeeParties`(EmployeeID int) RETURNS varchar(16383) CHARSET utf8mb4
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE PartyIDs VARCHAR(16383); 
    DECLARE PartyID VARCHAR(2000); 
    DECLARE done INT DEFAULT FALSE;
    DECLARE cur CURSOR FOR SELECT Party_id FROM MC_ManagementParties WHERE Employee_id = EmployeeID order by Party_id ;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    SET PartyIDs = '';

    OPEN cur;

    read_loop: LOOP
        FETCH cur INTO PartyID;
        IF done THEN
            LEAVE read_loop;
        END IF;

        SET PartyIDs = CONCAT(PartyIDs, PartyID, ',');
    END LOOP;

    CLOSE cur;

    RETURN PartyIDs;
END'''