from django.urls import path
from Login.views import login,forget_password
urlpatterns = [
    path("login/", login,name="login"),
    path('forget-password/', forget_password, name='forget_password'),
]
