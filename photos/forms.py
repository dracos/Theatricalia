from django import forms
from django.contrib.contenttypes.models import ContentType
from models import Photo

class PhotoForm(forms.ModelForm):
    content_type  = forms.CharField(widget=forms.HiddenInput)
    object_id     = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, target_object, initial=None, *args, **kwargs):
        if initial is None: initial = {}
        self.target_object = target_object
        initial.update({
            'content_type': target_object._meta,
            'object_id': target_object.pk,
        })
        super(PhotoForm, self).__init__(initial=initial, *args, **kwargs)

    class Meta:
        model = Photo
        exclude = ('is_visible',)

    def clean(self):
        self.cleaned_data['content_type'] = ContentType.objects.get_for_model(self.target_object)
        return self.cleaned_data

#    def get_photo_object(self):
#        if not self.is_valid():
#            raise ValueError("get_comment_object may only be called on valid forms")
#
#        new = Photo(**self.get_photo_create_data())
#        return new
#
#    def get_photo_create_data(self):
#        return dict(
#            content_type = ContentType.objects.get_for_model(self.target_object),
#            object_id    = self.target_object.pk,
#            title      = self.cleaned_data["title"],
#        )

