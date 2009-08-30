from django.http import HttpResponseRedirect
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.db.models import Q
from django.contrib.contenttypes.models import ContentType

from forms import RegistrationForm, AuthenticationForm
from shortcuts import render, send_email
from utils import int_to_base32, base32_to_int
from common.models import Alert
from reversion.models import Revision
from productions.models import Part

def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.get_profile()

    latest = []
    content_types = ContentType.objects.filter(
        Q(app_label='plays', model='play')
        | Q(app_label='people', model='person')
        | Q(app_label='productions', model='production')
        | Q(app_label='places', model='place')
    )
    for l in Revision.objects.filter(user=user).order_by('-date_created')[:10]:
        versions = []
        for v in l.version_set.filter(content_type__in=content_types):
            obj = v.content_type.get_object_for_this_type(id=v.object_id)
            url = obj.get_absolute_url()
            versions.append((obj, url))
        latest.append(versions)

    seen = user.visit_set.all()

    return render(request, 'profile.html', {
        'view': user,
        'profile': profile,
        'latest': latest,
        'seen': seen,
    })

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

@login_required
def profile_alert(request, username, id):
    user = get_object_or_404(User, username=username)
    profile = user.get_profile()
    alert = get_object_or_404(Alert, id=id)
    if user != alert.user:
        raise Exception("Trying to unsubscribe someone else's alert?")
    return HttpResponseRedirect(profile.get_absolute_url())
