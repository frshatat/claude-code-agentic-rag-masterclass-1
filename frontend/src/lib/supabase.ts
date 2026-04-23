import { createClient } from '@supabase/supabase-js'

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL as string
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY as string

export const supabase = createClient(supabaseUrl, supabaseAnonKey)

// Keep a fresh access token updated via auth state changes.
// onAuthStateChange fires with the initial session before getSession() resolves,
// and auto-fires TOKEN_REFRESHED events, so this stays current.
let _accessToken: string | null = null

supabase.auth.onAuthStateChange((_event, session) => {
  _accessToken = session?.access_token ?? null
})

void supabase.auth.getSession().then(({ data }) => {
  _accessToken = data.session?.access_token ?? null
})

export function getAccessToken(): string | null {
  return _accessToken
}

export async function getAccessTokenAsync(): Promise<string | null> {
  if (_accessToken) return _accessToken
  const { data } = await supabase.auth.getSession()
  _accessToken = data.session?.access_token ?? null
  return _accessToken
}
