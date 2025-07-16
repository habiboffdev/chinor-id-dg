-- Grant all privileges to opportuni_user
GRANT ALL PRIVILEGES ON DATABASE opportuni_db TO opportuni_user;

-- Grant schema privileges
GRANT ALL ON SCHEMA public TO opportuni_user;

-- Grant usage and create privileges on public schema
GRANT USAGE, CREATE ON SCHEMA public TO opportuni_user;

-- Grant privileges on all tables in public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO opportuni_user;

-- Grant privileges on all sequences in public schema
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO opportuni_user;

-- Grant privileges on all functions in public schema
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO opportuni_user;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO opportuni_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO opportuni_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO opportuni_user;

-- Alternative: Make opportuni_user a superuser (for development only)
-- ALTER USER opportuni_user WITH SUPERUSER;

\q
