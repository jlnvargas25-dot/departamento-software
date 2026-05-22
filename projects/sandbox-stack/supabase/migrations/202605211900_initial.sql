-- =============================================================
-- Migration: 202605211900_initial.sql
-- Feature: 001-todo-management
-- Rules: A5 (RLS multi-tenant), A6 (audit immutability),
--        A13 (optimistic concurrency), A24 (soft-delete lifecycle),
--        A25 (owner-only authz via auth.uid())
-- MANUAL STEP: apply with `supabase db push` after `supabase start`
-- =============================================================

-- -------------------------------------------------------
-- 1. todos table
-- -------------------------------------------------------
create table if not exists public.todos (
  id           uuid        primary key default gen_random_uuid(),
  user_id      uuid        not null references auth.users(id) on delete cascade,
  text         text        not null check (char_length(text) between 1 and 1000),
  completed_at timestamptz null,                 -- null = active; set = completed (A8 idempotent)
  created_at   timestamptz not null default now(), -- A6 audit
  updated_at   timestamptz not null default now(), -- A13 optimistic concurrency token
  deleted_at   timestamptz null                  -- null = active; set = soft-deleted (A24)
);

comment on table public.todos is 'Per-user todo items. RLS enforces strict tenant isolation (A5).';
comment on column public.todos.user_id is 'Owner. auth.uid() must match on every DML (A5, A25).';
comment on column public.todos.deleted_at is 'Soft-delete marker. Cron purges rows >30 days old (A24).';
comment on column public.todos.updated_at is 'Optimistic concurrency token. Always updated by trigger (A13).';

-- Partial index: covers listActive query (FR-011)
create index if not exists idx_todos_user_active
  on public.todos (user_id, created_at desc)
  where deleted_at is null;

-- Index for purge cron job (A24)
create index if not exists idx_todos_user_deleted
  on public.todos (user_id, deleted_at)
  where deleted_at is not null;

-- Trigger: keep updated_at current on every update (A13)
create or replace function public.set_updated_at()
returns trigger
language plpgsql
volatile  -- VOLATILE: reads/writes DB state (now()); cannot be inlined or cached (A13)
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create or replace trigger todos_set_updated_at
  before update on public.todos
  for each row
  execute function public.set_updated_at();

-- -------------------------------------------------------
-- 2. RLS on todos (A5 CRITICA + A25)
-- -------------------------------------------------------
alter table public.todos enable row level security;

-- SELECT: owner only
create policy "todos_select_own"
  on public.todos for select
  using (auth.uid() = user_id);

-- INSERT: owner must match session user (double-enforced with app layer)
create policy "todos_insert_own"
  on public.todos for insert
  with check (auth.uid() = user_id);

-- UPDATE: owner only on both the existing row and the new values
create policy "todos_update_own"
  on public.todos for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- DELETE (hard): owner only; used by cascade on account deletion
create policy "todos_delete_own"
  on public.todos for delete
  using (auth.uid() = user_id);

-- -------------------------------------------------------
-- 3. todo_events — append-only audit log (A6)
-- -------------------------------------------------------
create table if not exists public.todo_events (
  id            bigint      primary key generated always as identity,
  actor_user_id uuid        not null references auth.users(id) on delete cascade,
  todo_id       uuid        not null,  -- no FK: todo may be hard-deleted later
  kind          text        not null
                            check (kind in ('create','update','complete','uncomplete','delete')),
  occurred_at   timestamptz not null default now(),
  payload       jsonb       null       -- optional redacted snapshot
);

comment on table public.todo_events is 'Append-only audit trail for todo mutations (A6).';

create index if not exists idx_events_actor_time
  on public.todo_events (actor_user_id, occurred_at desc);

alter table public.todo_events enable row level security;

-- INSERT: actor must be the authenticated user (A5 + A25)
create policy "events_insert_self"
  on public.todo_events for insert
  with check (auth.uid() = actor_user_id);

-- SELECT: owner sees their own audit trail
create policy "events_select_own"
  on public.todo_events for select
  using (auth.uid() = actor_user_id);

-- No UPDATE / DELETE policies => denied by default (A6 immutability enforced at DB)

-- -------------------------------------------------------
-- 4. auth_events — auth audit log (A6 + A21)
-- -------------------------------------------------------
create table if not exists public.auth_events (
  id            bigint      primary key generated always as identity,
  actor_user_id uuid        null references auth.users(id) on delete set null,
  kind          text        not null
                            check (kind in (
                              'signup','signin_success','signin_fail',
                              'magic_link_sent','magic_link_redeemed',
                              'signout','session_expired'
                            )),
  outcome       text        not null,  -- 'ok' or short failure reason (never raw input)
  occurred_at   timestamptz not null default now(),
  ip_hash       text        null       -- hashed IP for abuse correlation; no raw PII (A22)
);

comment on table public.auth_events is 'Append-only auth audit. Inserts via service-role server only (A22).';

create index if not exists idx_auth_events_actor
  on public.auth_events (actor_user_id, occurred_at desc);

create index if not exists idx_auth_events_ip_recent
  on public.auth_events (ip_hash, occurred_at desc);

alter table public.auth_events enable row level security;

-- SELECT: owner sees their own auth history
create policy "auth_events_select_own"
  on public.auth_events for select
  using (auth.uid() = actor_user_id);

-- No INSERT policy for anon/authenticated: inserts done via service-role only (A22)
-- Service-role bypasses RLS by design; this is intentional and documented.
