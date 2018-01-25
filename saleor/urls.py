from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.views import serve
from django.views.i18n import JavaScriptCatalog
from graphene_django.views import GraphQLView

from .cart.urls import urlpatterns as cart_urls
from .core.sitemaps import sitemaps
from .core.urls import urlpatterns as core_urls
from .dashboard.urls import urlpatterns as dashboard_urls
from .order.urls import urlpatterns as order_urls
from .product.urls import urlpatterns as product_urls
from .registration.urls import urlpatterns as registration_urls
from .search.urls import urlpatterns as search_urls

urlpatterns = [
    url(r'^', include(core_urls)),
    url(r'^account/', include(registration_urls)),
    url(r'^cart/', include((cart_urls, 'cart'), namespace='cart')),
    url(r'^dashboard/',
        include((dashboard_urls, 'dashboard'), namespace='dashboard')),
    url(r'^graphql', GraphQLView.as_view(graphiql=settings.DEBUG)),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), name='javascript-catalog'),
    url(r'^order/', include((order_urls, 'order'), namespace='order')),
    url(r'^products/',
        include((product_urls, 'product'), namespace='product')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [
        url(r'^static/(?P<path>.*)$', serve)
    ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
