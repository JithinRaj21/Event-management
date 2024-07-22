from django import forms
from django.forms import DateInput

from .models import Event, Ticket, Venue, Contact, Attendee


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title','image', 'description', 'start_time', 'end_time', 'venue', 'ticketed', 'rate']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['event', 'price', 'quantity']


class VenueForm(forms.ModelForm):
    class Meta:
        model = Venue
        fields = ['name', 'address', 'capacity']


class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['booking_date']

        widgets = {
            'booking_date':forms.DateInput(attrs={'type': 'date'}),
        }


def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.fields['booking_date'].required = False


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your message'}),
        }
