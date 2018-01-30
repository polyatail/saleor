from django.conf import settings
from django.contrib import auth, messages
from django.contrib.auth import views as django_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from .forms import LoginForm


def login(request):
    kwargs = {
        'template_name': 'account/login.html', 'authentication_form': LoginForm}

    if request.user.is_authenticated():
      # create the cart_token for this session if not exists
      if 'cart_token' not in request.session:
        request.session['cart_token'] = request.get_signed_cookie(COOKIE_NAME, default=None)

    return django_views.LoginView.as_view(**kwargs)(request, **kwargs)


@login_required
def logout(request):
    auth.logout(request)
    messages.success(request, ('You have been successfully logged out.'))
    return redirect(settings.LOGIN_REDIRECT_URL)


