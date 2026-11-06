from django.test import TestCase as DjangoTestCase

from django.contrib.auth.models import User
from problems.models import Problem, TestCase

from .models import Submission
from .runner import judge_submission


class JudgeTests(DjangoTestCase):
    def setUp(self):
        self.user = User.objects.create_user("u1", password="pw12345!x")
        self.problem = Problem.objects.create(title="Add", description="sum", created_by=self.user)
        TestCase.objects.create(problem=self.problem, input_data="2 3\n", expected_output="5")

    def verdict(self, code):
        sub = Submission.objects.create(user=self.user, problem=self.problem, code=code)
        return judge_submission(sub).verdict

    def test_accepted(self):
        self.assertEqual(self.verdict("a,b=map(int,input().split());print(a+b)"), Submission.ACCEPTED)

    def test_wrong_answer(self):
        self.assertEqual(self.verdict("print(0)"), Submission.WRONG)

    def test_runtime_error(self):
        self.assertEqual(self.verdict("1/0"), Submission.ERROR)

    def test_time_limit(self):
        self.problem.time_limit = 1
        self.problem.save()
        self.assertEqual(self.verdict("while True: pass"), Submission.TLE)
