'''CREATE DEFINER=`pk`@`%` FUNCTION `GetStockEffectiveTransactionCountFromDateForPartyID`(FromDate Date,PartyID int) RETURNS tinyint(1)
    READS SQL DATA
    DETERMINISTIC
BEGIN
	DECLARE GRNCount INT;
	DECLARE InvoiceCount INT;
    DECLARE SalesReturnCount INT;
    DECLARE PurchaseReturnCount INT;
	
	SELECT COUNT(*) INTO GRNCount FROM T_GRNs WHERE GRNDate > FromDate  AND Party_id = PartyID;
	if GRNCount > 0 then
		Return False;
	end if;
	
	SELECT COUNT(*) INTO InvoiceCount FROM T_Invoices WHERE InvoiceDate > FromDate  AND Party_id = PartyID;
	if InvoiceCount > 0 then
		Return False;
	end if;
	
	SELECT COUNT(*) INTO SalesReturnCount FROM T_PurchaseReturn WHERE ReturnDate > FromDate  AND Party_id = PartyID AND Mode = 1;
	if SalesReturnCount > 0 then
		Return False;
	end if;
	
	SELECT COUNT(*) INTO PurchaseReturnCount FROM T_PurchaseReturn WHERE ReturnDate > FromDate  AND Customer_id = PartyID AND Mode IN (2,3);
	if PurchaseReturnCount > 0 then
		Return False;
	end if;
    
    Return True;
END'''