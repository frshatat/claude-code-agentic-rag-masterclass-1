import { useEffect, useRef, useState } from 'react'
import { getThread, sendMessage } from '@/lib/api'
import MessageList from './MessageList'
import MessageInput from './MessageInput'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

export default function ChatWindow({ threadId }: { threadId: string }) {
  const [messages, setMessages] = useState<Message[]>([])
  const [streaming, setStreaming] = useState('')
  const [loading, setLoading] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setMessages([])
    getThread(threadId)
      .then((t) => setMessages(t.messages ?? []))
      .catch(console.error)
  }, [threadId])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streaming])

  const handleSubmit = async (content: string) => {
    const userMsg: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content,
    }
    setMessages((prev) => [...prev, userMsg])
    setLoading(true)
    setStreaming('')

    let fullText = ''
    try {
      await sendMessage(threadId, content, (token) => {
        fullText += token
        setStreaming(fullText)
      })
      setMessages((prev) => [
        ...prev,
        { id: crypto.randomUUID(), role: 'assistant', content: fullText },
      ])
    } catch (err) {
      console.error(err)
    } finally {
      setStreaming('')
      setLoading(false)
    }
  }

  return (
    <div className="h-full flex flex-col">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && !streaming ? (
          <div className="h-full flex items-center justify-center text-muted-foreground text-sm">
            Send a message to start the conversation.
          </div>
        ) : (
          <MessageList messages={messages} streamingContent={streaming} />
        )}
        <div ref={bottomRef} />
      </div>
      <div className="border-t p-4">
        <MessageInput onSubmit={handleSubmit} disabled={loading} />
      </div>
    </div>
  )
}
