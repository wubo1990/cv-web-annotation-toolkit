from django import forms
from models import Challenge

class UploadSubmissionForm(forms.Form):
    method = forms.CharField(max_length=50)    
    title = forms.CharField(max_length=50)
    description = forms.CharField(max_length=500)
    challenge = forms.ModelChoiceField(queryset=Challenge.objects.filter(is_open=True))
    submission_file  = forms.FileField()
