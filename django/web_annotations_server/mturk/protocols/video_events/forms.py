from django import forms

from mturk import models

class UploadVideoForm(forms.Form):
    submit_for_annotation = forms.BooleanField(label="Submit for annotation",initial=True,required=False)
    video_file  = forms.FileField()
