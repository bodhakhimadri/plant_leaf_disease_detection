-- Reports are written by the signed-in user and are read by authenticated
-- community members for district-level disease alerts.
alter table public.disease_reports enable row level security;

drop policy if exists "Authenticated users can read disease reports" on public.disease_reports;
create policy "Authenticated users can read disease reports"
  on public.disease_reports for select to authenticated
  using (true);

drop policy if exists "Users can create their own disease reports" on public.disease_reports;
create policy "Users can create their own disease reports"
  on public.disease_reports for insert to authenticated
  with check ((select auth.uid()) = user_id);
