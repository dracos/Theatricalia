import re, random
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from django.core.validators import email_re
from common.models import Prelaunch
from shortcuts import render

from ratelimitcache import ratelimit

class OnlyLowercaseUrls:
    def process_request(self, request):
        if request.path.lower() != request.path:
            path = request.get_full_path().replace(request.path, request.path.lower())
            return HttpResponseRedirect(path)

class AlphaMiddleware(ratelimit):
    cookie_name = 'godot'
    form_field_name = 'godot'
    
    def __init__(self):
        super(AlphaMiddleware, self).__init__(minutes=2, requests=10, expire_after=(2+1)*60)

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
                    response = HttpResponseRedirect(request.get_full_path())
                    self.set_cookie(response, password)
                    return response
                else:
                    self.cache_incr(self.current_key(request))
                    vars['error']['pw'] = 'That is not the correct password.'

            email = request.POST.get('ebygum', '')
            if email:
                if email_re.match(email):
                    obj = Prelaunch(email = email)
                    obj.save()
                    vars['messages'] = ['Thank you; you will hopefully hear from us in the not too distant future.']
                else:
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

