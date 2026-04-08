-- Create messages table
CREATE TABLE messages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id UUID NOT NULL REFERENCES threads(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
  content TEXT NOT NULL,
  openai_message_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable Row-Level Security
ALTER TABLE messages ENABLE ROW LEVEL SECURITY;

-- RLS Policies — users can access messages whose thread belongs to them
CREATE POLICY "Users can view own messages"
  ON messages FOR SELECT
  USING (
    thread_id IN (SELECT id FROM threads WHERE user_id = auth.uid())
  );

CREATE POLICY "Users can insert own messages"
  ON messages FOR INSERT
  WITH CHECK (
    thread_id IN (SELECT id FROM threads WHERE user_id = auth.uid())
  );
