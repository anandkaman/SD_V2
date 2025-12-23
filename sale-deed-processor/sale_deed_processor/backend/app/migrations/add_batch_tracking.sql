-- Add batch_id column to document_details table
ALTER TABLE document_details ADD COLUMN batch_id VARCHAR(100);

-- Create index for faster batch queries
CREATE INDEX idx_document_details_batch_id ON document_details(batch_id);

-- Create batch_sessions table for metadata tracking
CREATE TABLE IF NOT EXISTS batch_sessions (
    id SERIAL PRIMARY KEY,
    batch_id VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    uploaded_count INTEGER DEFAULT 0,
    processed_count INTEGER DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    batch_name VARCHAR(200),
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE INDEX idx_batch_sessions_batch_id ON batch_sessions(batch_id);
CREATE INDEX idx_batch_sessions_created_at ON batch_sessions(created_at DESC);