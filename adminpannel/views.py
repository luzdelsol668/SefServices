from _ast import Div

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView

from accounts.models import User
from adminpannel.forms import LoginForm, AddNewPartnerForm, AddDriverForm
from adminpannel.models import Admin
from adminpannel.forms import CategoryForm
from rides.models import CarClass, Vehicle, PartnerCompany, Driver


# Create your views here.
class LoginView(TemplateView):
    template_name = 'admin/account/login.html'

    def post(self, request, *args, **kwargs):

        if self.request.method == 'POST':

            loginform = LoginForm(self.request.POST)
            remember_me = request.POST.get('remember_me')
            next_page = request.POST.get('next_page', None)

            if loginform.is_valid():

                email = loginform.cleaned_data['email']
                admin = User.objects.filter(email=email)

                if admin.exists():

                    if authenticate(email=email, password=self.request.POST.get('password')):

                        backend = 'coreservice.AuthBackend.AdminBackend'
                        login(request, user=admin.first(), backend=backend)
                        request.session['last_backend'] = backend
                        '''
                        if user.ip_address != user_ip:
                            user.last_login = timezone.now()
                            geo_ip_data = get_client_location(user_ip=user_ip)
                            # country = str(dict(countries)[str(country)])

                            data = {
                                'country': geo_ip_data['country'],
                                'city': geo_ip_data['city'],
                                'ip': str(user_ip),
                                'date': str(timezone.now().strftime("%a, %d %b %Y %H:%S"))
                            }

                            last_ip_changed.send(sender=User, id=user.id, **data)
                            User.objects.filter(email=request.user.email).update(ip_address=user_ip) 
                        '''

                        if remember_me:
                            request.session.set_expiry(0)
                        else:
                            request.session.set_expiry(1209600)  # set to 2 weeks

                        if next_page:
                            return redirect(next_page)
                        else:
                            return redirect('admin:dashboard_screen')

                    else:

                        messages.error(request, "Les informations saisies sont incorrecte", extra_tags='login_error')
                        return redirect('admin:login_screen')

                else:
                    messages.error(request, "Les informations saisies sont incorrecte", extra_tags='login_error')

                    return redirect('admin:login_screen')

            else:

                return HttpResponse('incorrecte')


    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        if self.request.GET.get('next'):
            context['next_page'] = self.request.GET.get('next')

        context['login_form'] = LoginForm

        return context


def user_logout(request):
    last_backend = request.session.get('last_backend', None)
    logout(request)

    if last_backend == 'exhibitor.AuthBackend.UserAuthBackend':
        return redirect('exhibitor:login_exhibitor')  # Replace with your backend 1 login URL name
    elif last_backend == 'coreservice.AuthBackend.UserAuthBackend':
        return redirect('admin:login_screen')

    return redirect('exhibitor:login_exhibitor')


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/dashboards/analytic_dash.html'
    login_url = 'admin:login_screen'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class CategoriesListeView(LoginRequiredMixin, TemplateView):
    template_name = 'admin/car_categories/category_list.html'
    login_url = 'admin:login_screen'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categoryForm'] = CategoryForm
        context['categories'] = CarClass.objects.all()
        context['total_categories'] = CarClass.objects.all().count()

        if "edition" in self.request.GET and "id" in self.request.GET:

            context['edition'] = True
            context['singleCategory'] = get_object_or_404(CarClass, pk=self.request.GET['id'])
            context['categoryForm'] = CategoryForm(instance=context['singleCategory'])

        return context


class SavingCategory(LoginRequiredMixin, View):
    login_url = "admin:login_screen"

    def post(self, request, *args, **kwargs):

        savingForm = CategoryForm(request.POST, request.FILES)

        if savingForm.is_valid():
            savingForm.save()
            messages.success(request, "Category saved", extra_tags="category_saved")
            return redirect('admin:liste-des-categories')

        else:
            messages.error(request, "Error Saving Category", extra_tags="category_not_saved")
            return redirect('admin:liste-des-categories')


class UpdateCategory(LoginRequiredMixin, UpdateView):
    login_url = 'admin:login_screen'

    def post(self, request, *args, **kwargs):
        stand_type = get_object_or_404(CarClass, pk=self.kwargs.get('pk'))
        categoryForm = CategoryForm(request.POST, request.FILES, instance=stand_type)
        if categoryForm.is_valid():
            categoryForm.save()
        messages.success(self.request, f"Mise à jour effectuée", extra_tags="category_update_success")
        return redirect('admin:liste-des-categories')


class CategoryDeletion(LoginRequiredMixin, DetailView):
    login_url = 'admin:login_screen'

    def get(self, request, *args, **kwargs):
        stand_type = get_object_or_404(CarClass, pk=self.kwargs.get('pk'))
        messages.success(self.request, f"Le type {stand_type} est supprimé", extra_tags="booth_type_delete_success")
        stand_type.delete()
        return redirect('admin:liste-des-categories')


class DriversListView(LoginRequiredMixin, TemplateView):
    login_url = 'admin:login_screen'
    template_name = 'admin/chauffeurs/drivers_list.html'

    def post(self, request, *args, **kwargs):

        addDriverForm = AddDriverForm(request.POST)
        if addDriverForm.is_valid():

            user = User.objects.create(
                email=addDriverForm.cleaned_data['email'],
                last_name=addDriverForm.cleaned_data['lastname'],
                first_name=addDriverForm.cleaned_data['firstname'],
                country="FR",
                phone=addDriverForm.cleaned_data['phone'],
            )

            Driver.objects.create(
                user=user,
                partner_id=addDriverForm.cleaned_data['partner'],
            )

            return redirect('admin:liste-de-chauffeur')


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['drivers'] = Driver.objects.all()
        context['addDriverForm'] = AddDriverForm

        return context





class PartnerListView(LoginRequiredMixin, TemplateView):
    login_url = 'admin:login_screen'
    template_name = 'admin/partner/partners_list.html'

    def post(self, request, *args, **kwargs):

        partnerForm = AddNewPartnerForm(request.POST)

        if partnerForm.is_valid():
            partnerForm.save()
            return redirect('admin:liste-de-partenaires')

        if "update" in request.POST:
            partner = get_object_or_404(PartnerCompany, pk=request.POST.get('partner'))
            partnerForm = AddNewPartnerForm(request.POST, instance=partner)
            if partnerForm.is_valid():
                partnerForm.save()
                return redirect('admin:liste-de-partenaires')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['partner_list'] = PartnerCompany.objects.all().order_by('-created_at')
        context['addPartnerForm'] = AddNewPartnerForm

        if "edition" in self.request.GET and "id" in self.request.GET:

            context['edition'] = True
            context['partner'] = get_object_or_404(PartnerCompany, pk=self.request.GET['id'])
            context['addPartnerForm'] = AddNewPartnerForm(instance=context['partner'])

        return context


class DeletePartner(LoginRequiredMixin, DetailView):
    login_url = 'admin:login_screen'

    def get(self, request, *args, **kwargs):
        stand_type = get_object_or_404(PartnerCompany, pk=self.kwargs.get('pk'))
        messages.success(self.request, f"Le partenaire {stand_type} est supprimé", extra_tags="booth_type_delete_success")
        stand_type.delete()
        return redirect('admin:liste-de-partenaires')


class CarListView(LoginRequiredMixin, TemplateView):
    login_url = 'admin:login_screen'
    template_name = 'admin/cars/car_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['cars_list'] = Vehicle.objects.all()

        return context


class AddNewCarView(LoginRequiredMixin, TemplateView):
    login_url = 'admin:login_screen'
    template_name = 'admin/cars/adding_new_car.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context














