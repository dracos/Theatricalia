from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.conf import settings
from django.shortcuts import render, resolve_url
from django.template.response import TemplateResponse
from django.utils.http import is_safe_url
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

from django.db.models import Q, Min
from django.db.models.expressions import RawSQL
from django.contrib.contenttypes.models import ContentType
from django_comments.models import Comment
from django.contrib import messages

from .forms import RegistrationForm, AuthenticationForm, ProfileForm
from shortcuts import send_email
from utils import int_to_base32, base32_to_int
from reversion.models import Revision
from .models import User


@login_required
def profile_user(request):
    return HttpResponseRedirect(request.user.profile.get_absolute_url())


def profile(request, username):
    user = get_object_or_404(User, username=username)
    profile = user.profile

    latest = []
    content_types = ContentType.objects.filter(
        Q(app_label='plays', model='play')
        | Q(app_label='people', model='person')
        | Q(app_label='productions', model='production')
        | Q(app_label='places', model='place')
    )
    for revision in Revision.objects.filter(user=user, version__content_type__in=content_types).distinct().order_by('-date_created')[:10]:
        versions = []
        for v in revision.version_set.filter(content_type__in=content_types):
            try:
                obj = v.content_type.get_object_for_this_type(id=v.object_id)
                url = obj.get_absolute_url()
                versions.append((obj, url))
            except:
                pass
        latest.append(versions)

    # Min bit isn't needed except to make sure the GROUP BY gets added
    seen = user.visit_set.annotate(min_press_date=Min('production__place__press_date')).annotate(best_date=RawSQL('MIN(IFNULL(productions_place.press_date, IF(productions_place.end_date!="", productions_place.end_date, productions_place.start_date)))', ())).order_by('-best_date')

    return render(request, 'profile.html', {
        'view': user,
        'profile': profile,
        'latest': latest,
        'observations': Comment.objects.filter(
            user=user, is_public=True, is_removed=False).order_by('-submit_date')[:5],
        'seen': seen,
    })


def register(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/')

    form = RegistrationForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            perform_login(request, user)
            send_confirmation_email(request, user)
            return render(request, 'registration/register-checkemail.html')
    return render(request, 'registration/register.html', {'form': form})


@sensitive_post_parameters()
@csrf_protect
@never_cache
def login(request, template_name='registration/login.html',
          redirect_field_name=REDIRECT_FIELD_NAME,
          authentication_form=AuthenticationForm,
          extra_context=None):
    """
    Displays the login form and handles the login action.
    """
    redirect_to = request.POST.get(redirect_field_name,
                                   request.GET.get(redirect_field_name, ''))

    if request.method == "POST":
        form = authentication_form(request, data=request.POST)
        if form.is_valid():

            # Ensure the user-originating redirection url is safe.
            if not is_safe_url(url=redirect_to, allowed_hosts=request.get_host()):
                redirect_to = resolve_url(settings.LOGIN_REDIRECT_URL)

            # Okay, security check complete. Log the user in.
            auth_login(request, form.get_user())

            return HttpResponseRedirect(redirect_to)
    else:
        form = authentication_form(request)

    current_site = get_current_site(request)

    context = {
        'form': form,
        redirect_field_name: redirect_to,
        'site': current_site,
        'site_name': current_site.name,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


# def registration_complete(request):
#     return render(request, 'accounts/registration_complete.html', {})

def perform_login(request, user):
    user.backend = 'profiles.backends.ModelBackend'  # Needs backend to login?
    auth_login(request, user)


def register_confirm(request, uidb32, token):
    try:
        uid_int = base32_to_int(uidb32)
    except ValueError:
        raise Http404

    user = get_object_or_404(User, id=uid_int)
    if default_token_generator.check_token(user, token):
        p = user.profile
        p.email_validated = True
        p.save()
        perform_login(request, user)
        # Decide what to do with someone confirming registration
        return render(request, 'registration/validated.html', {
            'user': user,
        })
    return HttpResponseRedirect('/')


def send_confirmation_email(request, user):
    send_email(
        request, "Theatricalia account confirmation",
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
    profile = request.user.profile
    form = ProfileForm(request.POST or None, instance=profile)

    if request.method == 'POST':
        if request.POST.get('disregard'):
            messages.success(request, u"All right, we\u2019ve ignored any changes you made.")
            return HttpResponseRedirect(profile.get_absolute_url())
        if form.is_valid():
            form.save()
            messages.success(request, "Your changes have been stored; thank you.")
            return HttpResponseRedirect(profile.get_absolute_url())

    return render(request, 'profile-edit.html', {
        'form': form,
        'profile': profile,
    })


# @login_required
# def profile_alert(request, id):
#    profile = request.user.profile
#    if id[0]=='l':
#        alert = get_object_or_404(AlertLocal, id=id[1:])
#    else:
#        alert = get_object_or_404(Alert, id=id)
#    if request.user != alert.user:
#        raise Exception("Trying to unsubscribe someone else's alert?")
#    alert.delete()
#    messages.success(request, "Your alert has been removed.")
#    return HttpResponseRedirect(profile.get_edit_url())
