-- Migration: Add user_info and user_tickets tables
-- Created: 2024-12-18
-- Description: Adds user info form tracking and ticket system tables

-- Create user_info table
CREATE TABLE IF NOT EXISTS user_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(200) NOT NULL,
    number_of_files INTEGER NOT NULL,
    file_region VARCHAR(200) NOT NULL,
    date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    batch_id VARCHAR(100),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index on batch_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_info_batch_id ON user_info(batch_id);

-- Create user_tickets table
CREATE TABLE IF NOT EXISTS user_tickets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_name VARCHAR(200) NOT NULL,
    batch_id VARCHAR(100),
    error_type VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'open',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME
);

-- Create index on batch_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_tickets_batch_id ON user_tickets(batch_id);

-- Create index on status for filtering
CREATE INDEX IF NOT EXISTS idx_user_tickets_status ON user_tickets(status);
