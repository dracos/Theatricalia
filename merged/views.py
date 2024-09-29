from django.http import Http404, HttpResponseRedirect
from django.core.mail import mail_admins
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse

from shortcuts import check_url, UnmatchingSlugException
from merged.models import Redirect
from merged.utils import merge_thing, check_old_exists
from places.models import Place
from people.models import Person
from productions.models import ProductionCompany, Production
from plays.models import Play
from utils import int_to_base32, base32_to_int


class MergeTokenGenerator(PasswordResetTokenGenerator):
    # No timeout
    def _num_seconds(self, dt):
        return 0

    def _make_hash_value(self, obj, timestamp):
        return f'{obj.pk}{obj.old_object_id}{obj.new_object_id}'


token_generator = MergeTokenGenerator()

type_dict = {
    'play': Play,
    'place': Place,
    'person': Person,
    'company': ProductionCompany,
    'production': Production,
}


def production_merge(request, play_id, play, id):
    return merge(request, 'production', id)


def merge(request, type, id, slug=None):
    if type in type_dict:
        obj_type = type_dict[type]
    else:
        raise Http404

    try:
        object = check_url(obj_type, id, slug)
    except UnmatchingSlugException as e:
        return HttpResponseRedirect(e.args[0].get_absolute_url() + "/merge")

    if request.POST.get('stop'):
        if 'merging_' + type in request.session:
            del request.session['merging_' + type]
        if not request.session.keys():
            request.session.flush()
        if request.user.is_authenticated:
            messages.success(request, u"We have forgotten your search for a duplicate.")
        return HttpResponseRedirect(object.get_absolute_url())

    if request.POST.get('dupe') and request.session.get('merging_' + type):
        # Send email
        other_id = request.session['merging_' + type]['id']
        other = obj_type.objects.get(id=other_id)

        r = Redirect.objects.create(old_object_id=other.id, new_object=object)
        token = token_generator.make_token(r)
        mail_admins(
            'Merge request',
            '%s\nand\n%s\n\n%s : https://theatricalia.com%s\n%s : https://theatricalia.com%s\n\nRequest made by: %s %s\n\nApprove: https://theatricalia.com%s (old to new)\nApprove: https://theatricalia.com%s (new to old)\nReject: https://theatricalia.com%s\n\nATB,\nMatthew' % (
                other, object, int_to_base32(other.id), other.get_absolute_url(),
                int_to_base32(object.id), object.get_absolute_url(), request.user, getattr(request.user, 'email', ''),
                reverse('merge_approve', args=(int_to_base32(r.id), token, 'old-to-new')),
                reverse('merge_approve', args=(int_to_base32(r.id), token, 'new-to-old')),
                reverse('merge_approve', args=(int_to_base32(r.id), token, 'reject')),
            ),
            fail_silently=True
        )

        del request.session['merging_' + type]
        return render(request, 'merged/thanks.html', {
            'object': object,
            'other': other,
        })

    request.session['merging_' + type] = {
        'id': object.id,
        'name': str(object),
    }

    return render(request, 'merged/start.html', {
        'object': object,
    })


def approve(request, uidb32, token, type):
    try:
        uid_int = base32_to_int(uidb32)
    except ValueError:
        raise Http404

    redirect = Redirect.objects.get(id=uid_int)

    if not request.user or not request.user.is_superuser or not token_generator.check_token(redirect, token):
        return HttpResponseRedirect('/')

    if type == 'reject':
        redirect.delete()
        return HttpResponseRedirect('/')

    if old := check_old_exists(redirect):
        if type == 'old-to-new':
            merge_thing(redirect.new_object, old, redirect)
        elif type == 'new-to-old':
            merge_thing(old, redirect.new_object, redirect)

    return HttpResponseRedirect(redirect.new_object.get_absolute_url())
