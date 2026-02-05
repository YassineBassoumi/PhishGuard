-- Migration: Add Multi-Provider Email Support
-- Date: 2026-02-04

-- Add provider column to users table to track connected providers
ALTER TABLE users ADD COLUMN IF NOT EXISTS connected_providers TEXT DEFAULT '[]';

-- Create email_providers configuration table
CREATE TABLE IF NOT EXISTS email_providers (
    id SERIAL PRIMARY KEY,
    provider_name VARCHAR(50) UNIQUE NOT NULL,
    oauth_authorize_url TEXT NOT NULL,
    oauth_token_url TEXT NOT NULL,
    api_base_url TEXT NOT NULL,
    scopes TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create user_email_credentials table to store provider-specific tokens
CREATE TABLE IF NOT EXISTS user_email_credentials (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider VARCHAR(20) NOT NULL,
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_expiry TIMESTAMP,
    email_address VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider)
);

-- Insert provider configurations
INSERT INTO email_providers (provider_name, oauth_authorize_url, oauth_token_url, api_base_url, scopes, is_active) 
VALUES 
    ('gmail', 
     'https://accounts.google.com/o/oauth2/v2/auth', 
     'https://oauth2.googleapis.com/token', 
     'https://gmail.googleapis.com', 
     'https://www.googleapis.com/auth/gmail.readonly', 
     true),
    ('outlook', 
     'https://login.microsoftonline.com/common/oauth2/v2.0/authorize', 
     'https://login.microsoftonline.com/common/oauth2/v2.0/token', 
     'https://graph.microsoft.com/v1.0', 
     'https://graph.microsoft.com/Mail.Read https://graph.microsoft.com/User.Read offline_access', 
     true),
    ('yahoo', 
     'https://api.login.yahoo.com/oauth2/request_auth', 
     'https://api.login.yahoo.com/oauth2/get_token', 
     'https://mail.yahoo.com', 
     'mail-r', 
     true)
ON CONFLICT (provider_name) DO NOTHING;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_user_email_credentials_user_provider ON user_email_credentials(user_id, provider);
CREATE INDEX IF NOT EXISTS idx_email_providers_active ON email_providers(is_active);
