-- Give users created before the profile trigger a profile row as well.
insert into public.user_profiles (id, email)
select users.id, users.email
from auth.users as users
where users.email is not null
  and not exists (
    select 1
    from public.user_profiles as profiles
    where profiles.id = users.id
  );

notify pgrst, 'reload schema';
