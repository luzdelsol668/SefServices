from django.urls import path, include
from unicodedata import name

from coreservice import views
from coreservice.views import *

app_name = 'core'
urlpatterns = [

    path('language/<slug:lang>/activate', views.language_activation, name='switch_language'),

    path('deconnexion', views.user_logout, name='user_logout'),

    path('', HomeView.as_view(), name='home_screen'),

    path('places/', include([

        path('search', PlacesDropDownView.as_view(), name='search_place'),

    ])),

    path('login', LoginView.as_view(), name='login_screen'),
    path('registration', SignUpView.as_view(), name='signup_screen'),
    path('field-validation', CheckExistingFields.as_view(), name='check_existing_fields'),

    path('bookings/', include([

        path('upcoming', UpcomingBookingView.as_view(), name='upcoming_bookings'),
        path('profile', CustomerProfileView.as_view(), name='customer_profile'),

    ])),
    path('account/', include([

        path('profile', CustomerProfileView.as_view(), name='customer_profile'),

        path('notification', EmailMarketingView.as_view(), name='notification'),

        path('password/', include([

            path('password-reset', AskPasswordReset.as_view(), name='ask_password_reset'),

        ])),

        path('payments', include([

            path('', PaymentMethodListView.as_view(), name='payment_information'),
            path('/card-authorization', CardAuthView.as_view(), name="card_authorization"),
            path('/save-payment-method', SavingPaymentMethodView.as_view(), name="saving_payment_method"),
            path("/card/<int:pk>/action", PaymentAction.as_view(), name="card_action"),

        ])),

    ]))

]
