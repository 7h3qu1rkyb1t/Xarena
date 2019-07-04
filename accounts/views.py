from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.contrib.auth import login, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.contrib.auth.models import User
from django.http import HttpResponse


def target(request):
    if request.user.is_authenticated:
        return redirect("profile")
    else:
        return redirect("login")


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            print("\n\n")
            print(user.username)
            print("\n\n")
            current_site = get_current_site(request)
            mail_subject = "Activate your account."
            message = render_to_string('accounts/acc_activate_email.html',
                                       {
                                           'user':user,
                                           'domain': current_site.domain,
                                           'uid' : urlsafe_base64_encode(force_bytes(user.pk)),
                                           'token' : account_activation_token.make_token(user)
                                       })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return render(request, "accounts/verify_email.html", )
         #   username = form.cleaned_data.get("username")
         #   messages.success(request, f"Account created for {username}. Login using that Credentials.")
          #  return redirect("login")
    else:
        form = UserRegisterForm()
    context = {
        "form" : form
    }
    return render(request, 'accounts/register.html', context )


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active =True
        user.profile.email_confirmed = True
        user.save()
        login(request, user)
        messages.success(request, f"{user.username} Your account has been activated. Login with Your credentials")
        return redirect("profile")
    else:
        return HttpResponse('Activation link is invalid!')



@login_required
def profile(request):
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f" Your account has been modified.")
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    context = {
        "u_form":u_form,
        "p_form":p_form
    }
    return render(request, "accounts/profile.html", context)