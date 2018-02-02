from django.conf.urls import url, include

from . import views as core_views
from .category.urls import urlpatterns as category_urls
from .staff.urls import urlpatterns as staff_urls
from .order.urls import urlpatterns as order_urls
from .product.urls import urlpatterns as product_urls


urlpatterns = [
    url(r'^$', core_views.index, name='index'),
    url(r'^companies/', include(category_urls)),
    url(r'^orders/', include(order_urls)),
    url(r'^products/', include(product_urls)),
    url(r'^users/', include(staff_urls)),
    url(r'^style-guide/', core_views.styleguide, name='styleguide'),
]
