-- Safe to run against both a new database and an existing hosted Supabase project.
-- Fixes sign-ups when an auth.users trigger exists but public.user_profiles
-- was never deployed.

create table if not exists public.user_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text not null,
  state text,
  district text,
  latitude double precision,
  longitude double precision,
  created_at timestamptz not null default now()
);

alter table public.user_profiles add column if not exists email text;
alter table public.user_profiles add column if not exists state text;
alter table public.user_profiles add column if not exists district text;
alter table public.user_profiles add column if not exists latitude double precision;
alter table public.user_profiles add column if not exists longitude double precision;
alter table public.user_profiles add column if not exists created_at timestamptz not null default now();

-- A SECURITY DEFINER trigger can insert a profile even when RLS is enabled.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.user_profiles (id, email, state, district, latitude, longitude)
  values (
    new.id,
    new.email,
    new.raw_user_meta_data ->> 'state',
    new.raw_user_meta_data ->> 'district',
    nullif(new.raw_user_meta_data ->> 'latitude', '')::double precision,
    nullif(new.raw_user_meta_data ->> 'longitude', '')::double precision
  )
  on conflict (id) do update set email = excluded.email;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute procedure public.handle_new_user();

alter table public.user_profiles enable row level security;

drop policy if exists "Users can view their own profile" on public.user_profiles;
create policy "Users can view their own profile"
  on public.user_profiles for select to authenticated
  using ((select auth.uid()) = id);

drop policy if exists "Users can update their own profile" on public.user_profiles;
create policy "Users can update their own profile"
  on public.user_profiles for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- Make PostgREST expose the repaired table immediately.
notify pgrst, 'reload schema';
