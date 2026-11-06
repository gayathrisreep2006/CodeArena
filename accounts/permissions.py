"""Role-based access helpers. Everyone imports from here."""
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied


def _role(user):
    return getattr(getattr(user, "profile", None), "role", None)


class HostRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Only Host or Admin may access (class-based views)."""

    def test_func(self):
        return _role(self.request.user) in ("host", "admin")


class AdminRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return _role(self.request.user) == "admin"


def host_required(view_func):
    """Decorator for function-based views: Host or Admin only."""
    from functools import wraps
    from django.contrib.auth.decorators import login_required

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if _role(request.user) not in ("host", "admin"):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def admin_required(view_func):
    from functools import wraps
    from django.contrib.auth.decorators import login_required

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if _role(request.user) != "admin":
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper
