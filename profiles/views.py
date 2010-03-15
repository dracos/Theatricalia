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
from django.contrib.comments.models import Comment

from forms import RegistrationForm, AuthenticationForm, ProfileForm
from shortcuts import render, send_email
from utils import int_to_base32, base32_to_int
from common.models import Alert, AlertLocal
from reversion.models import Revision
from productions.models import Part

@login_required
def profile_user(request):
    return HttpResponseRedirect(request.user.get_profile().get_absolute_url())

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
    for l in Revision.objects.filter(user=user, version__content_type__in=content_types).distinct().order_by('-date_created')[:10]:
        versions = []
        for v in l.version_set.filter(content_type__in=content_types):
            try:
                obj = v.content_type.get_object_for_this_type(id=v.object_id)
                url = obj.get_absolute_url()
                versions.append((obj, url))
            except:
                pass
        latest.append(versions)

    seen = user.visit_set.order_by('-IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date))', 'production__place__press_date').distinct()

    return render(request, 'profile.html', {
        'view': user,
        'profile': profile,
        'latest': latest,
        'observations': Comment.objects.filter(user=user).order_by('-submit_date')[:5],
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
    redirect_to = request.REQUEST.get(redirect_field_name, '')
    if not redirect_to: redirect_to = settings.LOGIN_REDIRECT_URL

    if request.user.is_authenticated():
        return HttpResponseRedirect(redirect_to)

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
        p.save()
        user.backend = 'theatricalia.profiles.backends.ModelBackend' # Needs backend to login?
        from django.contrib.auth import login
        login(request, user)
        # Decide what to do with someone confirming registration
        return render(request, 'registration/validated.html', {
            'user': user,
        })
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
def profile_edit(request):
    profile = request.user.get_profile()
    form = ProfileForm(request.POST or None, instance=profile)

    if request.method == 'POST':
        if request.POST.get('disregard'):
            request.user.message_set.create(message=u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(profile.get_absolute_url())
        if form.is_valid():
            form.save()
            request.user.message_set.create(message="Your changes have been stored; thank you.")
            return HttpResponseRedirect(profile.get_absolute_url())

    return render(request, 'profile-edit.html', {
        'form': form,
        'profile': profile,
    })

@login_required
def profile_alert(request, id):
    profile = request.user.get_profile()
    if id[0]=='l':
        alert = get_object_or_404(AlertLocal, id=id[1:])
    else:
        alert = get_object_or_404(Alert, id=id)
    if request.user != alert.user:
        raise Exception("Trying to unsubscribe someone else's alert?")
    alert.delete()
    request.user.message_set.create(message="Your alert has been removed.")
    return HttpResponseRedirect(profile.get_edit_url())
