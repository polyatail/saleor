from django.template.response import TemplateResponse
from django.contrib import messages
from django.utils.translation import pgettext_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from impersonate.views import impersonate as orig_impersonate

from ..dashboard.views import staff_member_required
from ..product.utils import products_with_availability, products_for_homepage
from ..userprofile.models import User


def home(request):
    if request.user.is_authenticated():
        return redirect('product:category', permanent=True, path=request.user.company.get_full_path(),
                        category_id=request.user.company.id)
    else:
      return HttpResponseRedirect("/account/login")

@staff_member_required
def styleguide(request):
    return TemplateResponse(request, 'styleguide.html')


def impersonate(request, uid):
    response = orig_impersonate(request, uid)
    if request.session.modified:
        msg = pgettext_lazy(
            'Impersonation message',
            'You are now logged as {}'.format(User.objects.get(pk=uid)))
        messages.success(request, msg)
    return response
