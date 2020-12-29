from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey


class Alert(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='alerts', on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        unique_together = (('user', 'content_type', 'object_id'),)

    def __str__(self):
        return "%s" % (self.content_object)


class AlertLocal(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    enabled = models.BooleanField(default=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='local_alerts', on_delete=models.CASCADE)

    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        unique_together = (('user', 'latitude', 'longitude'),)

    def __str__(self):
        return "%s's alert around (%s,%s)" % (self.user, self.latitude, self.longitude)


class AlertSent(models.Model):
    alert = models.ForeignKey(Alert, on_delete=models.CASCADE)
    production = models.ForeignKey('productions.Production', on_delete=models.CASCADE)


class Prelaunch(models.Model):
    email = models.EmailField()
    created = models.DateTimeField(auto_now_add=True)
