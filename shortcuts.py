import os
from django.template import RequestContext, loader, Context
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.http import Http404
from utils import base32_to_int, MistypedIDException
from merged.models import Redirect

class UnmatchingSlugException(Exception):
    pass

def check_url(type, id, slug=None):
    mistyped = False
    try:
        id = base32_to_int(id)
    except MistypedIDException, e:
        mistyped = True
        id = e.args[0]
    except:
        raise Http404('Could not match id %s' % id)
    try:
        obj = type.objects.get(id=id)
    except type.DoesNotExist:
        content_type = ContentType.objects.get_for_model(type)
        try:
            redir = Redirect.objects.get(old_object_id=id, content_type=content_type)
            obj = redir.new_object
            mistyped = True
        except Redirect.DoesNotExist:
            raise Http404('No %s matches the given query.' % type._meta.object_name)
    if (slug is not None and obj.slug != slug) or mistyped:
        raise UnmatchingSlugException(obj)
    return obj
    
def send_email(request, subject, template, context, to):
    t = loader.get_template(template)
    context.update({
        'host': request.META['HTTP_HOST'],
    })
    mail = t.render(Context(context))
    send_mail(subject, mail, settings.DEFAULT_FROM_EMAIL, [to])

