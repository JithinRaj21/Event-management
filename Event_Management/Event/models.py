from django.db import models
from django.contrib.auth.models import User


class Venue(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=255)
    image= models.ImageField(default='')
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    organizer = models.ForeignKey(User, on_delete=models.CASCADE)
    ticketed = models.BooleanField(default=True)
    rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return self.title


class Ticket(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f'{self.event.title} - ${self.price}'


class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    booking_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.user.username} attending {self.event.title}'


class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(default='No message provided')
    created_at = models.DateField(auto_now=True)

    def __str__(self):
        return '{}'.format(self.name)
