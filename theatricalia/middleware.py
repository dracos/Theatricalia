import re
import random
from django import http
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.urls import is_valid_path
from django.shortcuts import render
from django.utils.encoding import escape_uri_path, iri_to_uri
from django.utils.http import urlquote

from common.models import Prelaunch

from ratelimitcache import ratelimit


class MyMiddleware(object):
    def __init__(self, get_response, **kwargs):
        self.get_response = get_response
        super(MyMiddleware, self).__init__(**kwargs)

    def __call__(self, request):
        response = self.process_request(request)
        if not response:
            response = self.get_response(request)
        return response


class RemoteAddrMiddleware(MyMiddleware):
    def process_request(self, request):
       if 'REMOTE_ADDR' not in request.META or not request.META['REMOTE_ADDR']:
           request.META['REMOTE_ADDR'] = request.META['HTTP_X_REAL_IP']


class OnlyLowercaseUrls(MyMiddleware):
    def process_request(self, request):
        if 'tickets/lost/' in request.path:
            return
        if request.path.lower() != request.path:
            path = request.get_full_path().replace(request.path, request.path.lower())
            return http.HttpResponseRedirect(path)


class RemoveSlashMiddleware(MyMiddleware):
    response_redirect_class = http.HttpResponsePermanentRedirect

    def process_request(self, request):
        if self.should_redirect_with_slash(request):
            path = self.get_full_path_without_slash(request)
            return self.response_redirect_class(path)

    def should_redirect_with_slash(self, request):
        """
        Return True if settings.APPEND_SLASH is False and removing a slash from
        the request path turns an invalid path into a valid one.
        """
        if not settings.APPEND_SLASH and request.path_info.endswith('/'):
            urlconf = getattr(request, 'urlconf', None)
            return (
                not is_valid_path(request.path_info, urlconf) and
                is_valid_path(request.path_info[:-1], urlconf)
            )
        return False

    def get_full_path_without_slash(self, request):
        """
        Return the full path of the request with a trailing slash removed.

        Raise a RuntimeError if settings.DEBUG is True and request.method is
        POST, PUT, or PATCH.
        """
        new_path = '%s%s' % (
            escape_uri_path(request.path[:-1]),
            ('?' + iri_to_uri(request.META.get('QUERY_STRING', ''))) if request.META.get('QUERY_STRING', '') else ''
        )
        if settings.DEBUG and request.method in ('POST', 'PUT', 'PATCH'):
            raise RuntimeError((""
                "You called this URL via %(method)s, but the URL ends "
                "in a slash and you don't have APPEND_SLASH set. Django can't "
                "redirect to the non-slash URL while maintaining %(method)s data. "
                "Change your form to point to %(url)s (note no trailing "
                "slash), or set APPEND_SLASH=True in your Django settings." % {
                    'method': request.method,
                    'url': request.get_host() + new_path,
                }
            ))
        return new_path


class AlphaMiddleware(MyMiddleware, ratelimit):
    cookie_name = 'godot'
    form_field_name = 'godot'
    
    def __init__(self, get_response):
        super(AlphaMiddleware, self).__init__(get_response, minutes=2, requests=10, expire_after=(2+1)*60)

    def get_password(self):
        return settings.ALPHA_PASSWORD
    
    def process_request(self, request):
        # Process POST if our particular form has been submitted
        if request.method == 'POST' and self.form_field_name in request.POST:
            return self.login_screen(request)
        
        if request.COOKIES.get(self.cookie_name, '') != self.get_password() and not re.match('/static', request.path):
            return self.login_screen(request)
    
    def login_screen(self, request):
        vars = {
            'form_field_name': self.form_field_name,
            'path': request.get_full_path(),
            'error': {},
        }

        check = self.rate_limit_manual(request)
        if check:
            return check

        if request.method == 'POST':
            password = request.POST.get(self.form_field_name, '')
            if password:
                if password == self.get_password():
                    response = http.HttpResponseRedirect(request.get_full_path())
                    self.set_cookie(response, password)
                    return response
                else:
                    self.cache_incr(self.current_key(request))
                    vars['error']['pw'] = 'That is not the correct password.'

            email = request.POST.get('ebygum', '')
            if email:
                try:
                    validate_email(email)
                    obj = Prelaunch(email = email)
                    obj.save()
                    vars['messages'] = ['Thank you; you will hopefully hear from us in the not too distant future.']
                except ValidationError:
                    vars['error']['em'] = 'Please enter a valid email address.'

        statuses = [ 'Painting scenery', 'Auditioning actors', 'Cutting out gobos', 'Rehearsing', 'Measuring for costumes', 'Learning lines', 'Stocking the ice-cream cabinet' ]
        rand_not = int(request.POST.get('not', 0))
        if rand_not >= 1 and rand_not <= 7:
            rand = random.randint(0, len(statuses)-2)
            if rand >= rand_not:
                rand += 1
        else:
            rand = random.randint(0, len(statuses)-1)
        vars['rand'] = rand
        vars['status'] = statuses[rand]

        return render(request, 'alpha_password.html', vars)
    
    def set_cookie(self, response, password):
        response.set_cookie(self.cookie_name, password)

