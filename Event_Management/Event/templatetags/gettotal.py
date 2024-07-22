from django import template

from Event.models import Ticket

register = template.Library()


@register.simple_tag(name='gettotal')
def gettotal(event):
    total = 0
    tickets = Ticket.objects.filter(event=event)
    for ticket in tickets:
        total += ticket.price * ticket.quantity
    return total
