# Hairdrama Task Manager

Production-oriented task management application built for the Hairdrama Tech internship assignment.

## Architecture

```text
Next.js + TypeScript (Vercel)
        |
        | REST + JWT
        v
Flask API (Render/Railway)
        |
        +---- Supabase PostgreSQL
        |
        +---- Google OAuth verification
        |
        +---- Gmail API (task notifications)
```

## Features

- Google OAuth 2.0 login with Gmail accounts
- User profile creation/update from Google identity
- Create tasks
- Assign tasks to registered users
- Dashboard for created and assigned tasks
- Complete assigned tasks
- Email notification when a task is assigned
- Email notification when a task is completed
- Input validation and authorization checks
- Supabase PostgreSQL persistence
- SQL migration included in `/backend/migrations`
- `.env.example` files for frontend/backend
- Production-ready deployment configuration

## Repository structure

```text
backend/
  app/
    __init__.py
    config.py
    db.py
    auth.py
    email_service.py
    routes.py
  migrations/001_initial.sql
  requirements.txt
  run.py
frontend/
  app/
    login/page.tsx
    dashboard/page.tsx
    tasks/new/page.tsx
    tasks/[id]/page.tsx
    layout.tsx
    page.tsx
    globals.css
  components/
  lib/
  types/
  package.json
  next.config.ts
.env.example
```

## Local setup

### 1. Supabase

Create a Supabase project and run `backend/migrations/001_initial.sql` in the SQL editor.

### 2. Google Cloud

Create a Google OAuth 2.0 Web Client ID. Add your frontend origin to Authorized JavaScript origins. The backend verifies the Google ID token using Google's public keys.

For Gmail notifications, create a Google OAuth refresh token for the Gmail account that will send notification emails. The sender account must grant Gmail send permission.

### 3. Backend

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Backend runs on `http://localhost:5000`.

### 4. Frontend

```bash
cd frontend
npm install
copy .env.example .env.local
npm run dev
```

Frontend runs on `http://localhost:3000`.

## Environment variables

See `backend/.env.example` and `frontend/.env.example`. Never commit real credentials.

## Deployment

### Backend

Deploy `/backend` to Render or Railway as a Python web service.

Start command:

```bash
gunicorn run:app
```

Set all backend environment variables in the hosting dashboard.

### Frontend

Deploy `/frontend` to Vercel. Set `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_GOOGLE_CLIENT_ID` in Vercel environment variables.

After deployment, add the Vercel production URL to the Google OAuth client's authorized JavaScript origins.

## Security notes

- Google ID tokens are verified server-side; the email sent by the browser is not trusted.
- Backend API authorization is required for task mutations.
- Task assignees can only complete tasks assigned to them.
- Task creators can view/manage tasks they created.
- Service-role Supabase credentials are backend-only.
- Gmail refresh tokens are backend-only secrets.

## Interview explanation

The frontend is responsible for UI and calling the REST API. Flask owns authentication verification, authorization and business rules. Supabase stores users/tasks. Google provides identity. Gmail API sends transactional notifications after successful database operations.
