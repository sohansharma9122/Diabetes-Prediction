from django.urls import path
from Home.views import home,contact,about,faq,gallary
urlpatterns = [
    path("", home,name="home"),
    path("about/", about,name="about"),
    path("faq/", faq,name="faq"),
    path("gallary/", gallary,name="gallary"),

]