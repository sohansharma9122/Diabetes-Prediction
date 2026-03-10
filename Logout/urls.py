from django.urls import path
from Logout.views import logout
urlpatterns = [
    path('logout/',logout, name="logout"),
]
