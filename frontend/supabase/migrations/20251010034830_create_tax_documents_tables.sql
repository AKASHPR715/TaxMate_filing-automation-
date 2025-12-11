/*
  # Create TaxMate Database Schema

  This migration creates the necessary tables for the TaxMate tax filing automation system.

  ## New Tables
  
  ### `documents`
  Stores uploaded tax documents and their processing status
  - `id` (uuid, primary key)
  - `user_id` (text) - User identifier
  - `file_name` (text) - Original file name
  - `file_type` (text) - File type (PDF, JSON, etc.)
  - `file_url` (text) - Storage URL for the file
  - `status` (text) - Processing status: pending, processing, completed, failed
  - `extracted_data` (jsonb) - AI-extracted information from the document
  - `created_at` (timestamptz) - Creation timestamp
  - `updated_at` (timestamptz) - Last update timestamp

  ### `tax_computations`
  Stores tax computation results for each user
  - `id` (uuid, primary key)
  - `user_id` (text) - User identifier
  - `assessment_year` (text) - Tax assessment year (e.g., "2024-25")
  - `total_income` (numeric) - Total income amount
  - `total_deductions` (numeric) - Total deductions claimed
  - `taxable_income` (numeric) - Calculated taxable income
  - `tax_liability` (numeric) - Final tax liability
  - `computation_data` (jsonb) - Detailed computation breakdown
  - `created_at` (timestamptz) - Creation timestamp
  - `updated_at` (timestamptz) - Last update timestamp

  ### `chat_history`
  Stores user interactions with the AI chat assistant
  - `id` (uuid, primary key)
  - `user_id` (text) - User identifier
  - `session_id` (text) - Chat session identifier
  - `message` (text) - User message
  - `response` (text) - AI response
  - `context` (jsonb) - Additional context data
  - `created_at` (timestamptz) - Creation timestamp

  ## Security
  - RLS enabled on all tables
  - Policies restrict access to user's own data only
*/

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  file_name text NOT NULL,
  file_type text NOT NULL,
  file_url text NOT NULL,
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
  extracted_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create tax_computations table
CREATE TABLE IF NOT EXISTS tax_computations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  assessment_year text NOT NULL,
  total_income numeric(12, 2) NOT NULL DEFAULT 0,
  total_deductions numeric(12, 2) NOT NULL DEFAULT 0,
  taxable_income numeric(12, 2) NOT NULL DEFAULT 0,
  tax_liability numeric(12, 2) NOT NULL DEFAULT 0,
  computation_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- Create chat_history table
CREATE TABLE IF NOT EXISTS chat_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text NOT NULL,
  session_id text NOT NULL,
  message text NOT NULL,
  response text NOT NULL,
  context jsonb DEFAULT '{}'::jsonb,
  created_at timestamptz DEFAULT now()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_tax_computations_user_id ON tax_computations(user_id);
CREATE INDEX IF NOT EXISTS idx_tax_computations_year ON tax_computations(assessment_year);
CREATE INDEX IF NOT EXISTS idx_chat_history_user_id ON chat_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_history_session ON chat_history(session_id);

-- Enable Row Level Security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE tax_computations ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

-- RLS Policies for documents table
CREATE POLICY "Users can view own documents"
  ON documents FOR SELECT
  USING (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can insert own documents"
  ON documents FOR INSERT
  WITH CHECK (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can update own documents"
  ON documents FOR UPDATE
  USING (user_id = current_setting('app.user_id', TRUE))
  WITH CHECK (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can delete own documents"
  ON documents FOR DELETE
  USING (user_id = current_setting('app.user_id', TRUE));

-- RLS Policies for tax_computations table
CREATE POLICY "Users can view own tax computations"
  ON tax_computations FOR SELECT
  USING (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can insert own tax computations"
  ON tax_computations FOR INSERT
  WITH CHECK (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can update own tax computations"
  ON tax_computations FOR UPDATE
  USING (user_id = current_setting('app.user_id', TRUE))
  WITH CHECK (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can delete own tax computations"
  ON tax_computations FOR DELETE
  USING (user_id = current_setting('app.user_id', TRUE));

-- RLS Policies for chat_history table
CREATE POLICY "Users can view own chat history"
  ON chat_history FOR SELECT
  USING (user_id = current_setting('app.user_id', TRUE));

CREATE POLICY "Users can insert own chat messages"
  ON chat_history FOR INSERT
  WITH CHECK (user_id = current_setting('app.user_id', TRUE));

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for automatic updated_at updates
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
  BEFORE UPDATE ON documents
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_tax_computations_updated_at ON tax_computations;
CREATE TRIGGER update_tax_computations_updated_at
  BEFORE UPDATE ON tax_computations
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();
