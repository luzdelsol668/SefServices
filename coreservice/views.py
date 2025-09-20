from datetime import datetime, timedelta
from decimal import Decimal
import json
import requests as makeRequests
import stripe
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import Permission
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.paginator import Paginator
from django.db.models import Sum, Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.utils import timezone, translation
from django.utils.decorators import method_decorator
from django.utils.html import format_html
from django.utils.text import Truncator
from django.utils.translation import activate
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, DetailView
from django.utils.translation import gettext_lazy as _
from accounts.models import Customer, PaymentMethod
from coreservice.forms import LoginForm, RegistrationForm, CustomerProfileForm, EmailMarketingForm
from coreservice.helpers import StripeManager
from sefservices import settings as env_variable


def language_activation(request, lang):
    language = lang
    translation.activate(language)
    activate(language)
    request.LANGUAGE_CODE = lang
    next_page = request.GET.get('next')[3:]
    return redirect('/' + lang + next_page)


def user_logout(request):
    last_backend = request.session.get('last_backend', None)
    logout(request)

    if last_backend == 'accounts.AuthBackend.UserAuthBackend':
        return redirect('core:home_screen')  # Replace with your backend 1 login URL name
    elif last_backend == 'coreservice.AuthBackend.UserAuthBackend':
        return redirect('core:home_screen')

    return redirect('core:home_screen')


class HomeView(TemplateView):
    template_name = 'homepage/index.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        context['map_api_key'] = env_variable.GOOGLE_MAP_API_KEY
        context['language'] = self.request.LANGUAGE_CODE
        context['frHours'] = range(0, 24)

        return context


class PlacesDropDownView(View):
    #login_url = 'core:login_screen'

    def get(self, request, *args, **kwargs):
        query = request.GET.get("search_input")
        endpoint = "https://places.googleapis.com/v1/places:autocomplete"
        params = {
            "input": query,
            "languageCode": f"{request.LANGUAGE_CODE}",
        }
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": f"{env_variable.GOOGLE_MAP_API_KEY}",
            "X-Goog-FieldMask": "suggestions.placePrediction.placeId,suggestions.placePrediction.types,suggestions.placePrediction.structuredFormat.mainText.text,suggestions.placePrediction.structuredFormat.secondaryText.text"
        }
        result = makeRequests.post(endpoint, json=params, headers=headers).json()['suggestions']
        data = []

        for i in range(len(result)):

            print(result[i]['placePrediction']["types"])
            data.append({
                "placeId": result[i]['placePrediction']['placeId'],
                "types": result[i]['placePrediction']["types"],
                "mainText": result[i]['placePrediction']['structuredFormat']['mainText']['text'],
                "secondaryText": result[i]['placePrediction']['structuredFormat']['secondaryText']['text'],

            })
        #return JsonResponse(data, safe=False)
        return render(request, 'homepage/partials/partial_places_list.html', {"places": data})


class LoginView(TemplateView):
    template_name = 'accounts/login.html'

    def post(self, request, *args, **kwargs):

        if self.request.method == "POST":

            loginform = LoginForm(request.POST)

            if loginform.is_valid():

                email = str(loginform.cleaned_data['email']).lower()
                password = loginform.cleaned_data['password']

                next_page = request.POST.get('next_page', None)

                if Customer.objects.filter(email=email).exists():

                    customer = get_object_or_404(Customer, email=email)

                    if authenticate(email=email, password=password):

                        backend = 'accounts.AuthBackend.UserAuthBackend'
                        login(request, user=customer, backend=backend)
                        request.session['last_backend'] = backend

                        if next_page:
                            return redirect(next_page)
                        else:
                            return redirect('core:home_screen')

                    else:
                        messages.error(request, 'Email ou password incorrect')
                        return redirect('core:login_screen')

                else:
                    messages.error(request, 'Email ou password incorrect')
                    return redirect('core:login_screen')

            else:
                messages.error(request, 'Email ou password incorrect')
                return redirect('core:login_screen')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['loginForm'] = LoginForm()
        if "next" in self.request.GET:
            context['next_page'] = self.request.GET["next"]

        return context


class SignUpView(TemplateView):
    template_name = 'accounts/signup.html'

    def post(self, request, *args, **kwargs):
        signupForm = RegistrationForm(request.POST)

        phone = request.POST.get('phone_full')
        country_iso = request.POST.get('country_code')
        next_page = request.GET.get('next', None)

        if signupForm.is_valid():
            customer = signupForm.save(commit=False)
            customer.phone = phone
            customer.country = country_iso
            customer.set_password(signupForm.cleaned_data['password'])
            customer.save()  # I'm saving a new Customer.

            login(request, user=customer, backend='accounts.AuthBackend.UserAuthBackend')

            if next_page and not None:
                return redirect(next_page)

            return redirect('core:home_screen')

        else:
            return redirect('core:signup_screen')

    def get_context_data(self, **kwargs):
        context = super().get_context_data()

        context['SignupForm'] = RegistrationForm()

        return context


class CheckExistingFields(TemplateView):

    def get(self, request, *args, **kwargs):

        field = request.GET.get('field')
        value = request.GET.get('value')
        valid = True

        if field == 'email':
            if Customer.objects.filter(email=value).exists():
                valid = False
        elif field == 'phone':
            if Customer.objects.filter(phone=value[1:]).exists():
                valid = False

        return JsonResponse({'valid': valid})


class UpcomingBookingView(LoginRequiredMixin, TemplateView):
    login_url = 'core:login_screen'
    template_name = 'pages/bookings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class CustomerProfileView(LoginRequiredMixin, TemplateView):
    login_url = 'core:login_screen'
    template_name = 'pages/profile.html'

    def post(self, request, *args, **kwargs):

        if Customer.objects.exclude(email=request.user.email).filter(email=request.POST['email']).exists():

            messages.error(request, _("Error occurred"), "profile_update_error")
            return redirect('core:customer_profile')

        else:

            customer = get_object_or_404(Customer, email=request.user.email)
            profileForm = CustomerProfileForm(request.POST, instance=customer)

            if profileForm.is_valid():
                profileForm.save()
                messages.success(request, _('Your profile has been updated'), "profile_update_success")
                return redirect('core:customer_profile')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer = get_object_or_404(Customer, email=self.request.user.email)
        context['profileForm'] = CustomerProfileForm(instance=customer)

        return context


class EmailMarketingView(LoginRequiredMixin, TemplateView):
    login_url = 'core:login_screen'
    template_name = 'pages/email_and_notif.html'

    def post(self, request, *args, **kwargs):
        customer = get_object_or_404(Customer, email=request.user.email)
        notifForm = EmailMarketingForm(request.POST, instance=customer)

        if notifForm.is_valid():
            notifForm.save()
            messages.success(request, _('Setting updated'), "notif_update_success")
            return redirect('core:notification')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer = get_object_or_404(Customer, email=self.request.user.email)
        context['notifForm'] = EmailMarketingForm(instance=customer)

        return context


class AskPasswordReset(View):

    def get(self, request, *args, **kwargs):

        email = request.GET.get('email')

        customer = Customer.objects.filter(email=email)

        if customer.exists():
            # Task to send reset link
            return JsonResponse({
                "status": "success",
                "message": _("Password reset email sent, please check your inbox.")
            })
        else:
            return JsonResponse({
                'status': 'fail'
            })


class PaymentMethodListView(LoginRequiredMixin, TemplateView):
    login_url = 'core:login_screen'
    template_name = 'pages/payment_information.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        customer = get_object_or_404(Customer, email=self.request.user.email)
        context['STRIPE_PUBLIC_KEY'] = env_variable.STRIPE_PUBLIC_KEY

        context['payment_methods'] = customer.payment_methods.all().order_by('-is_default', '-created_at')

        return context


class CardAuthView(LoginRequiredMixin, View):
    login_url = 'core:login_screen'

    def get(self, request, *args, **kwargs):
        payment_manager = StripeManager()
        user = get_object_or_404(Customer, email=self.request.user.email)
        payment_manager.create_stripe_customer(user=user)
        setup_intent = payment_manager.create_card_intent(user=user)

        return JsonResponse({"status": "success", "client_secret": f"{setup_intent.client_secret}"})


@method_decorator(csrf_exempt, name='dispatch')
class SavingPaymentMethodView(LoginRequiredMixin, View):
    login_url = 'core:login_screen'

    def post(self, request, *args, **kwargs):

        payment_method_id = request.POST.get('payment_method_id')
        status = request.POST.get('status')

        if status == "succeeded":
            payment_manager = StripeManager()
            user = get_object_or_404(Customer, email=self.request.user.email)
            payment_manager.add_payment_method(user=user, payment_method_id=payment_method_id)
            return JsonResponse({"status": "success", "message": _("Card added successfully.")})
        else:
            return JsonResponse({"status": "error"})


class PaymentAction(LoginRequiredMixin, DetailView):
    login_url = 'core:login_screen'
    model = PaymentMethod

    def get(self, request, *args, **kwargs):

        action = request.GET.get('action')

        if action == 'make_default':
            payment_manager = StripeManager()
            user = get_object_or_404(Customer, email=self.request.user.email)
            payment_manager.set_default_payment_method(user=user, payment_method_id=self.get_object().payment_method_id)
            return redirect(reverse('core:payment_information'))

        elif action == 'remove_card':
            payment_manager = StripeManager()
            user = get_object_or_404(Customer, email=self.request.user.email)
            payment_manager.remove_payment_method(user=user, payment_method_id=self.get_object().payment_method_id)
            return redirect(reverse('core:payment_information'))

        return None




















