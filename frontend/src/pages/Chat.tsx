import { useState } from 'react'
import Sidebar from '@/components/layout/Sidebar'
import ChatWindow from '@/components/chat/ChatWindow'

export default function Chat() {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  const handleThreadCreated = (id: string) => {
    setActiveThreadId(id)
    setRefreshKey((k) => k + 1)
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        activeThreadId={activeThreadId}
        onSelectThread={setActiveThreadId}
        onThreadCreated={handleThreadCreated}
        refreshKey={refreshKey}
      />
      <main className="flex-1 overflow-hidden">
        {activeThreadId ? (
          <ChatWindow threadId={activeThreadId} />
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            Select or create a conversation to get started.
          </div>
        )}
      </main>
    </div>
  )
}
