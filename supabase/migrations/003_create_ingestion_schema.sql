-- Enable pgvector extension for embeddings
create extension if not exists vector;

-- Public documents table (stores file metadata)
create table if not exists public.documents (
  id uuid default gen_random_uuid() primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  file_name text not null,
  file_size_bytes bigint not null,
  content_hash text not null unique,
  status text check (status in ('uploading', 'processing', 'complete', 'error')) default 'uploading',
  error_message text,
  created_at timestamp default now(),
  updated_at timestamp default now()
);

-- RLS: Users see only their own documents
alter table public.documents enable row level security;
create policy "Users can read/insert/update/delete own documents"
  on public.documents
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Chunks table (document split into chunks for embedding)
create table if not exists public.chunks (
  id uuid default gen_random_uuid() primary key,
  document_id uuid not null references public.documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  sequence int not null,
  raw_text text not null,
  char_count int not null,
  created_at timestamp default now()
);

-- RLS: Users see only their own chunks
alter table public.chunks enable row level security;
create policy "Users can read/insert/update/delete own chunks"
  on public.chunks
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Embeddings table (vector search index)
create table if not exists public.embeddings (
  id uuid default gen_random_uuid() primary key,
  chunk_id uuid not null unique references public.chunks(id) on delete cascade,
  document_id uuid not null references public.documents(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  embedding vector(1536),
  created_at timestamp default now()
);

-- RLS: Users see only their own embeddings
alter table public.embeddings enable row level security;
create policy "Users can read/insert/update/delete own embeddings"
  on public.embeddings
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Indexes for vector search
create index if not exists embeddings_user_id_idx on public.embeddings(user_id);
create index if not exists embeddings_document_id_idx on public.embeddings(document_id);
