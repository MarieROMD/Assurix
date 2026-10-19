# Assurix : interface complète (frontend)

Ce dossier se **superpose** à votre projet existant (même arborescence). Aucun nouveau projet Django n'est créé.

## 1. Installation

1. Sauvegardez votre projet (ou faites un `git commit`).
2. Copiez le contenu de ce dossier à la racine de votre projet (là où se trouve `manage.py`), en acceptant le remplacement de :
   - `templates/base.html` (remplacé par la base autonome Assurix)
   - `assurix/settings.py` (3 ajouts, voir §4)
   - `assurix/urls.py` (routes de connexion/déconnexion + inclusion de `core.urls`)
3. Lancez :
   ```bash
   python manage.py check
   python manage.py runserver
   ```
4. Ouvrez http://127.0.0.1:8000/ : vous êtes redirigé vers `/connexion/`. Utilisez un utilisateur existant (ou `python manage.py createsuperuser`).

> `staticfiles/` n'a pas besoin d'être régénéré en développement (DEBUG=True sert `static/`). En production : `python manage.py collectstatic`.

## 2. Contenu

| Élément | Chemin |
|---|---|
| Application `core` (vues, URLs, navigation, balises, données de démo) | `core/` |
| Gabarit de base, sidebar, topbar, composants | `templates/base.html`, `templates/components/` |
| Connexion | `templates/registration/login.html` |
| Tableau de bord + 8 modules (un dossier chacun) | `templates/dashboard/`, `clients/`, `demandes/`, `contrats/`, `paiements/`, `sinistres/`, `expertises/`, `messages/`, `notifications/` |
| Design system et mise en page | `static/css/assurix-*.css` |
| JavaScript | `static/js/assurix-app.js`, `assurix-dashboard.js`, `assurix-theme.js` |
| Logos SVG, polices, Bootstrap 5.3.8, Bootstrap Icons, Chart.js 4.4.9 | `static/img/`, `static/fonts/`, `static/vendor/` |
| Aperçu autonome du design system | `static/design-preview.html` |

Bootstrap et Bootstrap Icons sont chargés **une seule fois**. AdminLTE n'est plus chargé par `base.html` (le paquet reste installé, rien n'est supprimé).

## 3. Mode démonstration (important)

Le backend n'a pas encore de modèles. Chaque page affiche donc des données **fictives** (`core/demo_data.py`), toujours signalées par le bandeau « Données de démonstration ».

- Pour tout désactiver : `ASSURIX_DEMO_MODE = False` dans `settings.py`. Les pages affichent alors des états vides, sans aucune donnée inventée.
- Pour brancher de vraies données : dans `core/views.py`, remplacez la source de la vue concernée (ex. `rows = _rows(demo_data.contrats)` par `rows = Contrat.objects...`). Les gabarits lisent des attributs simples (`ref`, `client`, `status`, `date`...). Voir l'en-tête de `core/views.py`.

## 4. Modifications de `settings.py`

- `INSTALLED_APPS` : ajout de `'core'`.
- Nouvelle section : `LOGIN_URL = 'login'`, `LOGIN_REDIRECT_URL = 'dashboard'`, `LOGOUT_REDIRECT_URL = 'login'`, `ASSURIX_DEMO_MODE = True`.

Rien d'autre n'a été modifié (modèles, migrations, authentification, AdminLTE).

## 5. Authentification

Connexion et déconnexion utilisent `LoginView` et `LogoutView` de Django. La déconnexion se fait par **POST** (formulaire avec jeton CSRF), comme l'exige Django. Toutes les pages sont protégées par `@login_required`. Le champ de connexion est « Nom d'utilisateur » (modèle `User` par défaut).

Rôle affiché : premier groupe de l'utilisateur ; sinon « Administrateur » (staff) ; sinon « Utilisateur ».

## 6. Limites connues (volontaires et documentées à l'écran)

- Création, modification et suppression : les boutons ouvrent une fenêtre « Action indisponible » qui explique quel modèle manque. Aucun succès n'est simulé.
- Le formulaire « Nouveau client » montre la disposition prévue, avec l'enregistrement désactivé.
- La recherche de la barre supérieure navigue entre les **modules** (raccourcis `/` ou Ctrl/Cmd+K) ; elle ne cherche pas dans des données.
- Les filtres de tableaux agissent sur les lignes affichées (côté navigateur). Avec de vraies données volumineuses, prévoyez filtrage et pagination côté serveur.
- « Mon profil » est affiché comme bientôt disponible (aucune page de profil n'existe).
- Notifications et messages : l'état lu/non lu est affiché mais ne peut pas être modifié.
- Le fichier `templates/dashboard.html` d'origine n'est plus utilisé (remplacé par `templates/dashboard/index.html`). Vous pouvez le supprimer quand vous le souhaitez.

## 7. Vérifications effectuées (hors de votre machine)

Python 3.12 + Django 6.1.2 : `manage.py check` sans erreur, 9 pages en 200 une fois connecté et 302 vers la connexion sinon, mauvaise connexion refusée avec message, déconnexion en POST. Navigateur Chromium : aucune erreur console ni ressource manquante, aucun débordement horizontal à 1440, 1024, 768 et 390 px, thème sombre, graphiques, menu mobile, repli de la sidebar, filtres, recherche rapide et panneau client testés. Ce n'est pas un test sur votre environnement : lancez `python manage.py check` et parcourez les pages.
