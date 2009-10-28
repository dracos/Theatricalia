from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

class Redirect(models.Model):
    content_type = models.ForeignKey(ContentType)
    old_object_id = models.PositiveIntegerField()
    new_object_id = models.PositiveIntegerField()
    new_object = generic.GenericForeignKey('content_type', 'new_object_id')

    def __unicode__(self):
        return 'ID %s -> %s' % (self.old_object_id, self.new_object)

