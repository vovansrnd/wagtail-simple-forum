# wagtail-simple-forum

**Añade un foro integrado con Wagtail: categorías, secciones, temas, publicaciones, moderación, mensajes privados, notificaciones, búsqueda y herramientas para importar una aplicación de foro anterior.**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## Funciones principales

- Jerarquía categoría → sección → tema → publicación con contadores de actividad.
- Bandeja de mensajes privados y conversaciones encadenadas.
- Antispam para invitados, moderación, búsqueda y límites de frecuencia.
- Importación y redirecciones del foro anterior; valida la ejecución de prueba antes del cambio.

## Requisitos y compatibilidad

- Dependencias declaradas: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- La compatibilidad de Python, Django y Wagtail debe verificarse en conjunto. La dependencia mínima del paquete no confirma que todas las versiones estén soportadas.

Los metadatos declaran Wagtail >= 6.0, pero una dependencia mínima no demuestra compatibilidad. Este archivo no incluye una matriz automatizada completa para todas las combinaciones de Django/Wagtail. Antes de actualizar producción, prueba las versiones exactas, la base de datos, el almacenamiento y la configuración de despliegue en un entorno de pruebas.

## Instalación

Instala el paquete en el mismo entorno virtual que tu proyecto Wagtail:

```bash
pip install wagtail-simple-forum
```

Añade las aplicaciones en el orden indicado y conserva las demás dependencias del proyecto:

```python
INSTALLED_APPS = [
    # Conserva también las demás dependencias Django/Wagtail que necesita el proyecto.
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

Incluya las URL del foro **antes de la ruta catch-all de Wagtail**. Las redirecciones heredadas también deben ir antes.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # Las rutas heredadas deben ir antes de la ruta catch-all de Wagtail.
]
```

Ejecute `python manage.py migrate wagtail_simple_forum`.


## Configuración inicial

Ejemplo mínimo para empezar. Adapta los nombres de modelos, campos API y URL a tu configuración.

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # Las rutas heredadas deben ir antes de la ruta catch-all de Wagtail.
]
```

Ejecute `python manage.py migrate wagtail_simple_forum`. Para una antigua app `forum`, ejecute primero `python manage.py forum_import_from_app --source forum --dry-run`.

Antes de importar el foro antiguo, haga una copia de seguridad y ejecute `--dry-run`. Mantenga instalada la app antigua hasta terminar el import y las comprobaciones.


## Ajustes y comportamiento importantes

El README en inglés de este directorio es la referencia canónica y contiene las tablas completas de opciones y ejemplos ampliados. Esta traducción cubre la configuración práctica y las advertencias de seguridad esenciales; consulta la referencia inglesa antes de cambiar opciones avanzadas.

Consulta la [versión inglesa del README](README.md) para ver la referencia completa de ajustes.

### Notas importantes

Las URL del foro y las redirecciones antiguas deben ir antes de la ruta catch-all de Wagtail. Antes de importar el foro anterior, haz una copia de seguridad y ejecuta primero `--dry-run`.

## Seguridad y operación

- Mantén las dependencias actualizadas. Para HTML escrito por usuarios, utiliza la limpieza y representación previstas; no muestres comentarios o publicaciones almacenadas con `|safe` incondicional.
- Comprueba migraciones y permisos con usuarios normales, restringidos, moderadores y administradores.
- En instalaciones multisitio, prueba cada dominio configurado y un host desconocido. Si no se encuentra un Site, la consulta nunca debe ampliarse a todos los sitios.
- Trata los tokens de API, las credenciales SMTP y las URL privadas como secretos. No los guardes en Git ni los incluyas en informes públicos.
- Haz copias de seguridad de la base de datos y de los medios antes de migraciones, movimientos masivos, importaciones o la primera publicación masiva. Prueba primero en staging.

## Combinaciones recomendadas

- `wagtail-mptt-comments` complementa el foro con comentarios en artículos; el selector Prose solo hace falta para campos propios.
- Los directorios de imágenes son independientes de los datos del foro.

## Lista de verificación

- [ ] Instala la versión candidata en staging y anota las versiones de Python, Django, Wagtail y la base de datos.
- [ ] Ejecuta `python manage.py check` y las migraciones del paquete.
- [ ] Prueba el flujo principal con un usuario normal y otro restringido.
- [ ] Revisa registros, acceso, caché, copias de seguridad y recuperación.

El archivo supera comprobaciones estáticas de sintaxis y empaquetado, pero no se ha ejecutado aquí una prueba completa de integración Django/Wagtail. Trata la lista siguiente como un requisito previo a la publicación, no como una afirmación de que se han probado todas las combinaciones.

## Solución de problemas

Si el flujo no funciona, revisa la configuración de la app, las migraciones, el orden de URL, los permisos y los registros de Django. Compara la versión y el ejemplo con el README inglés.

## Licencia y soporte

MIT. Código fuente: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

