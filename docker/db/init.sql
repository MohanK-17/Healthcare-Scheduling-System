-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create users table if not exists
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role VARCHAR(20),
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    full_name TEXT,
    password_plain TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Load data from CSV
COPY users(role, username, email, full_name, password_plain)
FROM '/docker-entrypoint-initdb.d/users_data.csv'
DELIMITER ',' CSV HEADER;
