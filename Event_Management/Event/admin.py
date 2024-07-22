from django.contrib import admin

from .models import Venue, Event, Ticket, Attendee, Contact

# Register your models here.
admin.site.register(Venue)
admin.site.register(Event)
admin.site.register(Ticket)
admin.site.register(Attendee)


class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')


admin.site.register(Contact, ContactAdmin)