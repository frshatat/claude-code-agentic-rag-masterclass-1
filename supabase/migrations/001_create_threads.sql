-- Create threads table
CREATE TABLE threads (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  openai_thread_id TEXT NOT NULL,
  title TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row-Level Security
ALTER TABLE threads ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY "Users can view own threads"
  ON threads FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own threads"
  ON threads FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own threads"
  ON threads FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own threads"
  ON threads FOR DELETE
  USING (auth.uid() = user_id);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER set_threads_updated_at
  BEFORE UPDATE ON threads
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
