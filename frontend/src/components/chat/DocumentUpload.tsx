import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/contexts/useAuth';
import { Button } from '@/components/ui/button';
import { getAccessToken } from '@/lib/supabase';
import { AlertCircle, CheckCircle, UploadCloud, Trash2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL ?? '';

interface Document {
  id: string;
  file_name: string;
  file_size_bytes: number;
  status: 'uploading' | 'processing' | 'complete' | 'error';
  error_message?: string;
  created_at: string;
}

function authHeaders(): HeadersInit | undefined {
  const token = getAccessToken();
  return token ? { Authorization: `Bearer ${token}` } : undefined;
}

export function DocumentUpload() {
  const { user } = useAuth();
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Load documents on mount
  useEffect(() => {
    loadDocuments();
  }, [user]);

  const loadDocuments = async () => {
    if (!user) return;
    
    setLoadingDocs(true);
    try {
      const headers = authHeaders();
      const response = await fetch(`${API_URL}/api/documents`, { headers });
      if (response.ok) {
        const data = await response.json();
        setDocuments(data || []);
      }
    } catch (error: any) {
      console.error('Failed to load documents:', error);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validations
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('File too large (max 10MB)');
      return;
    }

    const allowedTypes = ['application/pdf', 'text/plain', 'text/markdown'];
    if (!allowedTypes.includes(file.type)) {
      setUploadError('Unsupported file type. Use PDF, TXT, or MD.');
      return;
    }

    setUploading(true);
    setUploadError('');

    try {
      const formData = new FormData();
      formData.append('file', file);

      const headers = authHeaders();
      const response = await fetch(`${API_URL}/api/documents`, {
        method: 'POST',
        headers,
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Upload failed');
      }

      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }

      // Reload to get fresh list
      setTimeout(() => loadDocuments(), 500);
    } catch (error: any) {
      setUploadError(error.message || 'Upload failed');
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      const headers = authHeaders();
      const response = await fetch(`${API_URL}/api/documents/${docId}`, {
        method: 'DELETE',
        headers,
      });
      
      if (response.ok) {
        setDocuments(documents.filter(doc => doc.id !== docId));
      } else {
        throw new Error('Failed to delete');
      }
    } catch (error: any) {
      setUploadError(error.message || 'Failed to delete');
    }
  };

  return (
    <div className="p-4 m-4 bg-slate-50 border border-slate-200 rounded-lg space-y-4">
      <div className="space-y-2">
        <h3 className="font-semibold text-sm text-slate-900">📄 Documents</h3>
          
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.txt,.md"
            onChange={handleFileSelect}
            disabled={uploading}
            hidden
          />
          
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading || !user}
            variant="outline"
            className="w-full h-9 text-xs"
            size="sm"
          >
            {uploading ? (
              <>
                <span className="animate-spin mr-1">⏳</span>
                Uploading...
              </>
            ) : (
              <>
                <UploadCloud className="w-3 h-3 mr-1" />
                Upload File
              </>
            )}
          </Button>

          {uploadError && (
            <div className="flex gap-2 items-start text-xs text-red-600 bg-red-50 p-2 rounded">
              <AlertCircle className="w-3 h-3 mt-0.5 flex-shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Documents List */}
        {documents.length > 0 && (
          <div className="space-y-2 border-t pt-3 max-h-40 overflow-y-auto">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="flex items-center justify-between text-xs bg-white p-2 rounded border border-slate-200 hover:bg-slate-50"
              >
                <div className="flex items-center gap-2 flex-1 min-w-0">
                  {doc.status === 'complete' && (
                    <CheckCircle className="w-3 h-3 text-green-600 flex-shrink-0" />
                  )}
                  {doc.status === 'processing' && (
                    <span className="animate-spin w-3 h-3 text-blue-600">⏳</span>
                  )}
                  {doc.status === 'error' && (
                    <AlertCircle className="w-3 h-3 text-red-600 flex-shrink-0" />
                  )}
                  
                  <div className="min-w-0 flex-1">
                    <p className="truncate font-medium text-slate-700">
                      {doc.file_name}
                    </p>
                    <p className="text-xs text-slate-500">
                      {(doc.file_size_bytes / 1024).toFixed(1)}KB
                    </p>
                    {doc.error_message && (
                      <p className="text-xs text-red-600 truncate">
                        {doc.error_message}
                      </p>
                    )}
                  </div>
                </div>
                
                <button
                  onClick={() => handleDelete(doc.id)}
                  className="ml-2 p-1 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded flex-shrink-0"
                  title="Delete"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        )}

        {!loadingDocs && documents.length === 0 && (
          <p className="text-xs text-slate-500 text-center py-3">
            No documents yet. Upload one to get started.
          </p>
        )}
    </div>
  );
}
