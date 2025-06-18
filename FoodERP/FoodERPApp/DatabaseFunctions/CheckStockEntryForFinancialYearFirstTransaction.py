'''CREATE DEFINER=`pk`@`%` FUNCTION `CheckStockEntryForFinancialYearFirstTransaction`(FromDate Date,PartyID int,FinancialYear varchar(50),year_fs int) RETURNS tinyint
    READS SQL DATA
    DETERMINISTIC
BEGIN
DECLARE StockEntryDatewiseCount INT;

SELECT sum(bb)INTO StockEntryDatewiseCount  from
(SELECT COUNT(*)bb  FROM FoodERP.T_Stock WHERE StockDate between CONCAT(year_fs, '0331') AND FromDate AND Party_id=PartyID AND IsStockAdjustment=0
union
SELECT COUNT(*)bb  FROM SweetPOS.T_SPOSStock WHERE StockDate between CONCAT(year_fs, '0331') AND FromDate AND Party=PartyID AND IsStockAdjustment=0)a;

    if StockEntryDatewiseCount > 0 then	
		
        INSERT INTO M_FinancialYearFirstTransactionLog(FinancialYear,Party,Flag)VALUES(FinancialYear,PartyID,1);
		Return True;
	end if;
RETURN false;
END'''