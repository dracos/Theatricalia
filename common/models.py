from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User

class Alert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='alerts')

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)
    
    def __unicode__(self):
        return "%s" % (self.content_object)

class AlertLocal(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(User, related_name='local_alerts')

    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = (('user', 'latitude', 'longitude'),)
    
    def __unicode__(self):
        return "%s's alert around (%s,%s)" % (self.user, self.latitude, self.longitude)

class AlertSent(models.Model):
    alert = models.ForeignKey(Alert)
    production = models.ForeignKey('productions.Production')
