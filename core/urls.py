
from django.urls import path
from django.contrib.auth.decorators import login_required

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("clients/", views.client_list, name="client_list"),
    path("demandes/", views.demande_list, name="demande_list"),
    path("contrats/", views.contrat_list, name="contrat_list"),
    path("paiements/", views.paiement_list, name="paiement_list"),
    path("sinistres/", views.sinistre_list, name="sinistre_list"),
    path("expertises/", views.expertise_list, name="expertise_list"),
    path("messages/", views.message_list, name="message_list"),
    path("notifications/", views.notification_list, name="notification_list"),
]