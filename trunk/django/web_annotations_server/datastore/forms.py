from django import forms

class UploadPredictionsForm(forms.Form):
    title = forms.CharField(max_length=50)
    description = forms.CharField(max_length=500)
    category = forms.CharField(max_length=50)
    predictions_file  = forms.FileField()
