from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class Alert(models.Model):
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
    
    def __unicode__(self):
        return "%s's alert for %s" % (self.user, self.content_object)

class AlertLocal(models.Model):
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User)

    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = (('user', 'latitude', 'longitude'),)
    
    def __unicode__(self):
        return "%s's alert around (%s,%s)" % (self.user, self.latitude, self.longitude)

