-- Add remarks column to property_details table
ALTER TABLE property_details ADD COLUMN remarks TEXT;

-- Add index for faster filtering (optional)
CREATE INDEX IF NOT EXISTS idx_property_remarks ON property_details(remarks);

-- Verify column was added
SELECT sql FROM sqlite_master WHERE type='table' AND name='property_details';
