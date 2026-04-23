-- Add telegram_status column to leads table
-- Run this SQL in Supabase SQL Editor

ALTER TABLE leads 
ADD COLUMN IF NOT EXISTS telegram_status TEXT;

-- Add comment for documentation
COMMENT ON COLUMN leads.telegram_status IS 'Telegram alert status: sent / failed / null';

-- Optional: Add index if filtering by status becomes common
-- CREATE INDEX IF NOT EXISTS idx_leads_telegram_status ON leads(telegram_status);
