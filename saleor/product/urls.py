from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$',
        views.category_index, name='category'),
    url(r'(?P<slug>[a-z0-9-_]+?)-(?P<product_id>[0-9]+)/add/$',
        views.product_add_to_cart, name="add-to-cart"),
]
