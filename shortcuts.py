import os
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader, Context
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.db import connection
from utils import base32_to_int, MistypedIDException

class UnmatchingSlugException(Exception):
    pass

def check_url(type, id, slug):
    mistyped = False
    try:
        id = base32_to_int(id)
    except MistypedIDException, e:
        mistyped = True
        id = e.args[0]
    except:
        raise Http404('Could not match id %s' % id)
    obj = get_object_or_404(type, id=id)
    if obj.slug != slug or mistyped:
        raise UnmatchingSlugException(obj)
    return obj
    
def render(request, template_name, context={}, base=None):
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

