from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.urls import reverse
from sorl.thumbnail import ImageField
from utils import int_to_base32


def get_upload_to(instance, filename):
    return 'photos/%s/%s/%s' % (instance.content_type, instance.object_id, filename)


class PhotoManager(models.Manager):
    def get_queryset(self):
        return super(PhotoManager, self).get_queryset().filter(is_visible=True)


class Photo(models.Model):
    is_visible = models.BooleanField(default=True)

    title = models.CharField(max_length=255, help_text='(required)')
    photo = ImageField('Photograph', upload_to=get_upload_to, max_length=255)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    author = models.CharField(max_length=255, blank=True, verbose_name='Creator of image')
    source = models.URLField(blank=True, verbose_name='Source link')
    license = models.CharField(max_length=20, blank=True, choices=(
        ('own-work', 'Own work'),
        ('permitted', 'Granted permission to upload to Theatricalia'),
        ('Freely licensed', (
            ('cc-by', 'Creative Commons Attribution'),
            ('cc-by-sa', 'Creative Commons Attribution-ShareAlike'),
            ('cc-by-nc-sa', 'Creative Commons Attribution-NonCommercial-ShareAlike'),
            ('cc-by-nc', 'Creative Commons Attribution-NonCommercial'),
            ('cc-by-nd', 'Creative Commons Attribution-NoDerivatives'),
            ('cc-by-nd-nc', 'Creative Commons Attribution-NonCommercial-NoDerivatives'),
            ('free-other', 'Other similar licence (provide source link)'),
        )),
        ('Public domain', (
            ('cc-zero', 'Public domain under CC-Zero licence'),
            ('pd-age', 'Public domain due to age'),
            ('pd-other', 'Other public domain'),
        )),
    ))

    objects = PhotoManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('photo-view', kwargs={'photo_id': int_to_base32(self.id)})

    def get_attached(self):
        return self.content_object
