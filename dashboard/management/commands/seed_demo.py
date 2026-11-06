"""Create dummy data for the demo:  python manage.py seed_demo
All users share the password printed at the end. Safe to run more than once."""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from arena.models import Participant, Room
from judge.models import Submission
from judge.runner import judge_submission
from problems.models import Problem, TestCase

PASSWORD = "Demo@12345"

PROBLEMS = [
    ("Sum of Two Numbers", "easy", 100,
     "Read two integers on one line and print their sum.",
     [("2 3", "5", True), ("10 -4", "6", True), ("0 0", "0", False), ("100 250", "350", False)],
     "a, b = map(int, input().split())\nprint(a + b)"),
    ("Even or Odd", "easy", 100,
     "Read an integer n. Print Even if n is even, otherwise print Odd.",
     [("4", "Even", True), ("7", "Odd", True), ("0", "Even", False), ("-3", "Odd", False)],
     "n = int(input())\nprint('Even' if n % 2 == 0 else 'Odd')"),
    ("Reverse a String", "medium", 200,
     "Read a string and print it reversed.",
     [("hello", "olleh", True), ("CodeArena", "anerAedoC", False), ("a", "a", False)],
     "print(input()[::-1])"),
    ("FizzBuzz Single", "medium", 200,
     "Read n. Print FizzBuzz if divisible by 3 and 5, Fizz if by 3, Buzz if by 5, otherwise n.",
     [("15", "FizzBuzz", True), ("9", "Fizz", True), ("10", "Buzz", False), ("7", "7", False)],
     "n = int(input())\nprint('FizzBuzz' if n % 15 == 0 else 'Fizz' if n % 3 == 0 else 'Buzz' if n % 5 == 0 else n)"),
]

WRONG_CODE = "print('wrong')"


class Command(BaseCommand):
    help = "Create demo users, problems, a contest room and submissions"

    def handle(self, *args, **options):
        def make_user(name, role):
            user, created = User.objects.get_or_create(username=name, defaults={"email": f"{name}@example.com"})
            if created:
                user.set_password(PASSWORD)
                user.save()
            user.profile.role = role
            user.profile.save()
            return user

        host = make_user("demo_host", "host")
        players = [make_user(f"player{i}", "player") for i in range(1, 4)]
        make_user("demo_admin", "admin")

        problems, solutions = [], {}
        for title, diff, points, desc, cases, solution in PROBLEMS:
            problem, created = Problem.objects.get_or_create(
                title=title, defaults={"difficulty": diff, "points": points, "description": desc,
                                       "created_by": host, "time_limit": 2})
            if created:
                for inp, out, sample in cases:
                    TestCase.objects.create(problem=problem, input_data=inp + "\n", expected_output=out, is_sample=sample)
            problems.append(problem)
            solutions[problem.pk] = solution

        room, created = Room.objects.get_or_create(
            title="Demo Battle", defaults={"host": host, "duration_minutes": 60})
        if created:
            room.problems.set(problems)
            room.status = Room.LIVE
            room.start_time = timezone.now() - timedelta(minutes=20)
            room.save()
            for p in players:
                Participant.objects.get_or_create(room=room, user=p)
            plan = [  # (player index, problem index, solves?, minutes after start)
                (0, 0, True, 3), (0, 1, True, 7), (0, 2, False, 10), (0, 2, True, 14),
                (1, 0, True, 5), (1, 1, False, 9), (1, 1, True, 12),
                (2, 0, False, 6), (2, 0, True, 11),
            ]
            for pi, qi, solves, minute in plan:
                code = solutions[problems[qi].pk] if solves else WRONG_CODE
                sub = Submission.objects.create(user=players[pi], problem=problems[qi], room=room, code=code)
                judge_submission(sub)
                Submission.objects.filter(pk=sub.pk).update(submitted_at=room.start_time + timedelta(minutes=minute))

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"Logins (password for all: {PASSWORD}): demo_host, player1, player2, player3, demo_admin")
        self.stdout.write(f"Contest room code: {room.code}")
