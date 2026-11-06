# CodeArena - Live Coding Contest and Practice Platform

CodeArena is a Django and PostgreSQL web application where hosts create coding problems and contest rooms,
players submit Python code that is automatically judged against test cases, and a live leaderboard ranks
participants.

## Problem Statement
(Team: expand this section using the technical problem statement we prepared.)

## Features
- Registration, login, logout with three roles: Player, Host, Admin (role-based access control)
- Problem management with test cases (Host): create, view, update, delete, search, filter, pagination
- Automatic judging of submitted Python code (Accepted / Wrong Answer / Time Limit / Runtime Error)
- Submission history for every user
- Contest rooms with a join code, status workflow (Waiting -> Live -> Finished)
- Leaderboard with auto-refresh using a JSON endpoint
- Dashboard with summary statistics, CSV export of results

## Technologies
Python, Django, PostgreSQL, HTML, CSS, Bootstrap 5, JavaScript, Django Template Language, Django ORM,
Django authentication, Git and GitHub.

## Installation
```
git clone <repo-url>
cd codearena
python -m venv venv
venv\Scripts\activate          # Windows   (Linux/Mac: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env         # Linux/Mac: cp .env.example .env  -> then edit DB_PASSWORD
```
Create an empty PostgreSQL database named `codearena` (pgAdmin or `createdb codearena`), then:
```
python manage.py migrate
python manage.py seed_demo        # optional: dummy data for demo
python manage.py createsuperuser
python manage.py runserver
```
Open http://127.0.0.1:8000

## Usage
1. Register as a Host, create a problem with test cases.
2. Register as a Player, open the problem, submit code, see the verdict.
3. Host creates a contest room, Players join using the room code, the leaderboard updates live.

## Database Design
(Add ER diagram image here.)

## Screenshots
(Add screenshots of important pages here.)

## Acknowledgement
Parts of the code were generated with AI assistance and have been reviewed and understood by the team.
