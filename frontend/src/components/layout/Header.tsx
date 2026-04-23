import { useState } from 'react'
import { useAuth } from '@/contexts/useAuth'
import { Button } from '@/components/ui/button'
import { LogOut, Settings } from 'lucide-react'
import SettingsModal from '@/components/layout/SettingsModal'

export default function Header() {
  const { user, signOut } = useAuth()
  const [settingsOpen, setSettingsOpen] = useState(false)

  return (
    <>
      <header className="h-12 border-b flex items-center justify-between px-4 shrink-0">
        <span className="font-semibold text-sm">RAG Chat</span>
        <div className="flex items-center gap-3">
          <span className="text-xs text-muted-foreground">{user?.email}</span>
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSettingsOpen(true)}
            aria-label="Open settings"
          >
            <Settings className="h-4 w-4" />
          </Button>
          <Button variant="ghost" size="icon" onClick={signOut} aria-label="Sign out">
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </header>
      <SettingsModal open={settingsOpen} onClose={() => setSettingsOpen(false)} />
    </>
  )
}
