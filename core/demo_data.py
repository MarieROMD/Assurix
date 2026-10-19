"""
DONNÉES DE DÉMONSTRATION D'ASSURIX
==================================

Le backend n'a pas encore de modèles (Client, Contrat, Paiement, ...).
Pour que l'interface soit visible et testable, ce module fournit un jeu de
données FICTIF. Il est toujours signalé à l'écran par un bandeau
« Données de démonstration ».

Comment remplacer ces données par de vraies données
---------------------------------------------------
1. Créez vos modèles et migrations.
2. Dans core/views.py, remplacez l'appel `demo_data.xxx()` de la vue concernée
   par votre requête (ex. `Client.objects.all()`), en gardant les mêmes clés
   dans le contexte, puis passez `is_demo=False`.
3. Ou, pour tout désactiver d'un coup, ajoutez dans settings.py :
       ASSURIX_DEMO_MODE = False
   Les pages afficheront alors leurs états vides, sans aucune donnée inventée.

Aucune de ces fonctions n'écrit en base de données.
"""
from datetime import date, timedelta

from django.utils import timezone

MONTHS_FR = ["janv.", "févr.", "mars", "avr.", "mai", "juin",
             "juil.", "août", "sept.", "oct.", "nov.", "déc."]


def _d(days):
    """Date relative à aujourd'hui (négatif = passé)."""
    return date.today() + timedelta(days=days)


def _dt(minutes_ago):
    return timezone.now() - timedelta(minutes=minutes_ago)


# --------------------------------------------------------------------------
# Totaux affichés dans les indicateurs du tableau de bord (démo)
# --------------------------------------------------------------------------
def kpis():
    return {
        "clients": 1284,
        "contrats_actifs": 932,
        "demandes_en_attente": 47,
        "sinistres_a_traiter": 12,
    }


# --------------------------------------------------------------------------
# Modules
# --------------------------------------------------------------------------
def clients():
    rows = [
        ("CLI-0001", "Leïla Ben Salem", "Particulier", "Tunis", "leila.bensalem@exemple.tn", "+216 20 000 001", "Actif", 3, -820),
        ("CLI-0002", "Mehdi Karray", "Particulier", "Sfax", "mehdi.karray@exemple.tn", "+216 20 000 002", "Actif", 2, -640),
        ("CLI-0003", "Société Horizon", "Entreprise", "Sousse", "contact@horizon.exemple.tn", "+216 70 000 003", "Actif", 6, -1500),
        ("CLI-0004", "Nadia Trabelsi", "Particulier", "Ariana", "nadia.trabelsi@exemple.tn", "+216 20 000 004", "Actif", 1, -210),
        ("CLI-0005", "Atelier Médina", "Entreprise", "Tunis", "atelier@medina.exemple.tn", "+216 71 000 005", "En attente", 0, -12),
        ("CLI-0006", "Walid Jebali", "Particulier", "Nabeul", "walid.jebali@exemple.tn", "+216 20 000 006", "Actif", 2, -430),
        ("CLI-0007", "Cabinet Dhaouadi", "Entreprise", "Bizerte", "info@dhaouadi.exemple.tn", "+216 72 000 007", "Actif", 4, -980),
        ("CLI-0008", "Sonia Gharbi", "Particulier", "Monastir", "sonia.gharbi@exemple.tn", "+216 20 000 008", "Inactif", 0, -1900),
        ("CLI-0009", "Karim Mansouri", "Particulier", "Ben Arous", "karim.mansouri@exemple.tn", "+216 20 000 009", "Actif", 1, -90),
        ("CLI-0010", "Pharmacie Centrale", "Entreprise", "Tunis", "pharmacie@centrale.exemple.tn", "+216 71 000 010", "Actif", 3, -1120),
    ]
    return [
        {"ref": r[0], "name": r[1], "kind": r[2], "city": r[3], "email": r[4], "phone": r[5],
         "status": r[6], "contracts": r[7], "since": _d(r[8])}
        for r in rows
    ]


def demandes():
    rows = [
        ("DEM-0231", "Leïla Ben Salem", "Modification de garanties", "Nouvelle", -1, "Moyenne"),
        ("DEM-0230", "Atelier Médina", "Souscription", "En étude", -2, "Haute"),
        ("DEM-0229", "Walid Jebali", "Attestation d'assurance", "Acceptée", -3, "Basse"),
        ("DEM-0228", "Société Horizon", "Ajout d'un véhicule", "En attente de pièces", -5, "Moyenne"),
        ("DEM-0227", "Sonia Gharbi", "Résiliation", "En étude", -6, "Moyenne"),
        ("DEM-0226", "Karim Mansouri", "Souscription", "Nouvelle", -6, "Haute"),
        ("DEM-0225", "Cabinet Dhaouadi", "Changement d'adresse", "Acceptée", -8, "Basse"),
        ("DEM-0224", "Nadia Trabelsi", "Modification de garanties", "Refusée", -10, "Moyenne"),
    ]
    return [
        {"ref": r[0], "client": r[1], "kind": r[2], "status": r[3], "date": _d(r[4]), "priority": r[5]}
        for r in rows
    ]


def contrats():
    rows = [
        ("CTR-2026-0412", "Leïla Ben Salem", "Automobile", 200, 165, 1240, "Actif"),
        ("CTR-2026-0398", "Mehdi Karray", "Habitation", -330, 35, 680, "À renouveler"),
        ("CTR-2025-0871", "Société Horizon", "Flotte professionnelle", -380, -15, 18450, "Expiré"),
        ("CTR-2026-0405", "Nadia Trabelsi", "Santé", -90, 275, 2150, "Actif"),
        ("CTR-2026-0377", "Walid Jebali", "Automobile", -300, 65, 980, "À renouveler"),
        ("CTR-2024-0233", "Sonia Gharbi", "Habitation", -900, -60, 540, "Résilié"),
        ("CTR-2026-0420", "Cabinet Dhaouadi", "Responsabilité civile", -40, 325, 4300, "Actif"),
        ("CTR-2026-0431", "Pharmacie Centrale", "Multirisque professionnelle", -10, 355, 5200, "Actif"),
    ]
    return [
        {"ref": r[0], "client": r[1], "kind": r[2], "start": _d(r[3]), "end": _d(r[4]),
         "premium": r[5], "status": r[6], "renewal_days": r[4]}
        for r in rows
    ]


def paiements():
    rows = [
        ("PAY-8841", "Leïla Ben Salem", "CTR-2026-0412", 310, -2, "Payé", "Carte bancaire"),
        ("PAY-8840", "Cabinet Dhaouadi", "CTR-2026-0420", 1075, -4, "Payé", "Virement"),
        ("PAY-8839", "Mehdi Karray", "CTR-2026-0398", 170, -6, "En retard", "Prélèvement"),
        ("PAY-8838", "Pharmacie Centrale", "CTR-2026-0431", 1300, 5, "Planifié", "Virement"),
        ("PAY-8837", "Nadia Trabelsi", "CTR-2026-0405", 537.5, 8, "Planifié", "Prélèvement"),
        ("PAY-8836", "Société Horizon", "CTR-2025-0871", 4612.5, -20, "En retard", "Chèque"),
        ("PAY-8835", "Walid Jebali", "CTR-2026-0377", 245, -9, "Partiel", "Espèces"),
        ("PAY-8834", "Karim Mansouri", "CTR-2026-0429", 420, -12, "Payé", "Carte bancaire"),
    ]
    return [
        {"ref": r[0], "client": r[1], "contract": r[2], "amount": r[3], "date": _d(r[4]),
         "status": r[5], "method": r[6]}
        for r in rows
    ]


def sinistres():
    rows = [
        ("SIN-1187", "Leïla Ben Salem", "CTR-2026-0412", "Collision", -3, "Déclaré"),
        ("SIN-1186", "Mehdi Karray", "CTR-2026-0398", "Dégât des eaux", -5, "En expertise"),
        ("SIN-1185", "Pharmacie Centrale", "CTR-2026-0431", "Vol", -9, "En expertise"),
        ("SIN-1184", "Cabinet Dhaouadi", "CTR-2026-0420", "Incendie", -16, "Accepté"),
        ("SIN-1183", "Walid Jebali", "CTR-2026-0377", "Bris de glace", -21, "Indemnisé"),
        ("SIN-1182", "Nadia Trabelsi", "CTR-2026-0405", "Hospitalisation", -30, "Refusé"),
        ("SIN-1181", "Karim Mansouri", "CTR-2026-0429", "Collision", -41, "Clos"),
    ]
    return [
        {"ref": r[0], "client": r[1], "contract": r[2], "kind": r[3], "date": _d(r[4]), "status": r[5]}
        for r in rows
    ]


def expertises():
    rows = [
        ("EXP-0512", "SIN-1186", "Mehdi Karray", "Imed Zouari", 2, "Planifiée", 10),
        ("EXP-0511", "SIN-1185", "Pharmacie Centrale", "Rim Hammami", 0, "En cours", 55),
        ("EXP-0510", "SIN-1184", "Cabinet Dhaouadi", "Imed Zouari", -7, "Rapport remis", 90),
        ("EXP-0509", "SIN-1183", "Walid Jebali", "Anis Ferchichi", -14, "Terminée", 100),
        ("EXP-0508", "SIN-1187", "Leïla Ben Salem", "Rim Hammami", 4, "Planifiée", 10),
        ("EXP-0507", "SIN-1181", "Karim Mansouri", "Anis Ferchichi", -30, "Terminée", 100),
    ]
    return [
        {"ref": r[0], "claim": r[1], "client": r[2], "expert": r[3], "appointment": _d(r[4]),
         "status": r[5], "progress": r[6]}
        for r in rows
    ]


def messages():
    rows = [
        ("Leïla Ben Salem", "Question sur ma franchise", "Bonjour, pouvez-vous me confirmer le montant de la franchise…", 25, False),
        ("Imed Zouari", "Rapport d'expertise SIN-1184", "Le rapport est disponible, je vous l'ai déposé…", 140, False),
        ("Société Horizon", "Renouvellement de la flotte", "Nous souhaitons étudier une nouvelle proposition…", 420, False),
        ("Équipe sinistres", "Dossiers à relancer cette semaine", "Voici la liste des dossiers sans réponse depuis 7 jours…", 1300, True),
        ("Walid Jebali", "Merci pour l'indemnisation", "Je confirme la bonne réception du virement…", 2900, True),
        ("Rim Hammami", "Rendez-vous d'expertise décalé", "Le client demande de reporter au jeudi matin…", 4300, True),
        ("Nadia Trabelsi", "Pièces complémentaires", "Veuillez trouver ci-joint le certificat médical…", 5800, True),
        ("Comptabilité", "Relances de paiements en retard", "Trois paiements sont en retard de plus de 15 jours…", 8600, True),
    ]
    return [
        {"sender": r[0], "subject": r[1], "preview": r[2], "received": _dt(r[3]), "read": r[4]}
        for r in rows
    ]


def notifications():
    rows = [
        ("warning", "bi-calendar-event", "3 contrats arrivent à échéance sous 30 jours", "contrat_list", 18, False),
        ("danger", "bi-credit-card", "Paiement PAY-8839 en retard de 6 jours", "paiement_list", 95, False),
        ("info", "bi-clipboard2-check", "Expertise EXP-0512 planifiée après-demain", "expertise_list", 240, False),
        ("info", "bi-inbox", "2 nouvelles demandes reçues aujourd'hui", "demande_list", 410, False),
        ("success", "bi-check2-circle", "Sinistre SIN-1183 indemnisé", "sinistre_list", 1500, True),
        ("info", "bi-chat-left-text", "Nouveau message de Société Horizon", "message_list", 2200, True),
        ("warning", "bi-exclamation-triangle", "Sinistre SIN-1185 en expertise depuis 9 jours", "sinistre_list", 3300, True),
        ("success", "bi-person-check", "Client CLI-0009 ajouté", "client_list", 5400, True),
    ]
    return [
        {"tone": r[0], "icon": r[1], "text": r[2], "url_name": r[3], "created": _dt(r[4]), "read": r[5]}
        for r in rows
    ]


# --------------------------------------------------------------------------
# Tableau de bord
# --------------------------------------------------------------------------
def _last_months(n=12):
    today = date.today()
    out = []
    y, m = today.year, today.month
    for _ in range(n):
        out.append((y, m))
        m -= 1
        if m == 0:
            m, y = 12, y - 1
    out.reverse()
    return [MONTHS_FR[m - 1] for _, m in out]


def dashboard_charts():
    labels = _last_months(12)
    contracts = [38, 42, 40, 51, 47, 55, 60, 58, 66, 63, 71, 68]
    received = [41200, 44800, 43100, 52600, 49900, 58400, 61200, 59800, 67300, 64100, 72500, 69800]
    pending = [6200, 5400, 7100, 6800, 7600, 6100, 8200, 7400, 9100, 8300, 9800, 11200]
    claims = [("Déclaré", 5), ("En expertise", 7), ("Accepté", 18),
              ("Indemnisé", 31), ("Refusé", 4), ("Clos", 22)]
    return {
        "contracts_over_time": {"labels": labels, "values": contracts},
        "claims_by_status": {"labels": [c[0] for c in claims], "values": [c[1] for c in claims]},
        "payments": {"labels": labels, "received": received, "pending": pending,
                     "received_total": sum(received), "pending_total": pending[-1]},
    }


def priority_tasks():
    return [
        {"title": "Relancer 3 paiements en retard", "detail": "PAY-8839, PAY-8836, PAY-8835",
         "due": "Aujourd'hui", "tone": "danger", "url_name": "paiement_list"},
        {"title": "Traiter les sinistres déclarés", "detail": "SIN-1187 attend une première décision",
         "due": "Aujourd'hui", "tone": "danger", "url_name": "sinistre_list"},
        {"title": "Contacter les clients à renouveler", "detail": "CTR-2026-0398, CTR-2026-0377",
         "due": "Cette semaine", "tone": "warning", "url_name": "contrat_list"},
        {"title": "Compléter la demande DEM-0228", "detail": "Pièces manquantes côté client",
         "due": "Cette semaine", "tone": "warning", "url_name": "demande_list"},
        {"title": "Valider le rapport d'expertise EXP-0510", "detail": "Rapport remis par Imed Zouari",
         "due": "Ce mois-ci", "tone": "info", "url_name": "expertise_list"},
    ]


def recent_activity():
    return [
        {"icon": "bi-exclamation-triangle", "tone": "warning", "text": "Sinistre SIN-1187 déclaré par Leïla Ben Salem", "when": _dt(180)},
        {"icon": "bi-credit-card-2-front", "tone": "success", "text": "Paiement PAY-8841 reçu : 310,00 DT", "when": _dt(420)},
        {"icon": "bi-inbox", "tone": "info", "text": "Demande DEM-0231 reçue (modification de garanties)", "when": _dt(1500)},
        {"icon": "bi-file-earmark-text", "tone": "success", "text": "Contrat CTR-2026-0431 créé pour Pharmacie Centrale", "when": _dt(2900)},
        {"icon": "bi-clipboard2-check", "tone": "info", "text": "Expertise EXP-0510 : rapport remis", "when": _dt(4300)},
        {"icon": "bi-person-plus", "tone": "info", "text": "Nouveau client : Karim Mansouri", "when": _dt(7200)},
    ]


def unread_counts():
    return {
        "messages": sum(1 for m in messages() if not m["read"]),
        "notifications": sum(1 for n in notifications() if not n["read"]),
    }
