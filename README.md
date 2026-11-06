# CodeArena

**A coding practice and live contest platform built with Django.**

CodeArena lets players solve programming problems, submit Python solutions for automatic judging, and compete in timed coding contests. Hosts can manage problems and test cases, run contest rooms, and review results from a leaderboard.

> **Project status:** Academic/demo project. The code runner uses a subprocess, a time limit, and an output limit, but it is **not a security sandbox**. Do not deploy it publicly or run untrusted submissions on a machine with sensitive data.

## Table of contents

- [Features](#features)
- [User roles](#user-roles)
- [How a contest works](#how-a-contest-works)
- [Technology stack](#technology-stack)
- [Project structure](#project-structure)
- [Getting started](#getting-started)
- [Demo data](#demo-data)
- [Running tests](#running-tests)
- [Screenshots to add](#screenshots-to-add)
- [Limitations and security note](#limitations-and-security-note)
- [Contributing](#contributing)

## Features

- Account registration, login, and role-based permissions.
- Problem catalog with difficulty, points, descriptions, and sample test cases.
- Host tools to create and manage problems and their test cases.
- Hidden test cases that are used for judging but are not shown to players.
- Python submissions judged against a problem's test cases.
- Submission verdicts including **Accepted**, **Wrong Answer**, **Time Limit Exceeded**, and **Runtime Error**.
- Contest rooms with unique join codes and **Waiting**, **Live**, and **Finished** states.
- Room leaderboard with periodic browser refresh.
- Submission history, dashboard statistics, and CSV exports.
- Demo command that creates sample users, problems, a live contest, and example submissions.

## User roles

| Role | Main capabilities |
|---|---|
| Player | Browse problems, join contests, submit solutions, and view personal submissions and contest results. |
| Host | Create and manage problems and test cases, host contest rooms, and export room results. |
| Admin | Manage users and roles, in addition to host capabilities. |

## How a contest works

1. A host creates problems and adds sample and hidden test cases.
2. The host creates a room, chooses problems, and starts the contest.
3. Players join the room using its code and submit Python solutions.
4. CodeArena runs submissions against the problem's test cases and records a verdict.
5. The leaderboard ranks participants by contest score and penalty.

## Technology stack

- **Backend:** Python, Django
- **Database:** PostgreSQL (SQLite is also available for local development)
- **Frontend:** Django templates, HTML, CSS, JavaScript, Bootstrap 5
- **Code judging:** Python subprocess with a per-test-case timeout and output limit

## Project structure

```text
accounts/    Authentication, profiles, roles, and permissions
arena/       Contest rooms, participants, scoring, and leaderboards
config/      Django project settings and URL configuration
dashboard/   Home page, dashboard, CSV exports, and demo data command
judge/       Submissions and Python judging engine
problems/    Problems and test cases
static/      CSS and JavaScript
templates/   Django HTML templates
manage.py    Django management utility
```

## Getting started

### Requirements

- Python 3.10 or newer
- PostgreSQL, if using the default database configuration
- Git

### 1. Get the code and create a virtual environment

```powershell
git clone https://github.com/gayathrisreep2006/CodeArena.git
cd CodeArena
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents virtual environment activation, you can invoke the environment's Python directly as `.\venv\Scripts\python.exe`.

### 2. Configure the environment

```powershell
Copy-Item .env.example .env
```

Open `.env` and set `DB_PASSWORD` to your PostgreSQL password. Create an empty PostgreSQL database named `codearena` using pgAdmin or your preferred PostgreSQL tool. The example settings use `postgres` as the database user and `127.0.0.1:5432` as the database address; adjust them in `.env` if yours differ.

### SQLite alternative

For a quick local setup without PostgreSQL, add this line to `.env`:

```dotenv
USE_SQLITE=1
```

When using SQLite, you do not need to create the PostgreSQL database.

### 3. Apply migrations and start the server

```powershell
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser. To stop the development server, press `Ctrl+C` in the terminal.

To create an administrator account for Django's admin site, run:

```powershell
python manage.py createsuperuser
```

The admin site is at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

## Demo data

After migrations, create the sample data with:

```powershell
python manage.py seed_demo
```

The command prints the contest room code. Demo accounts share the password `Demo@12345`:

| Role | Username |
|---|---|
| Host | `demo_host` |
| Player | `player1`, `player2`, `player3` |
| Admin | `demo_admin` |

These are **demo-only credentials**. Do not use them for real accounts or on a publicly accessible deployment.

Suggested walkthrough:

1. Sign in as `demo_host` and explore the problems and contest room.
2. Sign in as a player in another browser session, join the room with the printed code, and view the leaderboard.
3. Submit a solution and inspect its verdict and submission history.
4. Explore the dashboard and the room results CSV export.

## Running tests

```powershell
python manage.py test
```

## Screenshots to add

Add your own screenshots to a folder such as `docs/images/` and embed them below. Capture the application with realistic demo data, crop out unrelated desktop/browser details, and make sure no personal information or secrets are visible.

Recommended screenshots:

1. **Home page** — introduces CodeArena and its main features.
2. **Problem list** — shows the problem catalog, difficulty, and points.
3. **Problem detail** — shows the statement and sample input/output.
4. **Submission result** — shows a submitted solution and its verdict.
5. **Contest room** — shows the room state, timer, and available problems.
6. **Leaderboard** — shows participant rankings and scores.
7. **Host problem/test-case management** — demonstrates how problems and cases are maintained.
8. **Dashboard or CSV results** — shows the summary statistics or exported contest results.

Once you add an image file, include it in the README like this (replace the filename with your screenshot):

```markdown
![CodeArena home page](docs/images/home-page.png)
```

## Limitations and security note

The judge executes submitted Python code in a separate process with a timeout and output-size limit. This provides basic controls for a local academic demo, **not isolation from malicious code**. It is not a full sandbox: do not expose the judge to the public internet or use it to run submissions you do not trust. A production service needs a properly isolated execution environment and additional operational security controls.

## Contributing

This repository is an academic project. Suggestions and bug reports are welcome through GitHub Issues.

## Acknowledgements

Built as a full-stack development project using Django and PostgreSQL. Review and understand the code before presenting or extending it.
