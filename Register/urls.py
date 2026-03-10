
from django.urls import path
from Register.views import signup
urlpatterns = [
    path('', signup , name='register'),
]
