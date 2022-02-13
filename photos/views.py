from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.core.exceptions import ObjectDoesNotExist
from django.apps import apps
from utils import base32_to_int
from django.contrib.auth.decorators import login_required
from django.utils.html import escape
from .models import Photo
from .forms import PhotoForm
from productions.models import Production
from plays.models import Play
from places.models import Place
from people.models import Person


@login_required
def take_photo(request):
    if settings.READ_ONLY:
        return HttpResponseRedirect('/read-only')

    data = request.POST.copy()
    if not request.user.is_authenticated:
        return HttpResponseBadRequest('Only signed in users can upload photographs.')

    ctype = data.get("content_type")
    object_id = data.get("object_id")
    if ctype is None or object_id is None:
        return HttpResponseBadRequest("Missing content_type or object_id field.")
    try:
        model = apps.get_model(ctype)
        target = model._default_manager.get(id=object_id)
    except TypeError:
        return HttpResponseBadRequest("Invalid content_type value: %r" % escape(ctype))
    except AttributeError:
        return HttpResponseBadRequest("The given content-type %r does not resolve to a valid model." % escape(ctype))
    except ObjectDoesNotExist:
        return HttpResponseBadRequest("No object matching content-type %r and object PK %r exists." % (
            escape(ctype), escape(object_id)))

    form = PhotoForm(target, data=data, files=request.FILES)

    if not form.is_valid():
        template_list = [
            "photos/preview.html"
            # "comments/%s_%s_preview.html" % tuple(str(model._meta).split(".")),
            # "comments/%s_preview.html" % model._meta.app_label,
        ]
        return render(request, template_list, {"form": form})

    form.save()
    # photo = form.get_photo_object()
    # photo.save()

    next = data.get("next", '/')
    return HttpResponseRedirect(next)


def photo_taken(request):
    pass


def view(request, photo_id):
    photo_id = base32_to_int(photo_id)
    photo = get_object_or_404(Photo, id=photo_id)

    next_photo = Photo.objects.filter(id__gt=photo.id)
    if next_photo:
        next_photo = next_photo[0]
    previous_photo = Photo.objects.filter(id__lt=photo.id).order_by('-id')
    if previous_photo:
        previous_photo = previous_photo[0]

    attached_title = 'Unknown'
    if isinstance(photo.content_object, Production):
        attached_title = photo.content_object.play.get_title_display()
    elif isinstance(photo.content_object, Play):
        attached_title = photo.content_object.get_title_display()
    elif isinstance(photo.content_object, Place):
        attached_title = str(photo.content_object)
    elif isinstance(photo.content_object, Person):
        attached_title = str(photo.content_object)

    return render(request, 'photos/view.html', {
        'photo': photo,
        'next_photo': next_photo,
        'previous_photo': previous_photo,
        'attached_title': attached_title,
    })
