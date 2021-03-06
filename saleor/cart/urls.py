from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^update/(?P<variant_id>\d+)/$', views.update, name='update-line'),
    url(r'^checkout/$', views.checkout, name='cart-checkout'),
    url(r'^userfield-update/$', views.userfield_update, name='userfield-update'),
    url(r'^summary/$', views.summary, name='cart-summary'),]
