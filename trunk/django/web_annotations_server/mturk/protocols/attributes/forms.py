from django import forms

import mturk.models

class PostBoxesToAttributesForm(forms.Form):
    target_session  = forms.ModelChoiceField(queryset=mturk.models.Session.objects.filter(task_def__type__name="attributes"))
    source_sessions  = forms.ModelMultipleChoiceField(queryset=mturk.models.Session.objects.filter(task_def__type__name="gxml"))
    shuffle = forms.BooleanField(label="Shuffle",initial=True,required=True)


