from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from utils import int_to_base32


class Redirect(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    old_object_id = models.PositiveIntegerField()
    new_object_id = models.PositiveIntegerField()
    new_object = GenericForeignKey('content_type', 'new_object_id')
    approved = models.BooleanField(default=False)

    def __str__(self):
        return 'ID %s -> %s' % (self.old_object_id, self.new_object)

    def old_base32(self):
        return int_to_base32(self.old_object_id)

    def new_base32(self):
        return int_to_base32(self.new_object_id)
