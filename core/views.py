"""
Vues de l'interface Assurix.

IMPORTANT : le backend n'a pas encore de modèles. Chaque vue ci-dessous
alimente donc sa page avec les données de démonstration de core/demo_data.py
(toujours signalées par un bandeau « Données de démonstration »).

Pour brancher de vraies données, remplacez dans une vue la ligne
    rows = _rows(demo_data.contrats)
par votre requête, par exemple
    rows = Contrat.objects.select_related("client")
puis passez is_demo=False. Les gabarits n'ont pas à changer tant que les
objets exposent les mêmes attributs (ref, client, status, ...).

Si ASSURIX_DEMO_MODE = False dans settings.py, toutes les pages affichent
leurs états vides (aucune donnée inventée).
"""
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from . import demo_data


def demo_enabled():
    return getattr(settings, "ASSURIX_DEMO_MODE", True)


def _rows(factory):
    """Retourne les lignes de démonstration, ou une liste vide si le mode démo est coupé."""
    return factory() if demo_enabled() else []


def _context(key, title, subtitle, **extra):
    context = {
        "active": key,
        "page_title": title,
        "page_subtitle": subtitle,
        "is_demo": demo_enabled(),
        "breadcrumbs": [
            {"label": "Accueil", "url_name": "dashboard"},
            {"label": title},
        ],
    }
    context.update(extra)
    return context


def _count(rows, *statuses):
    return sum(1 for r in rows if r["status"] in statuses)


# --------------------------------------------------------------------------
# Tableau de bord
# --------------------------------------------------------------------------

def dashboard(request):
    demo = demo_enabled()
    kpis = demo_data.kpis() if demo else {}
    charts = demo_data.dashboard_charts() if demo else None
    context = _context(
        "dashboard",
        "Tableau de bord",
        "Vue d'ensemble de votre activité.",
        breadcrumbs=[{"label": "Accueil"}],
        kpis=kpis,
        charts=charts,
        tasks=demo_data.priority_tasks() if demo else [],
        activity=demo_data.recent_activity() if demo else [],
    )
    return render(request, "dashboard/index.html", context)


# --------------------------------------------------------------------------
# Modules métier (un par page, jamais fusionnés)
# --------------------------------------------------------------------------

def client_list(request):
    rows = _rows(demo_data.clients)
    summary = [
        {"label": "Clients affichés", "value": len(rows), "icon": "bi-people", "tone": ""},
        {"label": "Particuliers", "value": sum(1 for r in rows if r["kind"] == "Particulier"), "icon": "bi-person", "tone": "blue"},
        {"label": "Entreprises", "value": sum(1 for r in rows if r["kind"] == "Entreprise"), "icon": "bi-building", "tone": "blue"},
        {"label": "En attente de validation", "value": _count(rows, "En attente"), "icon": "bi-hourglass-split", "tone": "warning"},
    ] if rows else []
    return render(request, "clients/list.html", _context(
        "clients", "Clients", "Consultez et recherchez les fiches clients.",
        rows=rows, summary=summary,
        filters=["Actif", "En attente", "Inactif"],
    ))



def demande_list(request):
    rows = _rows(demo_data.demandes)
    summary = [
        {"label": "Nouvelles", "value": _count(rows, "Nouvelle"), "icon": "bi-inbox", "tone": "blue"},
        {"label": "En étude", "value": _count(rows, "En étude"), "icon": "bi-search", "tone": "warning"},
        {"label": "En attente de pièces", "value": _count(rows, "En attente de pièces"), "icon": "bi-paperclip", "tone": "warning"},
        {"label": "Acceptées", "value": _count(rows, "Acceptée"), "icon": "bi-check2-circle", "tone": ""},
    ] if rows else []
    return render(request, "demandes/list.html", _context(
        "demandes", "Demandes", "Suivez les demandes de vos clients, de la réception à la décision.",
        rows=rows, summary=summary,
        filters=["Nouvelle", "En étude", "En attente de pièces", "Acceptée", "Refusée"],
    ))



def contrat_list(request):
    rows = _rows(demo_data.contrats)
    summary = [
        {"label": "Actifs", "value": _count(rows, "Actif"), "icon": "bi-shield-check", "tone": ""},
        {"label": "À renouveler", "value": _count(rows, "À renouveler"), "icon": "bi-arrow-repeat", "tone": "warning"},
        {"label": "Expirés", "value": _count(rows, "Expiré"), "icon": "bi-calendar-x", "tone": "danger"},
        {"label": "Résiliés", "value": _count(rows, "Résilié"), "icon": "bi-slash-circle", "tone": "blue"},
    ] if rows else []
    return render(request, "contrats/list.html", _context(
        "contrats", "Contrats", "Références, échéances et renouvellements de vos contrats.",
        rows=rows, summary=summary,
        filters=["Actif", "À renouveler", "Expiré", "Résilié"],
    ))



def paiement_list(request):
    rows = _rows(demo_data.paiements)
    def total(*statuses):
        return sum(r["amount"] for r in rows if r["status"] in statuses)
    summary = [
        {"label": "Encaissé", "value": total("Payé"), "money": True, "icon": "bi-cash-stack", "tone": ""},
        {"label": "À venir", "value": total("Planifié"), "money": True, "icon": "bi-calendar-event", "tone": "blue"},
        {"label": "En retard", "value": total("En retard"), "money": True, "icon": "bi-exclamation-circle", "tone": "danger"},
        {"label": "Partiels", "value": total("Partiel"), "money": True, "icon": "bi-pie-chart", "tone": "warning"},
    ] if rows else []
    return render(request, "paiements/list.html", _context(
        "paiements", "Paiements", "Primes encaissées, échéances à venir et retards.",
        rows=rows, summary=summary,
        filters=["Payé", "Planifié", "En retard", "Partiel"],
    ))



def sinistre_list(request):
    rows = _rows(demo_data.sinistres)
    summary = [
        {"label": "Déclarés", "value": _count(rows, "Déclaré"), "icon": "bi-flag", "tone": "blue"},
        {"label": "En expertise", "value": _count(rows, "En expertise"), "icon": "bi-clipboard2-check", "tone": "warning"},
        {"label": "Acceptés ou indemnisés", "value": _count(rows, "Accepté", "Indemnisé"), "icon": "bi-check2-circle", "tone": ""},
        {"label": "Refusés", "value": _count(rows, "Refusé"), "icon": "bi-x-circle", "tone": "danger"},
    ] if rows else []
    return render(request, "sinistres/list.html", _context(
        "sinistres", "Sinistres", "Déclarations de sinistres et suivi de leur traitement.",
        rows=rows, summary=summary,
        filters=["Déclaré", "En expertise", "Accepté", "Indemnisé", "Refusé", "Clos"],
    ))



def expertise_list(request):
    rows = _rows(demo_data.expertises)
    summary = [
        {"label": "Planifiées", "value": _count(rows, "Planifiée"), "icon": "bi-calendar-event", "tone": "blue"},
        {"label": "En cours", "value": _count(rows, "En cours"), "icon": "bi-activity", "tone": "warning"},
        {"label": "Rapports remis", "value": _count(rows, "Rapport remis"), "icon": "bi-file-earmark-check", "tone": ""},
        {"label": "Terminées", "value": _count(rows, "Terminée"), "icon": "bi-check2-all", "tone": ""},
    ] if rows else []
    return render(request, "expertises/list.html", _context(
        "expertises", "Expertises", "Affectations, rendez-vous et avancement des expertises.",
        rows=rows, summary=summary,
        filters=["Planifiée", "En cours", "Rapport remis", "Terminée"],
    ))



def message_list(request):
    rows = _rows(demo_data.messages)
    unread = sum(1 for r in rows if not r["read"])
    return render(request, "messages/list.html", _context(
        "messages", "Messages", "Échanges avec vos clients et votre équipe.",
        rows=rows, unread=unread, filters=["Non lu", "Lu"],
    ))



def notification_list(request):
    rows = _rows(demo_data.notifications)
    unread = sum(1 for r in rows if not r["read"])
    return render(request, "notifications/list.html", _context(
        "notifications", "Notifications", "Alertes, rappels et événements à suivre.",
        rows=rows, unread=unread, filters=["Non lue", "Lue"],
    ))
