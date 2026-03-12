# CVSU Case Tracking System

A Django-based case and session management system for the Cavite State University (CVSU) Guidance Office.

## Features

- **User Authentication** - Google OAuth2 integration with @cvsu.edu.ph email validation
- **Student Dashboard** - Track cases, view sessions, and manage appointments
- **Counselor Dashboard** - Manage student cases, schedule sessions, and track progress
- **Session Management** - Create, approve, reschedule, and complete guidance sessions
- **Case Management** - Track case status, assign counselors, and link related sessions
- **Formal Hearing System** - Schedule and manage formal hearings with evidence management
- **Real-time Notifications** - Toast notifications and notification bell for updates
- **Calendar Integration** - View scheduled sessions and hearings in calendar format
- **PDF/Excel Export** - Generate reports and export data

## Tech Stack

- **Backend**: Django 5.2, Python 3.12
- **Database**: PostgreSQL
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **Authentication**: Google OAuth2 via `social-auth-app-django`
- **Email**: Brevo SMTP
- **PDF Generation**: ReportLab

## Installation

1. Clone the repository:
```bash
git clone https://github.com/LaderaJA/casetracking.git
cd casetracking/Capstone
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from the example:
```bash
cp .env.example .env
# Edit .env with your actual configuration values
```

5. Set up the database:
```bash
cd Capstone
python manage.py migrate
python manage.py collectstatic
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

Visit http://localhost:8000 to access the application.

## Configuration

### Required Environment Variables

| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key (generate a new one for production) |
| `DEBUG` | Set to `True` for development, `False` for production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL username |
| `DB_PASSWORD` | PostgreSQL password |
| `DB_HOST` | Database host (default: localhost) |
| `DB_PORT` | Database port (default: 5432) |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` | Google OAuth2 client ID |
| `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` | Google OAuth2 client secret |
| `EMAIL_HOST_USER` | Brevo SMTP username |
| `EMAIL_HOST_PASSWORD` | Brevo SMTP password |
| `DEFAULT_FROM_EMAIL` | Default sender email address |

### Google OAuth2 Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth2 credentials (Web application type)
5. Add authorized redirect URI: `http://localhost:8000/auth/complete/google-oauth2/`
6. Copy Client ID and Client Secret to your `.env` file

## Project Structure

```
Capstone/
├── Capstone/              # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── app/                   # Main application
│   ├── models.py          # Database models
│   ├── views.py           # View logic
│   ├── urls.py            # URL routing
│   ├── templates/app/     # HTML templates
│   └── utils/             # Utility functions
├── static/app/            # Static files (CSS, JS, images)
├── media/                 # Uploaded files
└── manage.py
```

## User Roles

- **Student** - Can view their cases, request sessions, and track progress
- **Counselor** - Can manage all cases, schedule sessions, conduct hearings, and generate reports

## License

This project is proprietary software for Cavite State University.
