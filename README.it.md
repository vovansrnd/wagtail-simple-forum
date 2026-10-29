# wagtail-simple-forum

**Aggiunge un forum integrato con Wagtail: categorie, sezioni, argomenti, post, moderazione, messaggi privati, notifiche, ricerca e strumenti per importare una vecchia app forum.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Funzionalità principali

- Gerarchia categoria → sezione → argomento → post con contatori di attività.
- Caselle di messaggi privati e conversazioni in thread.
- Antispam per ospiti, moderazione, ricerca e limiti di frequenza.
- Strumenti di importazione e redirect per forum legacy; validare il dry-run prima del passaggio.

## Requisiti e compatibilità

- Dipendenze dichiarate: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- La compatibilità di Python, Django e Wagtail va verificata congiuntamente. La dipendenza minima del pacchetto non conferma il supporto di tutte le versioni.

I metadati dichiarano Wagtail >= 6.0, ma una dipendenza minima non dimostra la compatibilità. Questo archivio non contiene una matrice automatizzata completa per tutte le combinazioni Django/Wagtail. Prima di aggiornare la produzione, verifica in staging le versioni effettive, il database, lo storage e le impostazioni di deployment.

## Installazione

Installa il pacchetto nello stesso ambiente virtuale del progetto Wagtail:

```bash
pip install wagtail-simple-forum
```

Aggiungi le app nell’ordine indicato mantenendo le altre dipendenze del progetto:

```python
INSTALLED_APPS = [
    # Mantieni anche le altre dipendenze Django/Wagtail già necessarie.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Includere gli URL del forum **prima della route catch-all di Wagtail**. Anche i reindirizzamenti legacy devono precederla.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Le route legacy devono precedere la route catch-all di Wagtail.
]
```

Eseguire `python manage.py migrate wagtail_simple_forum`.


## Configurazione iniziale

Esempio minimo per iniziare. Adatta nomi dei modelli, campi API e URL alla tua configurazione.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Le route legacy devono precedere la route catch-all di Wagtail.
]
```

Eseguire `python manage.py migrate wagtail_simple_forum`. Per una vecchia app `forum`, eseguire prima `python manage.py forum_import_from_app --source forum --dry-run`.

Prima di importare il vecchio forum, fare un backup ed eseguire `--dry-run`. Mantenere installata la vecchia app fino al completamento dell’importazione e dei controlli.


## Impostazioni e comportamento importanti

Il README inglese in questa directory è il riferimento canonico e contiene le tabelle complete delle opzioni e gli esempi estesi. Questa traduzione copre la configurazione pratica e gli avvisi di sicurezza essenziali; consulta il riferimento inglese prima di modificare le opzioni avanzate.

Consulta il [README inglese](README.md) per la tabella completa delle impostazioni.

### Note importanti

Gli URL del forum e i redirect legacy devono precedere la catch-all di Wagtail. Prima di importare il vecchio forum, esegui un backup e avvia prima `--dry-run`.

## Sicurezza e operatività

- Mantieni aggiornate le dipendenze. Per l’HTML degli utenti usa il percorso previsto di sanificazione e rendering; non mostrare commenti o post salvati con `|safe` incondizionato.
- Verifica migrazioni e permessi con utenti normali, limitati, moderatori e amministratori.
- Nei progetti multi-sito, verifica ogni dominio configurato e un host sconosciuto. Se non viene trovato un Site, la query non deve estendersi ai record di tutti i siti.
- Tratta token API, credenziali SMTP e URL privati come segreti. Non inserirli in Git né in segnalazioni pubbliche.
- Esegui il backup del database e dei file multimediali prima di migrazioni, spostamenti in blocco, importazioni o pubblicazioni massive iniziali. Prova prima in staging.

## Combinazioni consigliate

- `wagtail-mptt-comments` completa il forum con commenti agli articoli; il selettore Prose serve solo per campi personalizzati.
- Le directory immagini sono indipendenti dai dati del forum.

## Lista di verifica

- [ ] Installa la versione candidata in staging e annota le versioni di Python, Django, Wagtail e database.
- [ ] Esegui `python manage.py check` e le migrazioni del pacchetto.
- [ ] Prova il flusso principale con un utente normale e uno limitato.
- [ ] Controlla log, accessi, cache, backup e ripristino.

L’archivio supera i controlli statici di sintassi e packaging, ma in questo ambiente non è stato eseguito un test completo d’integrazione Django/Wagtail. Considera la lista seguente un requisito per il rilascio, non la prova che ogni combinazione sia stata testata.

## Risoluzione dei problemi

Se il flusso non funziona, controlla configurazione dell’app, migrazioni, ordine URL, permessi e log Django. Confronta versione ed esempio con il README inglese.

## Licenza e supporto

MIT. Codice sorgente: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

