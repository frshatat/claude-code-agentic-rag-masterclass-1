"""Database schema initialization and migrations."""

from app.config import settings
from supabase import create_client
import logging

logger = logging.getLogger(__name__)

# Initialize Supabase admin client
_admin_client = None


def get_admin_client():
    """Get Supabase admin client with service role key."""
    global _admin_client
    if _admin_client is None:
        _admin_client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _admin_client


async def init_schema():
    """Initialize database schema if not already exists."""
    admin = get_admin_client()
    
    # SQL statements to create schema
    sql_statements = [
        # Enable pgvector extension
        "CREATE EXTENSION IF NOT EXISTS vector;",
        
        # Documents table
        """
        CREATE TABLE IF NOT EXISTS public.documents (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
          file_name text NOT NULL,
          file_size_bytes bigint NOT NULL,
          content_hash text NOT NULL UNIQUE,
          status text CHECK (status IN ('uploading', 'processing', 'complete', 'error')) DEFAULT 'uploading',
          error_message text,
          created_at timestamp DEFAULT now(),
          updated_at timestamp DEFAULT now()
        );
        """,
        
        # Documents RLS
        "ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;",
        """
        CREATE POLICY IF NOT EXISTS "Users can read/insert/update/delete own documents"
          ON public.documents
          FOR ALL
          USING (auth.uid() = user_id)
          WITH CHECK (auth.uid() = user_id);
        """,
        
        # Chunks table
        """
        CREATE TABLE IF NOT EXISTS public.chunks (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
          user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
          sequence int NOT NULL,
          raw_text text NOT NULL,
          char_count int NOT NULL,
          created_at timestamp DEFAULT now()
        );
        """,
        
        # Chunks RLS
        "ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;",
        """
        CREATE POLICY IF NOT EXISTS "Users can read/insert/update/delete own chunks"
          ON public.chunks
          FOR ALL
          USING (auth.uid() = user_id)
          WITH CHECK (auth.uid() = user_id);
        """,
        
        # Embeddings table
        """
        CREATE TABLE IF NOT EXISTS public.embeddings (
          id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
          chunk_id uuid NOT NULL UNIQUE REFERENCES public.chunks(id) ON DELETE CASCADE,
          document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
          user_id uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
          embedding vector(1536),
          created_at timestamp DEFAULT now()
        );
        """,
        
        # Embeddings RLS
        "ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;",
        """
        CREATE POLICY IF NOT EXISTS "Users can read/insert/update/delete own embeddings"
          ON public.embeddings
          FOR ALL
          USING (auth.uid() = user_id)
          WITH CHECK (auth.uid() = user_id);
        """,
        
        # Indexes
        "CREATE INDEX IF NOT EXISTS embeddings_user_id_idx ON public.embeddings(user_id);",
        "CREATE INDEX IF NOT EXISTS embeddings_document_id_idx ON public.embeddings(document_id);",
    ]
    
    logger.info("Initializing database schema...")
    
    # Try to check if documents table exists first
    try:
        admin.table('documents').select('*').limit(1).execute()
        logger.info("✅ Database schema already initialized")
        return True
    except Exception as check_error:
        if 'Could not find the table' not in str(check_error):
            logger.warning(f"⚠️ Got unexpected error checking for tables: {check_error}")
        logger.info("📝 Tables not found, attempting to create schema...")
    
    # Try to execute each SQL statement
    # Note: The Supabase Python SDK doesn't support arbitrary SQL execution
    # We document this limitation and suggest using supabase db push or the SQL editor
    logger.warning(
        "⚠️ Cannot auto-create schema - Supabase Python SDK doesn't support arbitrary SQL.\n"
        "Please run one of the following:\n"
        "  Option 1: supabase db push (requires Supabase CLI)\n"
        "  Option 2: Execute manually via Supabase dashboard SQL editor:\n"
        "    https://app.supabase.com/project/jfkijgjwytnivlthppcr/sql/new\n"
        "  Option 3: Use the schema migration file:\n"
        "    supabase/migrations/003_create_ingestion_schema.sql"
    )
    
    return False
