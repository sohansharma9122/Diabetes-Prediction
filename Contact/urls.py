from django.urls import path
from Contact.views import contact
urlpatterns = [
    path('',contact,name='contact'),
]
