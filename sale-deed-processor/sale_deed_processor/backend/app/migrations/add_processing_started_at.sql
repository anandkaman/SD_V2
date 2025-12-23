-- Add processing_started_at column to batch_sessions table
-- This tracks when processing actually started (when user clicks Start Processing button)
-- The existing created_at column tracks when files were uploaded

ALTER TABLE batch_sessions
ADD COLUMN IF NOT EXISTS processing_started_at TIMESTAMP;

-- Create index for faster queries on processing start time
CREATE INDEX IF NOT EXISTS idx_batch_sessions_processing_started_at
ON batch_sessions(processing_started_at DESC);