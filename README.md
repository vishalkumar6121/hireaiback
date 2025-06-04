# Talent AI Matchmaker Backend

This is the backend service for the Talent AI Matchmaker application, built with FastAPI and Supabase.

## Setup

1. Create a virtual environment and install dependencies:
```bash
chmod +x setup.sh
./setup.sh
```

2. Create a `.env` file in the root directory with the following variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
JWT_SECRET=your_jwt_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

3. Set up your Supabase database with the following tables:

```sql
-- Users table
create table users (
    id uuid default uuid_generate_v4() primary key,
    email text unique not null,
    full_name text not null,
    role text not null,
    hashed_password text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Candidates table
create table candidates (
    id uuid default uuid_generate_v4() primary key,
    full_name text not null,
    email text unique not null,
    phone text,
    location text,
    skills text[] default '{}',
    experience_years integer,
    current_role text,
    desired_role text,
    resume_url text,
    score float,
    status text default 'active',
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Outreach templates table
create table outreach_templates (
    id uuid default uuid_generate_v4() primary key,
    name text not null,
    subject text not null,
    body text not null,
    category text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null,
    updated_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Outreach messages table
create table outreach_messages (
    id uuid default uuid_generate_v4() primary key,
    template_id uuid references outreach_templates(id),
    candidate_id uuid references candidates(id),
    subject text,
    body text,
    status text default 'pending',
    sent_at timestamp with time zone,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);
```

4. Create a storage bucket in Supabase:
- Create a bucket named "resumes" for storing candidate resumes
- Set the bucket's privacy settings according to your needs

## Running the Application

To run the application in development mode:

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the application is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- GET `/api/health` - Check API health status

### Authentication
- POST `/api/auth/login` - User login
- POST `/api/auth/signup` - User registration
- POST `/api/auth/logout` - User logout

### Candidates
- GET `/api/candidates/search` - Search candidates
- GET `/api/candidates/leaderboard` - Get leaderboard data
- POST `/api/candidates/{candidate_id}/background-check` - Run background check

### Resumes
- POST `/api/resumes/upload` - Upload resume (supports PDF and DOCX)

### Analytics
- GET `/api/analytics` - Get analytics data

### Outreach
- GET `/api/outreach/templates` - Get outreach templates
- POST `/api/outreach/send` - Send outreach message 