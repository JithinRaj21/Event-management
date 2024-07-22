from django.urls import path
from .import views

urlpatterns = [
    path('',views.home,name='home'),
    path('<int:event_id>/', views.event_detail, name='event_detail'),
    path('event_list',views.event_list,name='event_list'),

    path('service_list',views.service_list,name='service_list'),
    path('service/<int:event_id>/', views.service_detail, name='service_detail'),

    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    path('contact',views.contact,name='contact'),
    path('message',views.contact_success,name='contact_success'),

    path('register_event/<int:event_id>/',views.register_event,name='register_event'),
    path('registration_success/<int:event_id>/', views.registration_success, name='registration_success'),



    path('services/<int:event_id>/', views.book_service, name='book_service'),

    path('organizer/register/', views.organizer_register, name='organizer_register'),
    path('organizer/login/', views.organizer_login, name='organizer_login'),
    path('organizer/dashboard/', views.organizer_dashboard, name='organizer_dashboard'),

    path('delete_event/<int:event_id>/', views.delete_event, name='delete_event'),
    path('delete_service/<int:event_id>/', views.delete_service, name='delete_service'),
    path('create_event/', views.create_event, name='create_event'),
    path('event_creation_success/',views.event_creation_success,name='event_creation_success'),

    path('edit_event/<int:event_id>/', views.edit_event, name='edit_event'),
    path('booking_details',views.booking_details,name='booking_details'),


    
    path('payment/create/<int:attendee_id>/', views.create_payment, name='create_payment'),
    path('payment/execute/', views.execute_payment, name='execute_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancelled/', views.payment_cancelled, name='payment_cancelled'),

]