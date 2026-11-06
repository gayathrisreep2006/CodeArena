"""Leaderboard logic. Scoring rules:
 - A problem is solved when the FIRST Accepted submission arrives during the contest time.
 - Score = sum of the points of solved problems.
 - Ties are broken by penalty time = minutes from contest start to each solve
   + 5 penalty minutes for every wrong attempt made before that solve.
"""
from judge.models import Submission

WRONG_PENALTY_MINUTES = 5


def build_leaderboard(room):
    rows = {}
    for participant in room.participants.select_related("user"):
        rows[participant.user_id] = {
            "username": participant.user.username, "solved": 0, "score": 0,
            "penalty": 0.0, "wrong": 0, "_solved_problems": set(), "_wrong_by_problem": {},
        }
    if not room.start_time:
        return _finish(rows)

    submissions = (room.submissions.filter(submitted_at__gte=room.start_time)
                   .select_related("problem").order_by("submitted_at"))
    for sub in submissions:
        if room.end_time and sub.submitted_at > room.end_time:
            continue
        row = rows.get(sub.user_id)
        if row is None or sub.problem_id in row["_solved_problems"]:
            continue
        if sub.verdict == Submission.ACCEPTED:
            row["_solved_problems"].add(sub.problem_id)
            row["solved"] += 1
            row["score"] += sub.problem.points
            minutes = (sub.submitted_at - room.start_time).total_seconds() / 60
            wrong_before = row["_wrong_by_problem"].get(sub.problem_id, 0)
            row["penalty"] += minutes + WRONG_PENALTY_MINUTES * wrong_before
        elif sub.verdict != Submission.PENDING:
            row["_wrong_by_problem"][sub.problem_id] = row["_wrong_by_problem"].get(sub.problem_id, 0) + 1
            row["wrong"] += 1
    return _finish(rows)


def _finish(rows):
    ordered = sorted(rows.values(), key=lambda r: (-r["score"], r["penalty"], r["username"]))
    result = []
    for rank, row in enumerate(ordered, start=1):
        result.append({
            "rank": rank, "username": row["username"], "solved": row["solved"],
            "score": row["score"], "penalty": round(row["penalty"], 1), "wrong": row["wrong"],
        })
    return result
