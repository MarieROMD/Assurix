"""
Navigation de l'application Assurix.

Une seule source de vérité pour :
  - la barre latérale (sidebar),
  - la recherche rapide de la barre supérieure,
  - les fils d'Ariane.

Chaque entrée référence un NOM D'URL réel défini dans core/urls.py.
Les neuf modules métier restent séparés.
"""

NAV_SECTIONS = [
    {
        "title": "Pilotage",
        "items": [
            {"key": "dashboard", "label": "Tableau de bord", "icon": "bi-grid-1x2",
             "url_name": "dashboard", "hint": "KPI, graphiques, activité récente"},
        ],
    },
    {
        "title": "Clientèle",
        "items": [
            {"key": "clients", "label": "Clients", "icon": "bi-people",
             "url_name": "client_list", "hint": "Fiches et coordonnées des clients"},
            {"key": "demandes", "label": "Demandes", "icon": "bi-inbox",
             "url_name": "demande_list", "hint": "Souscriptions, modifications, résiliations"},
            {"key": "contrats", "label": "Contrats", "icon": "bi-file-earmark-text",
             "url_name": "contrat_list", "hint": "Contrats, échéances, renouvellements"},
            {"key": "paiements", "label": "Paiements", "icon": "bi-credit-card-2-front",
             "url_name": "paiement_list", "hint": "Primes, encaissements, relances"},
        ],
    },
    {
        "title": "Sinistres",
        "items": [
            {"key": "sinistres", "label": "Sinistres", "icon": "bi-exclamation-triangle",
             "url_name": "sinistre_list", "hint": "Déclarations et suivi des sinistres"},
            {"key": "expertises", "label": "Expertises", "icon": "bi-clipboard2-check",
             "url_name": "expertise_list", "hint": "Experts, rendez-vous, avancement"},
        ],
    },
    {
        "title": "Communication",
        "items": [
            {"key": "messages", "label": "Messages", "icon": "bi-chat-left-text",
             "url_name": "message_list", "hint": "Échanges avec les clients et l'équipe"},
            {"key": "notifications", "label": "Notifications", "icon": "bi-bell",
             "url_name": "notification_list", "hint": "Alertes et rappels"},
        ],
    },
]


def all_items():
    for section in NAV_SECTIONS:
        for item in section["items"]:
            yield item


def get_item(key):
    for item in all_items():
        if item["key"] == key:
            return item
    return None
