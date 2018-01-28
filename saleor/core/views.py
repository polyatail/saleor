from django.template.response import TemplateResponse
from django.contrib import messages
from django.utils.translation import pgettext_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

from ..dashboard.views import staff_member_required
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


