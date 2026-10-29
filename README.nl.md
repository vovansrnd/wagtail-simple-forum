# wagtail-simple-forum

**Voegt een met Wagtail geïntegreerd discussieforum toe met categorieën, secties, onderwerpen, berichten, moderatie, privéberichten, meldingen, zoeken en hulpmiddelen voor import uit een oude forum-app.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Belangrijkste functies

- Hiërarchie categorie → sectie → onderwerp → bericht met activiteits­tellers.
- Inbox voor privéberichten en gesprekken in threads.
- Anti-spam voor gasten, moderatie, zoeken en rate limiting.
- Import- en redirecthulpmiddelen voor een oud forum; controleer de dry-run vóór de omschakeling.

## Vereisten en compatibiliteit

- Gedeclareerde afhankelijkheden: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Controleer de compatibiliteit van Python, Django en Wagtail gezamenlijk. De minimale pakketafhankelijkheid bewijst niet dat alle versies worden ondersteund.

De pakketmetadata vermeldt Wagtail >= 6.0, maar een minimale afhankelijkheid bewijst geen compatibiliteit. Dit archief bevat geen volledige geautomatiseerde matrix voor alle Django/Wagtail-combinaties. Test vóór een productie-upgrade de exacte versies, database, opslagbackend en deploymentinstellingen in staging.

## Installatie

Installeer het pakket in dezelfde virtuele omgeving als je Wagtail-project:

```bash
pip install wagtail-simple-forum
```

Voeg de apps in deze volgorde toe en behoud de overige projectafhankelijkheden:

```python
INSTALLED_APPS = [
    # Behoud ook de overige Django/Wagtail-afhankelijkheden die het project nodig heeft.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Neem forum-URL’s **op vóór de Wagtail-catch-all-route**. Ook oude omleidingen moeten daarvoor staan.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Legacy-routes moeten vóór de catch-all-route van Wagtail staan.
]
```

Voer `python manage.py migrate wagtail_simple_forum` uit.


## Eerste configuratie

Minimaal startvoorbeeld. Pas modelnamen, API-velden en URL’s aan je configuratie aan.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Legacy-routes moeten vóór de catch-all-route van Wagtail staan.
]
```

Voer `python manage.py migrate wagtail_simple_forum` uit. Gebruik bij een oude `forum`-app eerst `python manage.py forum_import_from_app --source forum --dry-run`.

Maak vóór de import van het oude forum een back-up en voer `--dry-run` uit. Houd de oude app geïnstalleerd totdat de import en controles zijn afgerond.


## Belangrijke instellingen en gedrag

De Engelse README in deze map is de canonieke referentie met volledige instellingstabellen en uitgebreide voorbeelden. Deze vertaling behandelt de praktische installatie en de belangrijkste veiligheidswaarschuwingen; raadpleeg de Engelse referentie voordat je geavanceerde instellingen wijzigt.

Raadpleeg de [Engelse README](README.md) voor het volledige instellingenoverzicht.

### Belangrijke aandachtspunten

Forum-URL’s en oude redirects moeten vóór de Wagtail-catch-all-route staan. Maak vóór import van het oude forum een back-up en voer eerst `--dry-run` uit.

## Beveiliging en beheer

- Houd afhankelijkheden bijgewerkt. Gebruik voor door gebruikers geschreven HTML het bedoelde opschonings- en renderpad; geef opgeslagen reacties of forumberichten niet onvoorwaardelijk weer met `|safe`.
- Controleer migraties en rechten met gewone, beperkte gebruikers, moderators en beheerders.
- Test bij meerdere sites elk ingesteld domein en een onbekende host. Als geen Site wordt gevonden, mag een query niet worden verbreed naar records van alle sites.
- Behandel API-tokens, SMTP-inloggegevens en privé-URL’s als geheimen. Commit ze niet naar Git en vermeld ze niet in openbare bugrapporten.
- Maak een back-up van database en mediabestanden vóór migraties, bulkverplaatsingen, imports of de eerste bulkpublicatie. Test zulke handelingen eerst in staging.

## Aanbevolen combinaties

- `wagtail-mptt-comments` vult het forum aan met artikelreacties; de Prose-kiezer is alleen nodig voor eigen velden.
- Afbeeldingsmappen staan los van forumgegevens.

## Controlelijst

- [ ] Installeer de kandidaat in staging en noteer de Python-, Django-, Wagtail- en databaseversies.
- [ ] Voer `python manage.py check` en de pakketmigraties uit.
- [ ] Test de hoofdworkflow met een gewone en beperkte gebruiker.
- [ ] Controleer logs, toegang, caching, back-ups en herstel.

Het archief slaagt voor statische syntax- en packagingcontroles, maar volledige Django/Wagtail-runtime-integratie is hier niet uitgevoerd. Beschouw de lijst hieronder als vrijgavevoorwaarde, niet als bewijs dat elke combinatie is getest.

## Probleemoplossing

Als de workflow niet werkt, controleer appconfiguratie, migraties, URL-volgorde, gebruikersrechten en Django-logs. Vergelijk pakketversie en voorbeeld met de Engelse README.

## Licentie en ondersteuning

MIT. Broncode: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

