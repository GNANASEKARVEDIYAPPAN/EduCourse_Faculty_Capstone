# EduCourse – Integrated Course Design & Automation System

Independent faculty-oriented Flask capstone project, based on the ten sections of the supplied FDP report. Not a copy of the earlier SmartCourse application.

## Run

```bash
python -m pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000 and sign in with the **demonstration-only** account `faculty` / `Faculty@123`. Change the password and SECRET_KEY before any real use. SQLite database is created automatically on first start. To create another faculty account, use the Python snippet below from this folder:

```python
from app import init,conn
from werkzeug.security import generate_password_hash
init()
with conn() as c:
    c.execute('INSERT INTO users(username,password,role) VALUES(?,?,?)',('faculty2',generate_password_hash('ChangeMe123!'),'faculty'))
```

## Features

- Login, logout, per-faculty subject and record isolation; horizontal navigation and ten dashboard links.
- Multi-subject record entry for each of the ten FDP deliverables, deletion and JSON export.
- Part 8 local keyword retrieval assistant using saved records (not a live AI model).
- Optional PHP JSON-export reader: export a course from Flask, save it as `php/sample_export.json`, and run `php -S localhost:8000 -t php`; open `http://localhost:8000/course_export.php`.

## Ten parts

1. Course Planning; 2. Course Website; 3. Experiential Learning; 4. Interactive Learning Resource; 5. Assessment Design; 6. Continuous Assessment Automation; 7. Outcome-Based Analysis; 8. AI Agent for Course Management; 9. Research Integration; 10. Responsible AI Use.

## Scope and limitations

This is a working **starter implementation**: each part is connected to persistent subject-specific deliverable records, but specialized course-site generation, quizzes, assessment engines, official CO attainment, external AI APIs, Google integrations, and scholarly search are **not implemented**. PHP runs as an optional separate service, not inside Flask. Use synthetic demonstration records only. Before production, add CSRF protection, account administration, HTTPS, secure secret configuration, backup, audit logs, stricter validation, and institution-approved OBE rules. Do not expose the default account publicly.
