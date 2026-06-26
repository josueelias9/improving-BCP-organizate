-- Migration: Move currency field from documents to transactions
-- Date: 2025-12-17
-- Description:
--   - Remove currency column from documents table
--   - Add currency column to transactions table
--   - Copy currency value from document.data JSON to transaction.currency for existing records

-- Step 1: Add currency column to transactions table
ALTER TABLE transactions ADD COLUMN currency VARCHAR DEFAULT '';

-- Step 2: Update existing transactions with currency from their parent document
-- Note: This assumes the currency is stored in the document.data JSON field
-- Adjust the JSON path according to your actual data structure
UPDATE transactions t
SET currency = d.data->>'currency'
FROM documents d
WHERE t.document_id = d.id
  AND d.data IS NOT NULL
  AND d.data->>'currency' IS NOT NULL;

-- Step 3: Remove currency column from documents table
ALTER TABLE documents DROP COLUMN currency;

-- Verification queries (uncomment to check the migration):
-- SELECT COUNT(*) as transactions_with_currency FROM transactions WHERE currency != '';
-- SELECT COUNT(*) as transactions_without_currency FROM transactions WHERE currency = '';
