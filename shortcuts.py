import os
from django.shortcuts import render_to_response
from django.template import RequestContext, loader, Context
from django.core.mail import send_mail
from django.db import connection

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
	send_mail(subject, mail, 'Matthew Somerville <matthew@theatricalia.com>', [to])

