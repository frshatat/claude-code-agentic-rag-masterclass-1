const API_URL = import.meta.env.VITE_API_URL ?? ''

async function authHeaders(): Promise<Record<string, string>> {
  const { supabase } = await import('./supabase')
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  return token ? { Authorization: `Bearer ${token}` } : {}
}

export async function getThreads() {
  const res = await fetch(`${API_URL}/api/threads`, {
    headers: await authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to fetch threads')
  return res.json()
}

export async function createThread(title?: string) {
  const res = await fetch(`${API_URL}/api/threads`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(await authHeaders()) },
    body: JSON.stringify({ title: title ?? null }),
  })
  if (!res.ok) throw new Error('Failed to create thread')
  return res.json()
}

export async function getThread(threadId: string) {
  const res = await fetch(`${API_URL}/api/threads/${threadId}`, {
    headers: await authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to fetch thread')
  return res.json()
}

export async function deleteThread(threadId: string) {
  const res = await fetch(`${API_URL}/api/threads/${threadId}`, {
    method: 'DELETE',
    headers: await authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to delete thread')
}

export async function sendMessage(
  threadId: string,
  content: string,
  onToken: (token: string) => void,
): Promise<void> {
  const headers = await authHeaders()
  const res = await fetch(`${API_URL}/api/threads/${threadId}/messages`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...headers },
    body: JSON.stringify({ content }),
  })
  if (!res.ok) throw new Error('Failed to send message')

  const reader = res.body!.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const lines = buffer.split('\n')
    buffer = lines.pop() ?? ''
    for (const line of lines) {
      if (line.startsWith('data: ')) {
        const payload = line.slice(6)
        if (payload === '[DONE]') return
        let parsed: { token?: string; error?: string }
        try {
          parsed = JSON.parse(payload) as { token?: string; error?: string }
        } catch {
          // ignore malformed lines
          continue
        }

        if (parsed.error) {
          throw new Error(parsed.error)
        }
        if (parsed.token) {
          onToken(parsed.token)
        }
      }
    }
  }
}
