create extension if not exists pgcrypto;

create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  google_id text unique not null,
  email text unique not null,
  name text not null,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.tasks (
  id uuid primary key default gen_random_uuid(),
  title text not null check (char_length(trim(title)) between 1 and 120),
  description text not null default '',
  created_by uuid not null references public.users(id) on delete cascade,
  assigned_to uuid not null references public.users(id) on delete restrict,
  status text not null default 'pending' check (status in ('pending','completed')),
  created_at timestamptz not null default now(),
  completed_at timestamptz
);

create index if not exists idx_tasks_created_by on public.tasks(created_by);
create index if not exists idx_tasks_assigned_to on public.tasks(assigned_to);
create index if not exists idx_tasks_status on public.tasks(status);

alter table public.users enable row level security;
alter table public.tasks enable row level security;

-- The backend uses the Supabase service role key and owns authorization.
-- No public client-side database access is required.
