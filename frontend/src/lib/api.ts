const API_URL = import.meta.env.VITE_API_URL ?? ''

export interface UserModelSettingsResponse {
  llm_model_name: string
  llm_base_url: string
  llm_api_key_set: boolean
  embedding_model_name: string
  embedding_base_url: string
  embedding_api_key_set: boolean
  embedding_dimensions: number
}

export interface UserModelSettingsUpdate {
  llm_model_name: string
  llm_base_url: string
  llm_api_key?: string
  embedding_model_name: string
  embedding_base_url: string
  embedding_api_key?: string
  embedding_dimensions: number
}

async function authHeaders(): Promise<Record<string, string>> {
  const { getAccessTokenAsync } = await import('./supabase')
  const token = await getAccessTokenAsync()
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

export async function getUserModelSettings(): Promise<UserModelSettingsResponse> {
  const res = await fetch(`${API_URL}/api/settings/model-config`, {
    headers: await authHeaders(),
  })
  if (!res.ok) throw new Error('Failed to fetch user settings')
  return res.json()
}

export async function updateUserModelSettings(body: UserModelSettingsUpdate) {
  const res = await fetch(`${API_URL}/api/settings/model-config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...(await authHeaders()) },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    const payload = await res.json().catch(() => ({}))
    throw new Error(payload.detail ?? 'Failed to save user settings')
  }
  return res.json()
}
