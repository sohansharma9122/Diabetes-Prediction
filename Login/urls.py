from django.urls import path
from Login.views import login
urlpatterns = [
    path("", login,name="login")
]
