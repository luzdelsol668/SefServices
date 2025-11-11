

from django.urls import path, include

from adminpannel import views
from adminpannel.views import *


app_name = 'admin'
urlpatterns = [

    path('', LoginView.as_view(), name='login_screen'),

    path('deconnexion', views.user_logout, name='deconnexion_screen'),

    path('dashboard', DashboardView.as_view(), name='dashboard_screen'),

    path('categories/', include([

        path('liste-des-categories', CategoriesListeView.as_view(), name='liste-des-categories'),
        path('add-new-category', SavingCategory.as_view(), name='add-new-category'),
        path('<int:pk>/update', UpdateCategory.as_view(), name='update-category'),
        path('<int:pk>/delete', CategoryDeletion.as_view(), name='delete-category'),

    ])),

    path('chauffeurs/', include([

        path('liste-de-chauffeur', DriversListView.as_view(), name='liste-de-chauffeur'),

    ])),

    path('partenaires/', include([

        path('liste-de-partenaires', PartnerListView.as_view(), name='liste-de-partenaires'),
        path('<int:pk>/delete', DeletePartner.as_view(), name='delete-partner'),

    ])),


    path('voitures/', include([

        path('liste-de-voitures', CarListView.as_view(), name='liste_de_voitures'),
        path('add-new-car', AddNewCarView.as_view(), name='add-new-car'),


    ])),

]
