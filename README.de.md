# wagtail-simple-forum

**Ergänzt ein in Wagtail integriertes Diskussionsforum mit Kategorien, Bereichen, Themen, Beiträgen, Moderation, privaten Nachrichten, Benachrichtigungen, Suche und Importwerkzeugen für eine alte Forum-App.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Wichtigste Funktionen

- Hierarchie Kategorie → Bereich → Thema → Beitrag mit Aktivitätszählern.
- Private Nachrichten mit Posteingang und Gesprächsverläufen.
- Anti-Spam für Gäste, Moderation, Suche und Ratenbegrenzung.
- Import- und Redirect-Helfer für alte Foren; Dry-Run vor dem Umschalten validieren.

## Voraussetzungen und Kompatibilität

- Deklarierte Abhängigkeiten: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Die Kompatibilität von Python, Django und Wagtail muss gemeinsam geprüft werden. Die minimale Paketabhängigkeit bestätigt keine Unterstützung jeder Version.

Die Paketmetadaten deklarieren Wagtail >= 6.0. Eine minimale Abhängigkeit ist jedoch kein Kompatibilitätstest. Dieses Quellarchiv enthält keine vollständige automatisierte Matrix für alle Django-/Wagtail-Kombinationen. Prüfen Sie vor einem Produktionsupgrade die konkreten Versionen, Datenbank, Speicher-Backend und Deployment-Einstellungen in einer Staging-Umgebung.

## Installation

Installieren Sie das Paket in derselben virtuellen Umgebung wie Ihr Wagtail-Projekt:

```bash
pip install wagtail-simple-forum
```

Fügen Sie die Apps in der angegebenen Reihenfolge hinzu und behalten Sie die übrigen Projektabhängigkeiten bei:

```python
INSTALLED_APPS = [
    # Behalten Sie auch andere bereits benötigte Django-/Wagtail-Abhängigkeiten bei.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Binden Sie die Forum-URLs **vor Wagtails Catch-all-Route** ein. Auch Legacy-Weiterleitungen müssen davor stehen.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Legacy-Routen müssen vor der Wagtail-Catch-all-Route stehen.
]
```

Führen Sie `python manage.py migrate wagtail_simple_forum` aus.


## Erste Konfiguration

Minimales Einstiegsbeispiel. Passen Sie Modellnamen, API-Felder und URLs an Ihre Konfiguration an.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Legacy-Routen müssen vor der Wagtail-Catch-all-Route stehen.
]
```

Führen Sie `python manage.py migrate wagtail_simple_forum` aus. Bei einer alten `forum`-App zuerst `python manage.py forum_import_from_app --source forum --dry-run` ausführen.

Sichern Sie vor dem Import die Datenbank und führen Sie `--dry-run` aus. Lassen Sie die alte App installiert, bis Import und Prüfungen abgeschlossen sind.


## Wichtige Einstellungen und Verhalten

Die englische README in diesem Verzeichnis ist die maßgebliche Referenz und enthält vollständige Einstellungstabellen und ausführliche Beispiele. Diese Übersetzung erklärt die praktische Einrichtung und die wichtigsten Sicherheitshinweise; konsultieren Sie vor Änderungen an erweiterten Einstellungen die englische Referenz.

Die vollständige Einstellungsreferenz finden Sie in der [englischen README](README.md).

### Wichtige Hinweise

Forum-URLs und Legacy-Weiterleitungen müssen vor der Wagtail-Catch-all-Route stehen. Sichern Sie vor dem Import eines alten Forums die Datenbank und führen Sie zuerst `--dry-run` aus.

## Sicherheit und Betrieb

- Halten Sie Abhängigkeiten aktuell. Verwenden Sie für nutzererstelltes HTML den vorgesehenen Bereinigungs- und Ausgabepfad; geben Sie gespeicherte Kommentare oder Forenbeiträge nicht bedingungslos mit `|safe` aus.
- Prüfen Sie Migrationen und Berechtigungen mit normalen, eingeschränkten Benutzern, Moderatoren und Administratoren.
- Testen Sie bei mehreren Wagtail-Sites jede konfigurierte Domain sowie einen unbekannten Host. Wenn keine Site gefunden wird, darf eine Abfrage nicht auf Datensätze aller Sites erweitert werden.
- Behandeln Sie API-Tokens, SMTP-Zugangsdaten und private URLs als Geheimnisse. Committen Sie diese nicht in Git und veröffentlichen Sie sie nicht in Fehlerberichten.
- Sichern Sie Datenbank und Mediendateien vor Migrationen, Massenverschiebungen, Importen oder der ersten Massenveröffentlichung. Testen Sie diese Vorgänge zuerst in Staging.

## Empfohlene Kombinationen

- `wagtail-mptt-comments` ergänzt das Forum um Artikelkommentare; `wagtail-prose-editor-images` ist nur bei eigenen Prose-Feldern nötig.
- Bildverzeichnisse sind unabhängig von Forendaten.

## Checkliste zur Überprüfung

- [ ] Installieren Sie den Kandidaten in Staging und notieren Sie Python-, Django-, Wagtail- und Datenbankversionen.
- [ ] Führen Sie `python manage.py check` und die Paketmigrationen aus.
- [ ] Prüfen Sie den Hauptablauf mit einem normalen und einem eingeschränkten Benutzer.
- [ ] Prüfen Sie Logs, Zugriffskontrolle, Caching, Backups und Wiederherstellung.

Das Archiv besteht statische Syntax- und Packaging-Prüfungen; die vollständige Django-/Wagtail-Laufzeitintegration wurde in dieser Umgebung jedoch nicht getestet. Betrachten Sie die folgende Checkliste als Freigabekriterium und nicht als Behauptung, dass jede Versionskombination getestet wurde.

## Fehlerbehebung

Wenn der Ablauf nicht funktioniert, prüfen Sie App-Konfiguration, Migrationen, URL-Reihenfolge, Benutzerrechte und Django-Logs. Vergleichen Sie Paketversion und Beispiel mit der englischen README.

## Lizenz und Support

MIT. Quellcode: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

