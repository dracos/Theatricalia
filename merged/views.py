# Create your views here.
from django.http import Http404, HttpResponseRedirect
from django.core.mail import mail_admins

from shortcuts import render, check_url
from places.models import Place
from people.models import Person
from productions.models import ProductionCompany
from plays.models import Play
from utils import int_to_base32

type_dict = {
    'play': Play,
    'place': Place,
    'person': Person,
    'company': ProductionCompany,
}

def merge(request, url):
    try:
        type, id, slug = url.split('/', 2)
    except ValueError:
        raise Http404

    if type in type_dict:
        obj_type = type_dict[type]
    else:
        raise Http404

    try:
        object = check_url(obj_type, id, slug)
    except:
        raise Http404

    if request.POST.get('stop'):
        if 'merging_' + type in request.session:
            del request.session['merging_' + type]
        if request.user.is_authenticated():
            request.user.message_set.create(message=u"We have forgotten your search for a duplicate.")
        return HttpResponseRedirect(object.get_absolute_url())

    if request.POST.get('dupe') and request.session.get('merging_' + type):
        # Send email
        other = request.session['merging_' + type]
        mail_admins('Merge request', '%s\nand\n%s\n\n%s : http://theatricalia.com%s\n%s : http://theatricalia.com%s\n\nATB,\nMatthew' % (other, object, int_to_base32(other.id), other.get_absolute_url(), int_to_base32(object.id), object.get_absolute_url()), fail_silently=True)
        del request.session['merging_' + type]
        return render(request, 'merged/thanks.html', {
            'object': object,
            'other': other,
        })

    request.session['merging_' + type] = object

    return render(request, 'merged/start.html', {
        'object': object,
    })

