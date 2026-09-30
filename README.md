# Study Portal — Python (Flask) version

A single Flask web app covering everything you described: study material,
courses, resume builder, and an opportunities board — all behind one login,
reachable from one dashboard. Uses SQLite, so there's nothing extra to
install or configure to get it running.

## Features included

| Module | What it does |
|---|---|
| **Auth** | Sign up, log in, log out (session-based, password hashing) |
| **Study material** | Upload files (PDF/DOC/PPT/TXT/ZIP), browse and filter by subject, download |
| **Courses** | Create courses with a description and a list of modules, enroll, track your own progress (%) |
| **Resume builder** | Fill in a form (education, skills, projects, experience) and download a generated PDF resume |
| **Opportunities board** | Post internships/jobs/hackathons, filter by type, bookmark ones you're interested in |

## Folder structure

```
study-portal-py/
├── app/
│   ├── __init__.py          app factory
│   ├── models.py            all database models
│   ├── main_routes.py       dashboard route
│   ├── auth/routes.py
│   ├── materials/routes.py
│   ├── courses/routes.py
│   ├── resume/routes.py
│   ├── opportunities/routes.py
│   ├── templates/           Jinja2 HTML templates
│   └── static/css/style.css
├── uploads/                 uploaded study material files (created automatically)
├── config.py
├── run.py                   entry point
├── requirements.txt
└── .env.example
```

## Prerequisites

- [Python](https://www.python.org/downloads/) 3.10 or newer, with `pip`
- No separate database install needed — it uses a local SQLite file
  (`study_portal.db`), created automatically the first time you run it

## How to run

```bash
cd study-portal-py

# 1. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
```

Open `.env` and set `SECRET_KEY` to any long random string (you can generate
one with `python3 -c "import secrets; print(secrets.token_hex(32))"`).

```bash
# 4. Run the app
python run.py
```

You should see something like `Running on http://127.0.0.1:5000`. Open
that URL in your browser, click "Sign up", create an account, and you'll
land on the dashboard with all four modules one click away.

## Notes on how each module works

- **Study material**: uploaded files are saved in the `uploads/` folder on
  disk (not in the database) with a unique filename; the database just
  stores the metadata and filename.
- **Courses**: modules are stored as plain text, one module per line, and
  split into a list when displayed — no need for a separate table unless
  you want per-module completion tracking later.
- **Resume builder**: each user has one resume record; saving the form
  updates it. The **Download PDF** button (visible once you've saved once)
  generates a PDF on the fly using `reportlab` — no external tools like
  wkhtmltopdf required.
- **Opportunities**: anyone logged in can post one; bookmarking is
  per-user, stored in a separate `Bookmark` table.

## What you could extend next

- Restrict "add course" / "post opportunity" to admin-role users only
  (the `User.role` field already supports `"admin"` vs `"student"`)
- Add a search box across study material titles/tags, not just subject
- Add resume templates (multiple PDF layouts to choose from)
- Swap SQLite for PostgreSQL/MySQL for deployment (just change
  `DATABASE_URL` in `.env` — SQLAlchemy handles the rest)

## Common issues

- **`ModuleNotFoundError`** — make sure your virtual environment is
  activated and `pip install -r requirements.txt` completed without errors.
- **Upload fails silently** — check the file extension is in
  `ALLOWED_EXTENSIONS` in `config.py`; add more extensions there if needed.
- **PDF download shows a 500 error** — make sure you've saved the resume
  form at least once before clicking "Download PDF".
- **Changes to `SECRET_KEY` log everyone out** — this invalidates existing
  sessions, which is expected.
