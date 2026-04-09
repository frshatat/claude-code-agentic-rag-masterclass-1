#!/usr/bin/env python3
"""
Initialize ingestion schema (documents, chunks, embeddings tables).
Run this script once to set up the schema if supabase CLI is not available.
"""

import os
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.config import settings
from supabase import create_client

def init_schema():
    """Create ingestion schema tables in Supabase."""
    supabase = create_client(settings.supabase_url, settings.supabase_service_role_key)
    
    # These SQL statements create the necessary tables and RLS policies
    sql_statements = [
        # Enable pgvector
        "create extension if not exists vector;",
        
        # Documents table
        """
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
        """,
        
        # Documents RLS
        "alter table public.documents enable row level security;",
        """
        create policy if not exists "Users can read/insert/update/delete own documents"
          on public.documents
          for all
          using (auth.uid() = user_id)
          with check (auth.uid() = user_id);
        """,
        
        # Chunks table
        """
        create table if not exists public.chunks (
          id uuid default gen_random_uuid() primary key,
          document_id uuid not null references public.documents(id) on delete cascade,
          user_id uuid not null references auth.users(id) on delete cascade,
          sequence int not null,
          raw_text text not null,
          char_count int not null,
          created_at timestamp default now()
        );
        """,
        
        # Chunks RLS
        "alter table public.chunks enable row level security;",
        """
        create policy if not exists "Users can read/insert/update/delete own chunks"
          on public.chunks
          for all
          using (auth.uid() = user_id)
          with check (auth.uid() = user_id);
        """,
        
        # Embeddings table
        """
        create table if not exists public.embeddings (
          id uuid default gen_random_uuid() primary key,
          chunk_id uuid not null unique references public.chunks(id) on delete cascade,
          document_id uuid not null references public.documents(id) on delete cascade,
          user_id uuid not null references auth.users(id) on delete cascade,
          embedding vector(1536),
          created_at timestamp default now()
        );
        """,
        
        # Embeddings RLS
        "alter table public.embeddings enable row level security;",
        """
        create policy if not exists "Users can read/insert/update/delete own embeddings"
          on public.embeddings
          for all
          using (auth.uid() = user_id)
          with check (auth.uid() = user_id);
        """,
        
        # Indexes
        "create index if not exists embeddings_user_id_idx on public.embeddings(user_id);",
        "create index if not exists embeddings_document_id_idx on public.embeddings(document_id);",
    ]
    
    try:
        for sql in sql_statements:
            if sql.strip():
                supabase.postgrest.rpc("exec_sql", {"sql": sql}).execute()
        print("✅ Ingestion schema initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing schema: {e}")
        return False

if __name__ == "__main__":
    init_schema()
