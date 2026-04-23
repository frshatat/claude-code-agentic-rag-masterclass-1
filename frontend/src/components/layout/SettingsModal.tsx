import { useEffect, useState } from 'react'
import { Button } from '@/components/ui/button'
import {
  getUserModelSettings,
  type UserModelSettingsUpdate,
  updateUserModelSettings,
} from '@/lib/api'

interface SettingsModalProps {
  open: boolean
  onClose: () => void
}

const INITIAL_FORM: UserModelSettingsUpdate = {
  llm_model_name: '',
  llm_base_url: '',
  llm_api_key: '',
  embedding_model_name: '',
  embedding_base_url: '',
  embedding_api_key: '',
  embedding_dimensions: 1536,
}

export default function SettingsModal({ open, onClose }: SettingsModalProps) {
  const [form, setForm] = useState<UserModelSettingsUpdate>(INITIAL_FORM)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [llmKeySet, setLlmKeySet] = useState(false)
  const [embeddingKeySet, setEmbeddingKeySet] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!open) return

    let cancelled = false
    setLoading(true)
    setError('')

    getUserModelSettings()
      .then((settings) => {
        if (cancelled) return
        setForm({
          llm_model_name: settings.llm_model_name,
          llm_base_url: settings.llm_base_url,
          llm_api_key: '',
          embedding_model_name: settings.embedding_model_name,
          embedding_base_url: settings.embedding_base_url,
          embedding_api_key: '',
          embedding_dimensions: settings.embedding_dimensions,
        })
        setLlmKeySet(settings.llm_api_key_set)
        setEmbeddingKeySet(settings.embedding_api_key_set)
      })
      .catch((err: unknown) => {
        if (cancelled) return
        setError(err instanceof Error ? err.message : 'Failed to load settings')
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [open])

  if (!open) return null

  const handleSave = async () => {
    setSaving(true)
    setError('')

    try {
      await updateUserModelSettings(form)
      onClose()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save settings')
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div className="w-full max-w-2xl rounded-xl border bg-background shadow-xl">
        <div className="flex items-center justify-between border-b px-6 py-4">
          <h2 className="text-lg font-semibold">Model Settings</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded px-2 py-1 text-sm text-muted-foreground hover:bg-muted"
            aria-label="Close settings"
          >
            x
          </button>
        </div>

        <div className="max-h-[75vh] space-y-6 overflow-y-auto px-6 py-5">
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading settings...</p>
          ) : (
            <>
              <section className="space-y-3">
                <h3 className="text-base font-semibold">LLM Configuration</h3>

                <label className="block text-sm font-medium">Model Name</label>
                <input
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.llm_model_name}
                  onChange={(e) => setForm((prev) => ({ ...prev, llm_model_name: e.target.value }))}
                  placeholder="e.g. anthropic/claude-3.5-sonnet"
                />

                <label className="block text-sm font-medium">Base URL</label>
                <input
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.llm_base_url}
                  onChange={(e) => setForm((prev) => ({ ...prev, llm_base_url: e.target.value }))}
                  placeholder="e.g. https://openrouter.ai/api/v1"
                />

                <label className="block text-sm font-medium">API Key</label>
                <input
                  type="password"
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.llm_api_key ?? ''}
                  onChange={(e) => setForm((prev) => ({ ...prev, llm_api_key: e.target.value }))}
                  placeholder={llmKeySet ? 'Stored securely. Enter a new key to rotate.' : 'Enter API key'}
                />
              </section>

              <section className="space-y-3 border-t pt-5">
                <h3 className="text-base font-semibold">Embedding Configuration</h3>

                <label className="block text-sm font-medium">Model Name</label>
                <input
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.embedding_model_name}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, embedding_model_name: e.target.value }))
                  }
                  placeholder="e.g. text-embedding-3-small"
                />

                <label className="block text-sm font-medium">Base URL</label>
                <input
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.embedding_base_url}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, embedding_base_url: e.target.value }))
                  }
                  placeholder="e.g. https://api.openai.com/v1"
                />

                <label className="block text-sm font-medium">API Key</label>
                <input
                  type="password"
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.embedding_api_key ?? ''}
                  onChange={(e) =>
                    setForm((prev) => ({ ...prev, embedding_api_key: e.target.value }))
                  }
                  placeholder={
                    embeddingKeySet ? 'Stored securely. Enter a new key to rotate.' : 'Enter API key'
                  }
                />

                <label className="block text-sm font-medium">Dimensions</label>
                <input
                  type="number"
                  min={1}
                  className="w-full rounded-md border bg-background px-3 py-2 text-sm"
                  value={form.embedding_dimensions}
                  onChange={(e) =>
                    setForm((prev) => ({
                      ...prev,
                      embedding_dimensions: Number(e.target.value) || 1536,
                    }))
                  }
                  placeholder="e.g. 1536"
                />
              </section>
            </>
          )}

          {error ? <p className="text-sm text-destructive">{error}</p> : null}
        </div>

        <div className="flex justify-end gap-2 border-t px-6 py-4">
          <Button variant="outline" onClick={onClose} disabled={saving}>
            Cancel
          </Button>
          <Button onClick={handleSave} disabled={saving || loading}>
            {saving ? 'Saving...' : 'Save'}
          </Button>
        </div>
      </div>
    </div>
  )
}
