from django.conf.urls import url

from ..core import TOKEN_PATTERN
from . import views


urlpatterns = [
    url(r'^%s/$' % (TOKEN_PATTERN,), views.details, name='details'),
    url(r'^%s/confirmation/$' % (TOKEN_PATTERN,),
        views.confirmation, name='confirmation'),
]
