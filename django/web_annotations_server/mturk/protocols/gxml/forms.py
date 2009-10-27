from django import forms

from mturk import models

class UploadImageForm(forms.Form):
    submit_for_annotation = forms.BooleanField(label="Submit for annotation",initial=True,required=False)
    image_file  = forms.FileField()


class UploadImageTGZForm(forms.Form):
    submit_for_annotation = forms.BooleanField(label="Submit for annotation",initial=True,required=False)
    image_tgz_file  = forms.FileField()
