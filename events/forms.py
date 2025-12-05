from django import forms
from django.utils import timezone
from .models import Event

class EventCreationForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'stream_url']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        if scheduled_date and scheduled_date < timezone.now():
            raise forms.ValidationError("La data programada no pot ser en el passat.")
        return scheduled_date

    def clean_title(self):
        title = self.cleaned_data.get('title')
        if self.user and Event.objects.filter(creator=self.user, title=title).exists():
            raise forms.ValidationError("Ja tens un esdeveniment amb aquest títol.")
        return title

    def clean_max_viewers(self):
        max_viewers = self.cleaned_data.get('max_viewers')
        if max_viewers is not None and not (1 <= max_viewers <= 1000):
            raise forms.ValidationError("El màxim d'espectadors ha d'estar entre 1 i 1000.")
        return max_viewers

class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'scheduled_date', 'thumbnail', 'max_viewers', 'tags', 'status', 'stream_url', 'duration']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M'),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'thumbnail': forms.FileInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'max_viewers': forms.NumberInput(attrs={'class': 'form-control'}),
            'tags': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'stream_url': forms.URLInput(attrs={'class': 'form-control'}),
            'duration': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'HH:MM:SS'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_status(self):
        status = self.cleaned_data.get('status')
        if self.instance.pk and self.user != self.instance.creator:
             # If the user is not the creator, they shouldn't be able to change status via this form normally,
             # but if they somehow do, we validate it.
             # However, the requirement says "Només el creador pot canviar l'estat".
             # If the field is exposed to others, we should revert it or raise error.
             # Assuming this form is only used by the creator or admins.
             # If we want to strictly enforce it here:
             if status != self.instance.status:
                 raise forms.ValidationError("Només el creador pot canviar l'estat.")
        return status

    def clean_scheduled_date(self):
        scheduled_date = self.cleaned_data.get('scheduled_date')
        # Removed strict check for live events here to allow finish+date change
        return scheduled_date

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        duration = cleaned_data.get('duration')
        scheduled_date = cleaned_data.get('scheduled_date')

        # Logic moved from clean_scheduled_date:
        # Only prevent date change if we are STARTING/STAYING live
        if self.instance.pk and self.instance.status == 'live' and status == 'live':
             if scheduled_date and scheduled_date != self.instance.scheduled_date:
                self.add_error('scheduled_date', "No es pot canviar la data si l'esdeveniment continua en directe.")

        if duration and status != 'finished':
            self.add_error('duration', "La duració només es pot establir si l'esdeveniment ha finalitzat.")
        
        return cleaned_data

class EventSearchForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cercar...'}))
    category = forms.ChoiceField(choices=[('', 'Totes')] + Event.CATEGORY_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    status = forms.ChoiceField(choices=[('', 'Tots')] + Event.STATUS_CHOICES, required=False, widget=forms.Select(attrs={'class': 'form-select'}))
