import re
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from shortcuts import render

class OnlyLowercaseUrls:
    def process_request(self, request):
        if request.path.lower() != request.path:
            path = request.get_full_path().replace(request.path, request.path.lower())
            return HttpResponseRedirect(path)

class AlphaMiddleware(object):
    cookie_name = 'alpha'
    form_field_name = 'alpha'
    
    def get_password(self):
        return settings.ALPHA_PASSWORD
    
    def process_request(self, request):
        # Process POST if our particular form has been submitted
        if request.method == 'POST' and self.form_field_name in request.POST:
            return self.login_screen(request)
        
        if request.COOKIES.get(self.cookie_name, '') != self.get_password() and not re.match('/static', request.path):
            return self.login_screen(request)
    
    def login_screen(self, request):
        msg = ''
        if request.method == 'POST':
            password = request.POST.get(self.form_field_name, '')
            if password == self.get_password():
                response = HttpResponseRedirect(request.get_full_path())
                self.set_cookie(response, password)
                return response
            else:
                msg = 'Incorrect password'
        return render(request, 'alpha_password.html', {
            'msg': msg,
            'form_field_name': self.form_field_name,
            'path': request.get_full_path(),
        })
    
    def set_cookie(self, response, password):
        response.set_cookie(self.cookie_name, password)
