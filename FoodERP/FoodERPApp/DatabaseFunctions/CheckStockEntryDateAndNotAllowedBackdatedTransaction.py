'''CREATE DEFINER=`pk`@`%` FUNCTION `CheckStockEntryDateAndNotAllowedBackdatedTransaction`(TransactionDate Date,PartyID int) RETURNS tinyint(1)
    READS SQL DATA
    DETERMINISTIC
BEGIN
DECLARE StockEntryDate date;
SELECT StockDate INTO StockEntryDate  FROM T_Stock WHERE  Party_id=PartyID AND IsStockAdjustment=0 ORDER BY StockDate desc LIMIT 1;
if StockEntryDate then
	if TransactionDate > StockEntryDate then
		Return True; 
	end if;
else
	Return True; 
end if;   
RETURN false;
END'''