import os
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context
from django.core.mail import send_mail
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.http import Http404
from django.db import connection
from utils import base32_to_int, MistypedIDException
from merged.models import Redirect
from people.models import Person

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
        if type == Person:
            obj = type.objects.get(id=id, deleted=False)
        else:
            obj = type.objects.get(id=id)
    except:
        content_type = ContentType.objects.get_for_model(type)
        try:
            redir = Redirect.objects.get(old_object_id=id, content_type=content_type)
            obj = redir.new_object
            mistyped = True
        except:
            raise Http404('No %s matches the given query.' % type._meta.object_name)
    if (slug is not None and obj.slug != slug) or mistyped:
        raise UnmatchingSlugException(obj)
    return obj
    
def render(request, template_name, context=None, base=None):
    if context is None: context = {}
#    context['base'] = base or 'base.html'
#    context['path'] = request.path
    context['connection'] = connection
    return render_to_response(
        template_name, context, context_instance = RequestContext(request)
    )

def send_email(request, subject, template, context, to):
    t = loader.get_template(template)
    context.update({
        'host': request.META['HTTP_HOST'],
    })
    mail = t.render(Context(context))
    send_mail(subject, mail, settings.DEFAULT_FROM_EMAIL, [to])

