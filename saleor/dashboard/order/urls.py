from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.order_list, name='orders'),
    url(r'^(?P<order_pk>\d+)/$',
        views.order_details, name='order-details'),
    url(r'^(?P<order_pk>\d+)/add-note/$',
        views.order_add_note, name='order-add-note'),
    url(r'^(?P<order_pk>\d+)/cancel/$',
        views.cancel_order, name='order-cancel'),
    url(r'^(?P<order_pk>\d+)/ship/$',
        views.ship_order, name='order-shipped'),

    url(r'^(?P<order_pk>\d+)/line/(?P<line_pk>\d+)/change/$',
        views.orderline_change_quantity, name='orderline-change-quantity'),
    url(r'^(?P<order_pk>\d+)/line/(?P<line_pk>\d+)/cancel/$',
        views.orderline_cancel, name='orderline-cancel'),
]
