# wagtail-simple-forum

**Dodaje forum dyskusyjne zintegrowane z Wagtail: kategorie, sekcje, tematy, wpisy, moderację, wiadomości prywatne, powiadomienia, wyszukiwanie i narzędzia importu ze starej aplikacji forum.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Najważniejsze funkcje

- Hierarchia kategoria → sekcja → temat → wpis z licznikami aktywności.
- Skrzynka wiadomości prywatnych i rozmowy w wątkach.
- Antyspam dla gości, moderacja, wyszukiwanie i ograniczanie częstotliwości.
- Import i przekierowania ze starego forum; sprawdź dry-run przed przełączeniem ruchu.

## Wymagania i zgodność

- Zadeklarowane zależności: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Zgodność Pythona, Django i Wagtail należy sprawdzać łącznie. Minimalna zależność pakietu nie potwierdza obsługi każdej wersji.

Metadane deklarują Wagtail >= 6.0, ale minimalna zależność nie dowodzi zgodności. Archiwum nie zawiera pełnej automatycznej macierzy wszystkich kombinacji Django/Wagtail. Przed aktualizacją produkcji sprawdź dokładne wersje, bazę danych, backend plików i konfigurację wdrożenia na środowisku testowym.

## Instalacja

Zainstaluj pakiet w tym samym środowisku wirtualnym co projekt Wagtail:

```bash
pip install wagtail-simple-forum
```

Dodaj aplikacje w tej kolejności, zachowując pozostałe zależności projektu:

```python
INSTALLED_APPS = [
    # Zachowaj również inne zależności Django/Wagtail wymagane przez projekt.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Dołącz adresy forum **przed trasą catch-all Wagtail**. Przekierowania legacy również muszą znajdować się wcześniej.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Trasy legacy muszą występować przed trasą catch-all Wagtail.
]
```

Uruchom `python manage.py migrate wagtail_simple_forum`.


## Pierwsza konfiguracja

Minimalny przykład na początek. Dostosuj nazwy modeli, pola API i adresy URL do swojej konfiguracji.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Trasy legacy muszą występować przed trasą catch-all Wagtail.
]
```

Uruchom `python manage.py migrate wagtail_simple_forum`. Dla starej aplikacji `forum` najpierw uruchom `python manage.py forum_import_from_app --source forum --dry-run`.

Przed importem starego forum wykonaj kopię bazy i uruchom `--dry-run`. Pozostaw starą aplikację do zakończenia importu i kontroli.


## Ważne ustawienia i zachowanie

Angielski README w tym katalogu jest kanoniczną dokumentacją i zawiera pełne tabele opcji oraz rozszerzone przykłady. To tłumaczenie opisuje praktyczną konfigurację i najważniejsze ostrzeżenia bezpieczeństwa; przed zmianą zaawansowanych opcji sprawdź dokumentację angielską.

Pełną tabelę ustawień znajdziesz w [angielskim README](README.md).

### Ważne uwagi

URL-e forum i stare przekierowania muszą być przed trasą catch-all Wagtail. Przed importem starego forum wykonaj kopię bazy i najpierw uruchom `--dry-run`.

## Bezpieczeństwo i eksploatacja

- Aktualizuj zależności. Dla HTML użytkowników stosuj przewidziany mechanizm oczyszczania i renderowania; nie wyświetlaj zapisanych komentarzy ani postów bezwarunkowo przez `|safe`.
- Sprawdź migracje i uprawnienia jako zwykły, ograniczony użytkownik, moderator i administrator.
- W instalacji wieloserwisowej przetestuj każdą skonfigurowaną domenę i nieznany host. Brak Site nie może rozszerzać zapytania na rekordy wszystkich witryn.
- Traktuj tokeny API, dane SMTP i prywatne adresy URL jako sekrety. Nie dodawaj ich do Git ani do publicznych zgłoszeń.
- Wykonaj kopię zapasową bazy i plików multimedialnych przed migracjami, masowym przenoszeniem, importem lub pierwszą masową publikacją. Najpierw przetestuj te operacje na stagingu.

## Zalecane połączenia

- `wagtail-mptt-comments` uzupełnia forum o komentarze artykułów; selektor Prose jest potrzebny tylko w polach własnych.
- Katalogi obrazów są niezależne od danych forum.

## Lista kontrolna

- [ ] Zainstaluj wersję kandydującą na stagingu i zapisz wersje Pythona, Django, Wagtail oraz bazy.
- [ ] Uruchom `python manage.py check` i migracje pakietu.
- [ ] Przetestuj główny przepływ jako zwykły i ograniczony użytkownik.
- [ ] Sprawdź logi, dostęp, cache, kopie zapasowe i odtwarzanie.

Archiwum przechodzi statyczne kontrole składni i pakowania, ale w tym środowisku nie wykonano pełnych testów integracyjnych Django/Wagtail. Poniższą listę traktuj jako warunek wydania, a nie potwierdzenie przetestowania każdej kombinacji.

## Rozwiązywanie problemów

Jeśli przepływ nie działa, sprawdź konfigurację aplikacji, migracje, kolejność URL, uprawnienia i logi Django. Porównaj wersję pakietu i przykład z angielskim README.

## Licencja i pomoc

MIT. Kod źródłowy: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

