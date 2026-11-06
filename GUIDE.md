# CodeArena - Run, Demo and Viva Guide

## 1. Run (first time)
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env          (edit DB_PASSWORD)
-- create empty database "codearena" in pgAdmin --
python manage.py migrate
python manage.py seed_demo      (dummy users, problems, a live contest)
python manage.py createsuperuser   (optional, for /admin)
python manage.py runserver
python manage.py test           (16 tests, should all pass)
```
Demo logins (password `Demo@12345`): `demo_host`, `player1`, `player2`, `player3`, `demo_admin`.
`seed_demo` prints the contest room code.

## 2. Demo flow (5 minutes)
1. Home page -> explain the problem (practice + live contests, auto judging).
2. Login `demo_host` -> create a problem -> add sample + hidden test cases.
3. Create a contest room -> pick problems -> Start.
4. Open a second browser/incognito as `player1` -> join with room code -> submit a correct solution -> show Accepted; submit a wrong one -> Wrong Answer; submit `while True: pass` -> Time Limit.
5. Show the leaderboard updating by itself (and the JSON endpoint `/arena/<code>/leaderboard.json`).
6. Host: download results CSV. Dashboard: statistics. `demo_admin`: Users page (role change).
7. Show a player opening `/problems/new/` -> 403 (access control).

## 3. Where is what (for viva)
| Syllabus point | File |
|---|---|
| Models, relationships, constraints | `*/models.py` (UniqueConstraint in `arena/models.py`) |
| Roles / authorization | `accounts/permissions.py`, `_can_manage()` in views |
| ModelForms + validation | `problems/forms.py`, `arena/forms.py`, `accounts/forms.py` |
| Judge engine (subprocess + timeout) | `judge/runner.py` |
| Scoring and ranking | `arena/services.py` |
| JSON endpoint | `arena/views.py` -> `leaderboard_json` |
| CSV export | `dashboard/views.py` |
| Aggregate ORM queries | `dashboard/views.py` -> `dashboard` |
| Template inheritance | `templates/base.html`, `templates/partials/` |
| Search / filter / pagination | `problem_list`, `room_list`, `my_submissions`, `user_list` |

## 4. Questions to prepare
- How is code run safely? (separate process, `-I` isolated mode, timeout, output limit, Python only, no shell; mention it is not a full sandbox and Docker would be the next step)
- How is a player stopped from seeing hidden test cases / others' code? (queries filter `is_sample`, `submission_detail` checks owner/host/admin)
- How is double joining prevented? (`UniqueConstraint(room, user)` + `get_or_create`)
- How does the leaderboard break ties? (score, then penalty minutes, 5 min per wrong attempt)
- How does the room finish automatically? (`Room.sync_status()` compares now with `end_time`)
- Why polling and not WebSockets? (syllabus scope; JSON endpoint + `setInterval` is simpler and reliable)
