
create table if not exists public.landing_settings (
  key text primary key,
  value jsonb not null
);

create table if not exists public.landing_visitors (
  visitor_id text primary key,
  first_seen timestamptz not null default now()
);

create table if not exists public.landing_clicks (
  visitor_id text primary key,
  clicked_at timestamptz not null default now()
);

insert into public.landing_settings (key, value)
values ('main', '{
  "title": "My Telegram Bot",
  "username": "@my_bot",
  "description": "Welcome! Tap below to start.",
  "start_url": "https://t.me/",
  "pfp": "",
  "bg": "#101820",
  "accent": "#229ED9"
}'::jsonb)
on conflict (key) do nothing;
