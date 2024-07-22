from decimal import Decimal

import paypalrestsdk
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
import requests
from .forms import EventForm, TicketForm, VenueForm, ContactForm, AttendeeForm
from .models import Event, Ticket, Attendee, Venue

from django.http import JsonResponse


# Create your views here.
def home(request):
    ticketed_events = Event.objects.filter(ticketed=True)
    non_ticketed_events = Event.objects.filter(ticketed=False)
    return render(request, 'base.html', {
        'ticketed_events': ticketed_events,
        'non_ticketed_events': non_ticketed_events
    })


def event_list(request):
    events = Event.objects.filter(ticketed=True)
    return render(request, 'event_list.html', {'ticketed_events': events})


def service_list(request):
    events = Event.objects.filter(ticketed=False)
    return render(request, 'service_list.html', {'non_ticketed_events': events})


def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    tickets = Ticket.objects.filter(event=event) if event.ticketed else None
    return render(request, 'event_detail.html', {'event': event, 'tickets': tickets})


def service_detail(request, event_id):
    service = get_object_or_404(Event, pk=event_id, ticketed=False)
    return render(request, 'service_detail.html', {'service': service})


@login_required(login_url='/login/')
@transaction.atomic
def register_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        user = request.user
        quantity = int(request.POST.get('quantity', 1))
        ticket_id = request.POST.get('ticket_id')
        ticket = get_object_or_404(Ticket, id=ticket_id)

        if ticket.quantity >= quantity:
            ticket.quantity -= quantity
            ticket.save()

            # Store the quantity in the session
            request.session['ticket_quantity'] = quantity
            request.session['ticket_id'] = ticket.id

            attendee = Attendee.objects.create(user=user, event=event, ticket=ticket)
            return redirect(reverse('create_payment', args=[attendee.id]))
        else:
            return render(request, 'register_event.html', {
                'event': event,
                'tickets': Ticket.objects.filter(event=event),
                'error': 'Not enough tickets available.'
            })
    tickets = Ticket.objects.filter(event=event)
    return render(request, 'register_event.html', {'event': event, 'tickets': tickets})


paypalrestsdk.configure({
    'mode': settings.PAYPAL_MODE,
    'client_id': settings.PAYPAL_CLIENT_ID,
    'client_secret': settings.PAYPAL_CLIENT_SECRET,
})


def get_exchange_rate():
    url = 'https://api.exchangerate-api.com/v4/latest/INR'
    response = requests.get(url)
    data = response.json()
    return data['rates']['USD']


def create_payment(request, attendee_id):
    attendee = get_object_or_404(Attendee, id=attendee_id)
    event = attendee.event
    quantity = request.session.get('quantity', 1)
    total_amount_inr = quantity * event.rate

    exchange_rate = get_exchange_rate()
    total_amount_usd = total_amount_inr * Decimal(exchange_rate)

    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": request.build_absolute_uri(reverse('execute_payment')),
            "cancel_url": request.build_absolute_uri(reverse('payment_cancelled'))
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": event.title,
                    "sku": "item",
                    "price": f"{total_amount_usd:.2f}",
                    "currency": "USD",
                    "quantity": quantity
                }]
            },
            "amount": {
                "total": f"{total_amount_usd:.2f}",
                "currency": "USD"
            },
            "description": f"Payment for {event.title}"
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                approval_url = str(link.href)
                return redirect(approval_url)
    else:
        return render(request, 'payment_error.html', {'error': payment.error})


def execute_payment(request):
    payment_id = request.GET.get('paymentId')
    payer_id = request.GET.get('PayerID')
    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return render(request, 'payment_success.html')
    else:
        return render(request, 'payment_error.html', {'error': payment.error})



def payment_success(request):
    # Extract details from the query parameters
    transaction_id = request.GET.get('transaction_id')
    amount = request.GET.get('amount')
    event_title = request.GET.get('event_title')

    return render(request, 'payment_success.html', {
        'transaction_id': transaction_id,
        'amount': amount,
        'event_title': event_title,
    })


def payment_cancelled(request):
    return render(request, 'payment_cancelled.html')


def registration_success(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    attendee = Attendee.objects.filter(user=request.user, event=event).first()

    return render(request, 'registration_success.html', {'event': event, 'attendee': attendee})


@login_required(login_url='/login/')
def book_service(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        form = AttendeeForm(request.POST)
        if form.is_valid():
            attendee = form.save(commit=False)
            attendee.event = event
            attendee.user = request.user
            attendee.save()
            return redirect(reverse('registration_success', args=[event.id]))
    else:
        form = AttendeeForm()

    context = {
        'form': form,
        'service': event,

    }
    return render(request, 'register_service.html', context)


@login_required
def create_event(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        image = request.FILES.get('image')
        description = request.POST.get('description')
        ticketed = request.POST.get('ticketed') == 'on'
        rate = request.POST.get('rate')

        # Ensure the organizer is the logged-in user
        organizer = request.user

        # Check if venue, start_time, and end_time are provided
        if 'venue' in request.POST and 'start_time' in request.POST and 'end_time' in request.POST:
            venue_id = request.POST.get('venue')
            venue = Venue.objects.get(id=venue_id) if venue_id else None
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')

            # Create Event with venue, start_time, and end_time
            Event.objects.create(
                title=title,
                image=image,
                description=description,
                start_time=start_time,
                end_time=end_time,
                venue=venue,
                ticketed=ticketed,
                rate=rate,
                organizer=organizer
            )

        return redirect('event_creation_success')  # Replace with your redirect URL

    venues = Venue.objects.all()
    return render(request, 'create_event.html', {'venues': venues})


def event_creation_success(request):
    return render(request, 'event_creation_succes.html')


def edit_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect('organizer_dashboard')
    else:
        form = EventForm(instance=event)
    return render(request, 'edit_event.html', {'form': form})


@login_required
def create_ticket(request):
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = TicketForm()
    return render(request, 'create_ticket.html', {'form': form})


@login_required
def create_venue(request):
    if request.method == 'POST':
        form = VenueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = VenueForm()
    return render(request, 'create_venue.html', {'form': form})


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        phone_number = request.POST.get('phone_number')

        if password != confirm_password:
            return render(request, 'register.html', {'error_message': 'Passwords do not match'})

        if User.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error_message': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)

        user.save()

        auth_login(request, user)
        return redirect('login')

    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None:
            auth_login(request, user)
            return redirect('home')  # Redirect to a success page
        else:
            # Return an 'invalid login' error message.
            return render(request, 'login.html', {'error_message': 'Invalid login'})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    return render(request, 'profile.html')


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'message.html')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})


def contact_success(request):
    return render(request, 'message.html')


def organizer_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            return render(request, 'organizer_register.html', {'error_message': 'Passwords do not match'})

        if User.objects.filter(email=email).exists():
            return render(request, 'organizer_register.html', {'error_message': 'Email already exists'})

        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = True  # Mark user as staff
        user.save()

        auth_login(request, user)
        return redirect('organizer_login')

    return render(request, 'organizer_register.html')


def organizer_login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None

        if user is not None and user.is_staff:
            auth_login(request, user)
            return redirect('organizer_dashboard')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'organizer_login.html', {'error_message': 'Invalid login'})

    return render(request, 'organizer_login.html')


def is_organizer(user):
    return user.is_authenticated and user.is_staff


@login_required
def organizer_dashboard(request):
    ticketed_events = Event.objects.filter(ticketed=True)
    non_ticketed_events = Event.objects.filter(ticketed=False)
    return render(request, 'organizer_dashboard.html', {
        'ticketed_events': ticketed_events,
        'non_ticketed_events': non_ticketed_events
    })


def delete_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    event.delete()
    return redirect(reverse('organizer_dashboard'))


def delete_service(request, event_id):
    service = get_object_or_404(Event, id=event_id)
    service.delete()
    return redirect(reverse('organizer_dashboard'))


@login_required
def booking_details(request):
    # Retrieve services booked by users
    booked_services = Event.objects.filter(ticketed=False)

    context = {
        'booked_services': booked_services,
    }

    return render(request, 'booking_details.html', context)
