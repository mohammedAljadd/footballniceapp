from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['day', 'date', 'time', 'max_players', 'location_url']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'day': forms.Select(attrs={'class': 'form-control'}),
            'max_players': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '30'}),
            'location_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://maps.google.com/...'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget.attrs.update({'required': True})
        self.fields['time'].widget.attrs.update({'required': True})
        self.fields['day'].widget.attrs.update({'required': True})
        self.fields['max_players'].widget.attrs.update({'required': True})
        self.fields['location_url'].widget.attrs.update({'required': True})