import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '@/lib/supabase'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/contexts/useAuth'

type Mode = 'magic' | 'password'

export default function Login() {
  const navigate = useNavigate()
  const { user, loading: authLoading } = useAuth()
  const [mode, setMode] = useState<Mode>('password')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    if (mode === 'password') {
      const { error: err } = await supabase.auth.signInWithPassword({ email, password })
      if (err) {
        setError(err.message)
      } else {
        navigate('/', { replace: true })
      }
    } else {
      const { error: err } = await supabase.auth.signInWithOtp({
        email,
        options: { emailRedirectTo: `${window.location.origin}/auth/callback` },
      })
      if (err) {
        setError(err.message)
      } else {
        setSent(true)
      }
    }

    setLoading(false)
  }

  useEffect(() => {
    if (!authLoading && user) {
      navigate('/', { replace: true })
    }
  }, [authLoading, user, navigate])

  if (sent) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-2">
          <h1 className="text-2xl font-semibold">Check your email</h1>
          <p className="text-muted-foreground">
            We sent a magic link to <strong>{email}</strong>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-full max-w-sm space-y-6 p-6 border rounded-lg shadow-sm">
        <h1 className="text-2xl font-semibold text-center">Sign in</h1>

        <div className="flex rounded-md border overflow-hidden text-sm">
          <button
            type="button"
            onClick={() => { setMode('password'); setError(null) }}
            className={`flex-1 py-2 ${
              mode === 'password' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-accent'
            }`}
          >
            Password
          </button>
          <button
            type="button"
            onClick={() => { setMode('magic'); setError(null) }}
            className={`flex-1 py-2 ${
              mode === 'magic' ? 'bg-primary text-primary-foreground' : 'bg-background hover:bg-accent'
            }`}
          >
            Magic link
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
          {mode === 'password' && (
            <input
              type="password"
              required
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          )}
          {error && <p className="text-sm text-destructive">{error}</p>}
          <Button type="submit" className="w-full" disabled={loading}>
            {loading
              ? mode === 'password' ? 'Signing in…' : 'Sending…'
              : mode === 'password' ? 'Sign in' : 'Send magic link'}
          </Button>
        </form>
      </div>
    </div>
  )
}
