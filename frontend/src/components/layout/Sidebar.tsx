import { useEffect, useState } from 'react'
import { Plus, Trash2, MessageSquare, FileText } from 'lucide-react'
import { createThread, deleteThread, getThreads } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { DocumentUpload } from '@/components/chat/DocumentUpload'
import Header from './Header'

interface Thread {
  id: string
  title: string | null
  created_at: string
}

interface Props {
  activeThreadId: string | null
  onSelectThread: (id: string) => void
  onThreadCreated: (id: string) => void
  refreshKey: number
}

export default function Sidebar({
  activeThreadId,
  onSelectThread,
  onThreadCreated,
  refreshKey,
}: Props) {
  const [threads, setThreads] = useState<Thread[]>([])
  const [activeTab, setActiveTab] = useState<'chats' | 'documents'>('chats')
  useEffect(() => {
    getThreads().then(setThreads).catch(console.error)
  }, [refreshKey])

  const handleNew = async () => {
    const thread = await createThread('New chat')
    setThreads((prev) => [thread, ...prev])
    onThreadCreated(thread.id)
  }

  const handleDelete = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation()
    await deleteThread(id)
    setThreads((prev) => prev.filter((t) => t.id !== id))
    if (activeThreadId === id) onSelectThread('')
  }

  return (
    <aside className="w-64 border-r flex flex-col shrink-0 h-full">
      <Header />

      {/* Tab Switcher */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('chats')}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === 'chats'
              ? 'border-b-2 border-primary text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <MessageSquare className="h-4 w-4" /> Chats
        </button>
        <button
          onClick={() => setActiveTab('documents')}
          className={`flex-1 flex items-center justify-center gap-1.5 px-3 py-2 text-sm font-medium transition-colors ${
            activeTab === 'documents'
              ? 'border-b-2 border-primary text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <FileText className="h-4 w-4" /> Documents
        </button>
      </div>

      {activeTab === 'chats' ? (
        <>
          <div className="p-2">
            <Button className="w-full gap-2" variant="outline" onClick={handleNew}>
              <Plus className="h-4 w-4" /> New chat
            </Button>
          </div>
          <nav className="flex-1 overflow-y-auto p-2 space-y-1">
            {threads.map((t) => (
              <div
                key={t.id}
                onClick={() => onSelectThread(t.id)}
                className={`group flex items-center justify-between rounded-md px-3 py-2 text-sm cursor-pointer hover:bg-accent ${activeThreadId === t.id ? 'bg-accent' : ''}`}
              >
                <span className="truncate">{t.title ?? 'Untitled'}</span>
                <Button
                  variant="ghost"
                  size="icon"
                  className="h-6 w-6 opacity-0 group-hover:opacity-100"
                  onClick={(e) => handleDelete(e, t.id)}
                  aria-label="Delete thread"
                >
                  <Trash2 className="h-3 w-3" />
                </Button>
              </div>
            ))}
          </nav>
        </>
      ) : (
        <div className="flex-1 overflow-y-auto px-2 pt-2">
          <DocumentUpload />
        </div>
      )}
    </aside>
  )
}
