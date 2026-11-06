from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase as DjangoTestCase
from django.urls import reverse
from django.utils import timezone

from judge.models import Submission
from problems.models import Problem, TestCase

from .models import Participant, Room
from .services import build_leaderboard

SOLVE = "a,b=map(int,input().split());print(a+b)"


class AccessAndFlowTests(DjangoTestCase):
    def setUp(self):
        self.host = User.objects.create_user("host1", "h@x.com", "pw12345!x")
        self.host.profile.role = "host"; self.host.profile.save()
        self.p1 = User.objects.create_user("p1", "p1@x.com", "pw12345!x")
        self.p2 = User.objects.create_user("p2", "p2@x.com", "pw12345!x")
        self.problem = Problem.objects.create(title="Add", description="sum", points=100, created_by=self.host)
        TestCase.objects.create(problem=self.problem, input_data="2 3\n", expected_output="5")
        self.room = Room.objects.create(title="R", host=self.host, duration_minutes=30,
                                        status=Room.LIVE, start_time=timezone.now() - timedelta(minutes=5))
        self.room.problems.add(self.problem)

    # ---- access control ----
    def test_player_cannot_create_problem(self):
        self.client.login(username="p1", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("problems:create")).status_code, 403)

    def test_host_can_create_problem(self):
        self.client.login(username="host1", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("problems:create")).status_code, 200)

    def test_other_host_cannot_edit_problem(self):
        other = User.objects.create_user("host2", "h2@x.com", "pw12345!x")
        other.profile.role = "host"; other.profile.save()
        self.client.login(username="host2", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("problems:edit", args=[self.problem.pk])).status_code, 403)

    def test_login_required_for_rooms(self):
        self.assertEqual(self.client.get(reverse("arena:list")).status_code, 302)

    def test_hidden_cases_not_shown(self):
        TestCase.objects.create(problem=self.problem, input_data="9 9\n", expected_output="18", is_sample=False)
        resp = self.client.get(reverse("problems:detail", args=[self.problem.pk]))
        self.assertNotContains(resp, "18")

    def test_cannot_view_someone_elses_submission(self):
        sub = Submission.objects.create(user=self.p1, problem=self.problem, code="x")
        self.client.login(username="p2", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("judge:detail", args=[sub.pk])).status_code, 403)

    def test_admin_cannot_be_chosen_at_registration(self):
        resp = self.client.post(reverse("accounts:register"), {
            "username": "sneaky", "email": "s@x.com", "password1": "Str0ng!Pass99",
            "password2": "Str0ng!Pass99", "role": "admin"})
        self.assertEqual(resp.status_code, 200)  # form invalid, re-rendered
        self.assertFalse(User.objects.filter(username="sneaky").exists())

    # ---- contest flow ----
    def test_submit_requires_joining(self):
        self.client.login(username="p1", password="pw12345!x")
        self.client.post(reverse("judge:submit", args=[self.problem.pk]), {"code": SOLVE, "room": self.room.code})
        self.assertEqual(Submission.objects.count(), 0)

    def test_join_submit_and_leaderboard(self):
        self.client.login(username="p1", password="pw12345!x")
        self.client.post(reverse("arena:join"), {"code": self.room.code})
        self.assertTrue(Participant.objects.filter(room=self.room, user=self.p1).exists())
        self.client.post(reverse("judge:submit", args=[self.problem.pk]), {"code": SOLVE, "room": self.room.code})
        board = build_leaderboard(self.room)
        self.assertEqual(board[0]["username"], "p1")
        self.assertEqual(board[0]["score"], 100)

    def test_json_endpoint(self):
        self.client.login(username="p1", password="pw12345!x")
        resp = self.client.get(reverse("arena:leaderboard_json", args=[self.room.code]))
        self.assertEqual(resp.status_code, 200)
        self.assertIn("leaderboard", resp.json())

    def test_expired_room_closes_and_blocks_submit(self):
        self.room.start_time = timezone.now() - timedelta(minutes=99)
        self.room.save()
        Participant.objects.create(room=self.room, user=self.p1)
        self.client.login(username="p1", password="pw12345!x")
        self.client.post(reverse("judge:submit", args=[self.problem.pk]), {"code": SOLVE, "room": self.room.code})
        self.room.refresh_from_db()
        self.assertEqual(self.room.status, Room.FINISHED)
        self.assertEqual(Submission.objects.count(), 0)

    def test_csv_only_for_room_owner(self):
        self.client.login(username="p1", password="pw12345!x")
        self.assertEqual(self.client.get(reverse("dashboard:room_csv", args=[self.room.code])).status_code, 403)
        self.client.login(username="host1", password="pw12345!x")
        resp = self.client.get(reverse("dashboard:room_csv", args=[self.room.code]))
        self.assertEqual(resp["Content-Type"], "text/csv")
