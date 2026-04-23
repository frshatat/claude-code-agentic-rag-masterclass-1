create table if not exists public.user_model_settings (
  user_id uuid primary key references auth.users(id) on delete cascade,
  llm_model_name text not null default '',
  llm_base_url text not null default '',
  llm_api_key_encrypted text,
  embedding_model_name text not null default '',
  embedding_base_url text not null default '',
  embedding_api_key_encrypted text,
  embedding_dimensions integer not null default 1536 check (embedding_dimensions > 0),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

alter table public.user_model_settings enable row level security;

create policy "Users can read own model settings"
  on public.user_model_settings
  for select
  using (auth.uid() = user_id);

create policy "Users can insert own model settings"
  on public.user_model_settings
  for insert
  with check (auth.uid() = user_id);

create policy "Users can update own model settings"
  on public.user_model_settings
  for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "Users can delete own model settings"
  on public.user_model_settings
  for delete
  using (auth.uid() = user_id);

create or replace function public.set_user_model_settings_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists trg_user_model_settings_updated_at on public.user_model_settings;
create trigger trg_user_model_settings_updated_at
before update on public.user_model_settings
for each row
execute function public.set_user_model_settings_updated_at();
