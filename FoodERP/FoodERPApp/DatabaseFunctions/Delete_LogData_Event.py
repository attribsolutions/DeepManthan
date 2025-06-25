'''DROP EVENT IF EXISTS delete_old_transaction_logs;

DELIMITER $$

CREATE EVENT delete_old_transaction_logs
ON SCHEDULE EVERY 1 DAY
DO
BEGIN
  -- Step 1: Delete from child table first
  DELETE child
  FROM L_TransactionLogJsonData child
  JOIN L_Transactionlog parent ON child.Transactionlog_id = parent.id
  WHERE parent.TranasactionDate < NOW() - INTERVAL 60 DAY;

  -- Step 2: Delete from parent table
  DELETE FROM L_Transactionlog
  WHERE TranasactionDate < NOW() - INTERVAL 60 DAY; 
  
  OPTIMIZE TABLE TransactionLog.L_TransactionLog;
  OPTIMIZE TABLE TransactionLog.L_TransactionLogJsonData;
  
  
END$$

DELIMITER ;'''