"""
Balises et filtres du gabarit Assurix.

Usage dans un template :  {% load assurix_tags %}
"""
from decimal import Decimal, InvalidOperation

from django import template
from django.conf import settings
from django.urls import NoReverseMatch, reverse

from .. import demo_data, navigation

register = template.Library()

NNBSP = "\u202f"   # espace fine insécable (séparateur de milliers)
NBSP = "\u00a0"


# ---------------------------------------------------------------------------
# Utilisateur : nom, initiales, rôle
# ---------------------------------------------------------------------------
@register.filter
def ax_name(user):
    """Nom complet si disponible, sinon identifiant."""
    if not getattr(user, "is_authenticated", False):
        return ""
    full = user.get_full_name().strip()
    return full or user.get_username()


@register.filter
def ax_first_name(user):
    if not getattr(user, "is_authenticated", False):
        return ""
    return (user.first_name or user.get_username()).strip()


@register.filter
def ax_initials(value):
    """Initiales d'un utilisateur Django OU d'une chaîne (ex. « Leïla Ben Salem » -> « LB »)."""
    text = ax_name(value) if hasattr(value, "get_username") else str(value or "")
    parts = [p for p in text.replace("-", " ").split() if p]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[1][0]).upper()


@register.filter
def ax_role(user):
    """
    Premier groupe Django de l'utilisateur ; sinon « Administrateur » pour le
    personnel (is_staff) ; sinon « Utilisateur ».
    """
    if not getattr(user, "is_authenticated", False):
        return ""
    cached = getattr(user, "_ax_role", None)
    if cached is not None:
        return cached
    group = user.groups.order_by("name").first()
    if group:
        role = group.name
    elif user.is_staff:
        role = "Administrateur"
    else:
        role = "Utilisateur"
    user._ax_role = role
    return role


# ---------------------------------------------------------------------------
# Navigation (sidebar + recherche rapide)
# ---------------------------------------------------------------------------
def _safe_reverse(name):
    try:
        return reverse(name)
    except NoReverseMatch:
        return "#"


@register.simple_tag(takes_context=True)
def ax_nav(context):
    """Sections de navigation avec état actif et compteurs."""
    request = context.get("request")
    current = getattr(getattr(request, "resolver_match", None), "url_name", None)
    demo = getattr(settings, "ASSURIX_DEMO_MODE", True)
    counts = demo_data.unread_counts() if demo else {"messages": 0, "notifications": 0}

    sections = []
    for section in navigation.NAV_SECTIONS:
        items = []
        for item in section["items"]:
            items.append({
                **item,
                "url": _safe_reverse(item["url_name"]),
                "active": item["url_name"] == current,
                "count": counts.get(item["key"], 0),
            })
        sections.append({"title": section["title"], "items": items})
    return sections


@register.simple_tag
def ax_search_items():
    """Liste (sérialisable en JSON) pour la recherche rapide de modules."""
    return [
        {"label": item["label"], "hint": item["hint"], "icon": item["icon"],
         "url": _safe_reverse(item["url_name"])}
        for item in navigation.all_items()
    ]


@register.simple_tag
def ax_shell():
    """Données du menu de notifications de la barre supérieure."""
    demo = getattr(settings, "ASSURIX_DEMO_MODE", True)
    if not demo:
        return {"is_demo": False, "notifications": [], "unread": 0}
    items = demo_data.notifications()
    return {
        "is_demo": True,
        "notifications": items[:5],
        "unread": sum(1 for n in items if not n["read"]),
    }


@register.filter
def ax_url(url_name):
    """{{ 'client_list'|ax_url }} -> '/clients/' (renvoie '#' si le nom est inconnu)."""
    return _safe_reverse(url_name)


# ---------------------------------------------------------------------------
# Présentation
# ---------------------------------------------------------------------------
_TONES = {
    "success": {"Actif", "Payé", "Accepté", "Acceptée", "Indemnisé", "Terminée", "Rapport remis"},
    "warning": {"À renouveler", "En attente", "En étude", "En attente de pièces", "En expertise",
                "Partiel", "En cours", "Moyenne"},
    "danger": {"Expiré", "En retard", "Refusé", "Refusée", "Haute"},
    "info": {"Déclaré", "Planifié", "Planifiée", "Nouvelle", "Non lu", "Non lue"},
}


@register.filter
def ax_tone(status):
    """Statut métier -> ton du badge (success, warning, danger, info ou vide = neutre)."""
    for tone, values in _TONES.items():
        if status in values:
            return tone
    return ""


@register.filter
def ax_money(value):
    """1240 -> « 1 240,00 DT » (espaces insécables)."""
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError):
        return "—"
    text = f"{amount:,.2f}".replace(",", NNBSP).replace(".", ",")
    return f"{text}{NBSP}DT"


@register.filter
def ax_int(value):
    """1284 -> « 1 284 » ; None -> « — »."""
    if value is None or value == "":
        return "—"
    try:
        return f"{int(value):,}".replace(",", NNBSP)
    except (ValueError, TypeError):
        return str(value)


_STEPS = {"Déclaré": 1, "En expertise": 2, "Accepté": 3, "Refusé": 3, "Indemnisé": 4, "Clos": 4}


@register.filter
def ax_step(status):
    """Statut de sinistre -> étape (1 à 4) pour le suivi visuel."""
    return _STEPS.get(status, 0)
