# wagtail-simple-forum

**Ajoute un forum de discussion intégré à Wagtail : catégories, sections, sujets, messages, modération, messages privés, notifications, recherche et outils d’import d’une ancienne application de forum.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Fonctionnalités principales

- Hiérarchie catégorie → section → sujet → message avec compteurs d’activité.
- Boîte de réception privée et conversations en fil.
- Antispam pour invités, modération, recherche et limitation du débit.
- Outils d’import et de redirection d’un ancien forum ; validez le mode dry-run avant la bascule.

## Prérequis et compatibilité

- Dépendances déclarées: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- La compatibilité de Python, Django et Wagtail doit être vérifiée conjointement. La dépendance minimale du paquet ne confirme pas que toutes les versions sont prises en charge.

Les métadonnées déclarent Wagtail >= 6.0, mais une dépendance minimale ne prouve pas la compatibilité. Cette archive ne contient pas de matrice automatisée complète pour toutes les combinaisons Django/Wagtail. Avant une mise à jour en production, testez les versions exactes, la base de données, le stockage et la configuration de déploiement en préproduction.

## Installation

Installez le paquet dans le même environnement virtuel que votre projet Wagtail :

```bash
pip install wagtail-simple-forum
```

Ajoutez les applications dans cet ordre en conservant les autres dépendances du projet :

```python
INSTALLED_APPS = [
    # Conservez également les autres dépendances Django/Wagtail déjà requises.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Incluez les URL du forum **avant la route catch-all de Wagtail**. Les redirections historiques doivent également la précéder.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Les routes héritées doivent précéder la route catch-all de Wagtail.
]
```

Exécutez `python manage.py migrate wagtail_simple_forum`.


## Configuration initiale

Exemple minimal pour démarrer. Adaptez les noms de modèles, les champs API et les URL à votre configuration.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Les routes héritées doivent précéder la route catch-all de Wagtail.
]
```

Exécutez `python manage.py migrate wagtail_simple_forum`. Pour une ancienne application `forum`, lancez d’abord `python manage.py forum_import_from_app --source forum --dry-run`.

Avant l’import de l’ancien forum, sauvegardez la base et lancez `--dry-run`. Gardez l’ancienne application installée jusqu’à la fin de l’import et des contrôles.


## Paramètres et comportement importants

Le README anglais de ce répertoire est la référence canonique et contient les tableaux complets des options et les exemples détaillés. Cette traduction couvre la mise en place pratique et les avertissements de sécurité essentiels ; consultez la référence anglaise avant de modifier les options avancées.

Consultez le [README en anglais](README.md) pour la référence complète des paramètres.

### Points importants

Les URL du forum et les redirections historiques doivent précéder la route catch-all de Wagtail. Avant d’importer l’ancien forum, sauvegardez la base et lancez d’abord `--dry-run`.

## Sécurité et exploitation

- Maintenez les dépendances à jour. Pour le HTML utilisateur, utilisez le chemin prévu de nettoyage et de rendu ; n’affichez pas les commentaires ou messages stockés avec un `|safe` inconditionnel.
- Vérifiez migrations et autorisations avec des utilisateurs normaux, restreints, modérateurs et administrateurs.
- En environnement multisite, testez chaque domaine configuré ainsi qu’un hôte inconnu. Si aucun Site n’est trouvé, une requête ne doit jamais s’élargir à tous les sites.
- Traitez les jetons API, identifiants SMTP et URL privées comme des secrets. Ne les committez pas dans Git et ne les publiez pas dans les rapports de bug.
- Sauvegardez la base de données et les fichiers médias avant les migrations, déplacements en masse, imports ou première publication en masse. Testez d’abord en préproduction.

## Combinaisons recommandées

- `wagtail-mptt-comments` complète le forum avec les commentaires d’articles ; le sélecteur Prose n’est utile que pour des champs personnalisés.
- Les répertoires d’images sont indépendants des données du forum.

## Liste de vérification

- [ ] Installez la version candidate en préproduction et notez les versions de Python, Django, Wagtail et de la base de données.
- [ ] Exécutez `python manage.py check` et les migrations du paquet.
- [ ] Testez le flux principal avec un utilisateur normal et un utilisateur restreint.
- [ ] Vérifiez journaux, accès, cache, sauvegardes et restauration.

L’archive passe les contrôles statiques de syntaxe et de packaging, mais l’intégration Django/Wagtail complète n’a pas été exécutée dans cet environnement. Considérez la liste ci-dessous comme une condition de publication, et non comme la preuve que toutes les combinaisons sont testées.

## Dépannage

Si le flux ne fonctionne pas, vérifiez la configuration de l’application, les migrations, l’ordre des URL, les autorisations et les journaux Django. Comparez la version et l’exemple avec le README anglais.

## Licence et assistance

MIT. Code source: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

