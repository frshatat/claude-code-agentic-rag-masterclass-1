interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
}

interface Props {
  messages: Message[]
  streamingContent: string
}

export default function MessageList({ messages, streamingContent }: Props) {
  return (
    <div className="flex flex-col gap-4">
      {messages.map((m) => (
        <div
          key={m.id}
          className={`flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div
            className={`max-w-[75%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap ${
              m.role === 'user'
                ? 'bg-primary text-primary-foreground'
                : 'bg-muted'
            }`}
          >
            {m.content}
          </div>
        </div>
      ))}
      {streamingContent && (
        <div className="flex justify-start">
          <div className="max-w-[75%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap bg-muted">
            {streamingContent}
            <span className="animate-pulse">▋</span>
          </div>
        </div>
      )}
    </div>
  )
}
