from functools import wraps
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.conf import settings


# decorators for web users ----------------------------
def student_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 4:
                request.layout = 'layouts/student-layout.html'
                return function(request, *args, **kwargs)
            else:
                messages.error(
                    request, 'Your account not associated with any student account.'
                )
                return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            messages.error(
                request, 'You have to login to access your account.'
            )
            return HttpResponseRedirect(settings.LOGIN_URL)
    return wrap


def instructor_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 3:
                request.layout = 'layouts/instructor-layout.html'
                return function(request, *args, **kwargs)
            else:
                messages.error(
                    request, 'Your account not associated with any instructor account.'
                )
                return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            messages.error(
                request, 'You have to login to access your account.'
            )
            return HttpResponseRedirect(settings.LOGIN_URL)
    return wrap



def user_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 4:
                request.layout = 'layouts/student-layout.html'
                return function(request, *args, **kwargs)
            elif request.user.role == 3:
                request.layout = 'layouts/instructor-layout.html'
                return function(request, *args, **kwargs)
            else:
                messages.error(
                    request, 'Your account not associated with any instructor or student account.'
                )
                return HttpResponseRedirect(settings.LOGIN_URL)
        else:
            messages.error(
                request, 'You have to login to access your account.'
            )
            return HttpResponseRedirect(settings.LOGIN_URL)
    return wrap


def admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 1 or request.user.role == 2:
                request.layout = 'layouts/admin-layout.html'
                return function(request, *args, **kwargs)
            else:
                messages.error(
                    request, 'Your account not associated with any admin account.'
                )
                return HttpResponseRedirect('/admin/login')
        else:
            messages.error(
                request, 'You have to login to access your account.'
            )
            return HttpResponseRedirect('/admin/login')
    return wrap


def super_admin_required(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.role == 1:
                request.layout = 'layouts/admin-layout.html'
                return function(request, *args, **kwargs)
            else:
                messages.error(
                    request, 'Your account not associated with any admin account.'
                )
                return HttpResponseRedirect('/admin/login')
        else:
            messages.error(
                request, 'You have to login to access your account.'
            )
            return HttpResponseRedirect('/admin/login')
    return wrap

# decorators for mobile users ----------------------------
