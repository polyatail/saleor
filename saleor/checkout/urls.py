from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.summary_view, name='index'),
    url(r'^summary/', views.summary_view, name='summary'),
    url(r'^login/', views.login, name='login')]
