"""Judge engine: runs submitted Python code against test cases.

MEMBER 3 owns this file. The skeleton below already works for simple cases;
improve it (output limits, better error messages) and write the submit view.
SAFETY: only Python, a hard timeout, and output size limit. Never run the
code with shell=True.
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from django.conf import settings

from .models import Submission


def run_code(code, input_data, time_limit):
    """Run `code` once. Returns (status, stdout, stderr, elapsed_ms)."""
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "solution.py"
        path.write_text(code, encoding="utf-8")
        start = time.monotonic()
        try:
            result = subprocess.run(
                [sys.executable, "-I", str(path)],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=time_limit,
                cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return "timeout", "", "", int((time.monotonic() - start) * 1000)
        elapsed = int((time.monotonic() - start) * 1000)
        limit = settings.JUDGE_MAX_OUTPUT_CHARS
        stdout, stderr = result.stdout[:limit], result.stderr[:limit]
        if result.returncode != 0:
            return "error", stdout, stderr, elapsed
        return "ok", stdout, stderr, elapsed


def judge_submission(submission):
    """Run every test case of the problem and save the verdict on the submission."""
    problem = submission.problem
    cases = list(problem.test_cases.all())
    submission.total_cases = len(cases)
    passed, total_ms = 0, 0
    verdict, message = Submission.ACCEPTED, ""

    for case in cases:
        status, out, err, ms = run_code(submission.code, case.input_data, problem.time_limit)
        total_ms += ms
        if status == "timeout":
            verdict, message = Submission.TLE, "Time limit exceeded"
            break
        if status == "error":
            verdict, message = Submission.ERROR, err
            break
        if out.strip() != case.expected_output.strip():
            verdict, message = Submission.WRONG, "Output did not match on a test case"
            break
        passed += 1

    if not cases:
        verdict, message = Submission.ERROR, "This problem has no test cases yet"
    submission.verdict = verdict
    submission.passed_cases = passed
    submission.runtime_ms = total_ms
    submission.error_message = message
    submission.save()
    return submission
