import hashlib
import logging
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File

from app.auth.dependencies import get_current_user
from app.db.supabase import get_supabase_for_token

router = APIRouter(prefix="/documents")
logger = logging.getLogger(__name__)

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_TYPES = {"application/pdf", "text/plain", "text/markdown"}


async def compute_file_hash(content: bytes) -> str:
    """Compute SHA256 hash of file content."""
    return hashlib.sha256(content).hexdigest()


@router.post("")
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
):
    """Upload a document for ingestion."""
    
    # Validate file
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 10MB)")
    
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Use PDF, TXT, or MD.",
        )
    
    # Read file
    try:
        content = await file.read()
    except Exception as e:
        logger.exception("Failed to read uploaded file")
        raise HTTPException(status_code=400, detail="Failed to read file")
    
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check for duplicates
    supabase = get_supabase_for_token(user["access_token"])
    
    try:
        existing = supabase.table("documents").select("*").eq(
            "content_hash", file_hash
        ).execute()
        
        if existing.data:
            raise HTTPException(
                status_code=409,
                detail="Document already uploaded",
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error checking for duplicate documents")
        # Continue anyway - table might not exist yet
    
    # Create document record
    doc_id = str(uuid4())
    doc_record = {
        "id": doc_id,
        "user_id": user["id"],
        "file_name": file.filename or "document",
        "file_size_bytes": len(content),
        "content_hash": file_hash,
        "status": "uploading",
    }
    
    try:
        # Insert DB record
        response = supabase.table("documents").insert(doc_record).execute()
        
        # Upload to Supabase Storage
        storage_path = f"{user['id']}/{doc_id}/{file.filename}"
        supabase.storage.from_("user-documents").upload(
            path=storage_path,
            file=content,
            file_options={"content-type": file.content_type},
        )
        
        # Mark as uploaded (chunking happens async in Phase 7)
        supabase.table("documents").update(
            {"status": "processing"}
        ).eq("id", doc_id).execute()
        
        logger.info(f"Document uploaded: {doc_id} by user {user['id']}")
        
        return {
            "document_id": doc_id,
            "file_name": file.filename,
            "file_size": len(content),
            "status": "processing",
            "message": "File uploaded. Processing started.",
        }
    
    except Exception as e:
        logger.exception(f"Error uploading document: {e}")
        
        # Mark as error
        try:
            supabase.table("documents").update({
                "status": "error",
                "error_message": str(e),
            }).eq("id", doc_id).execute()
        except Exception:
            pass  # Table might not exist
        
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}",
        )


@router.get("")
async def list_documents(user: dict = Depends(get_current_user)):
    """List user's uploaded documents."""
    supabase = get_supabase_for_token(user["access_token"])
    
    try:
        response = supabase.table("documents").select("*").order(
            "created_at", desc=True
        ).execute()
        return response.data
    except Exception as e:
        logger.exception("Error listing documents")
        return []  # Return empty list if table doesn't exist


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: dict = Depends(get_current_user),
):
    """Delete a document."""
    supabase = get_supabase_for_token(user["access_token"])
    
    try:
        # Verify ownership via RLS
        doc = supabase.table("documents").select("*").eq(
            "id", document_id
        ).execute()
        
        if not doc.data:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Delete from DB (cascades to chunks, embeddings)
        supabase.table("documents").delete().eq(
            "id", document_id
        ).execute()
        
        logger.info(f"Document deleted: {document_id}")
        
        return {"status": "deleted"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error deleting document: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete document")
