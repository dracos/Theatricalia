from shortcuts import render, send_email
from forms import RegistrationForm, AuthenticationForm
from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from utils import int_to_base32, base32_to_int
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.views.decorators.cache import never_cache

def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            send_confirmation_email(request, user)
            return render(request, 'registration/register-checkemail.html')
    return render(request, 'registration/register.html', { 'form': form })

def login(request, template_name='registration/login.html', redirect_field_name=REDIRECT_FIELD_NAME):
    if request.user.is_authenticated():
        return HttpResponseRedirect(request.REQUEST.get(redirect_field_name, '/'))

    redirect_to = request.REQUEST.get(redirect_field_name, '')

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            from django.contrib.auth import login
            login(request, form.get_user())
            if request.session.test_cookie_worked():
                request.session.delete_test_cookie()
            if not redirect_to or '//' in redirect_to or ' ' in redirect_to:
                redirect_to = settings.LOGIN_REDIRECT_URL
            return HttpResponseRedirect(redirect_to)
    else:
        form = AuthenticationForm(request)

    request.session.set_test_cookie()

    return render(request, template_name, {
        'form': form,
        redirect_field_name: redirect_to,
    })
login = never_cache(login)

#def registration_complete(request):
#    return render(request, 'accounts/registration_complete.html', {})

def register_confirm(request, uidb32, token):
    try:
        uid_int = base32_to_int(uidb32)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)
    if default_token_generator.check_token(user, token):
        p = user.get_profile()
        p.email_validated = True
        print p
        p.save()
        user.backend = 'theatricalia.profiles.backends.ModelBackend' # Needs backend to login?
        from django.contrib.auth import login
        login(request, user)
        print user.is_authenticated()
        # Decide what to do with someone confirming registration
        #return render(request, 'hmm')
        #return HttpResponseRedirect(reverse('validate-email-success'))
    print request.user.is_authenticated()
    return HttpResponseRedirect('/')

def send_confirmation_email(request, user):
    send_email(request, "Theatricalia account confirmation",
        'registration/confirmation-email.txt',
        {
            'email': user.email,
            'uid': int_to_base32(user.id),
            'user': user,
            'token': default_token_generator.make_token(user),
            'protocol': 'http',
        }, user.email
    )
