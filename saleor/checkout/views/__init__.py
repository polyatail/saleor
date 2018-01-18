from django.shortcuts import redirect
from django.template.response import TemplateResponse

from .summary import summary_no_address
from .validators import validate_cart
from ..core import load_checkout
from ...registration.forms import LoginForm

@load_checkout
@validate_cart
def summary_view(request, checkout):
    """Display the correct order summary."""
    return summary_no_address(request, checkout)

@load_checkout
@validate_cart
def login(request, checkout):
    """Allow the user to log in prior to checkout."""
    if request.user.is_authenticated:
        return redirect('checkout:index')
    form = LoginForm()
    return TemplateResponse(request, 'checkout/login.html', {'form': form})
