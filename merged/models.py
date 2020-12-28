from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

class Redirect(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    old_object_id = models.PositiveIntegerField()
    new_object_id = models.PositiveIntegerField()
    new_object = GenericForeignKey('content_type', 'new_object_id')

    def __str__(self):
        return 'ID %s -> %s' % (self.old_object_id, self.new_object)

