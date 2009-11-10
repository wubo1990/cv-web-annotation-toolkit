from django import forms
from models import Challenge

class UploadSubmissionForm(forms.Form):
    method = forms.CharField(max_length=50)    
    title = forms.CharField(max_length=50)
    description = forms.CharField(max_length=500,widget=forms.Textarea)
    contact_person = forms.CharField()
    affiliation = forms.CharField()
    contributors = forms.CharField(widget=forms.Textarea)

    challenge = forms.ModelChoiceField(queryset=Challenge.objects.filter(is_open=True))
    submission_file  = forms.FileField()


