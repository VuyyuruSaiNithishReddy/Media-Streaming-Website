from django.urls import path,include

from . import views



urlpatterns = [
    path("", views.login, name="login"),
    path("login", views.login, name="login"),
    path("register", views.register, name="register"),
    path("otp",views.otp,name='otp'),
    path("home", views.home, name="home"),
    path("model_form_upload", views.model_form_upload, name="model_form_upload"),
    path("logout", views.logout, name="logout"),
    #path("movies",views.movies,name="movies"),
    path("recommendation",views.recommendation,name="recommendation"),
    path("moviereq",views.mvoierequest,name="mreq"),
    path("dblist",views.dblist,name="dblist"),
    ]