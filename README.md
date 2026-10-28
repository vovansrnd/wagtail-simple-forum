# wagtail-simple-forum

Лёгкий форум для Wagtail с приватными сообщениями, антиспамом и модерацией
через стандартную админку Wagtail. Без зависимостей от сторонних форумных
движков — только Wagtail, django-prose-editor и nh3.

## Возможности

- Категории → разделы → темы → сообщения (денормализованные счётчики, O(1) на ответ)
- Личные сообщения с пагинацией и уведомлениями
- Гости: имена/emails, модерация, математическая капча (stateless, HMAC-подпись),
  honeypot, подписанный токен времени отправки
- Rate limiting (cache-based): создание тем, ответы, поиск, ЛС
- Счётчик просмотров с дедупликацией по хешу IP (1 час)
- Модерация: закрепление/закрытие тем, одобрение, мягкое удаление сообщений,
  группы модераторов (`FORUM_MODERATOR_GROUPS`)
- Импорт legacy-данных: `legacy_id` у всех моделей + редиректы `viewtopic.php` /
  `viewforum.php` + модель `ForumLegacyUserMap` (отображаемые имена и роли
  пользователей старого форума)
- Тонкая настройка темы: шаблон `base_forum.html` перекрывается в проекте
  (например, `vsproject/templates/wagtail_simple_forum/base_forum.html`)
- i18n (русская локаль в комплекте), URL-ы с юникодными слагами

## Установка

```bash
pip install wagtail-simple-forum
```

```python
INSTALLED_APPS = [
    ...,
    "wagtail_simple_forum",
]

urlpatterns = [
    ...,
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_urls,  # from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_urls
]
```

Миграции моделей изображения/рендеров не требуются: форум использует
стандартную модель пользователя и собственные таблицы.

## Настройки

| Настройка | По умолчанию | Описание |
|---|---|---|
| `FORUM_ALLOWED_HOSTS` | `None` (все) | Список хостов, на которых форум доступен (остальные получают 404) |
| `FORUM_ALLOW_GUESTS` | `True` | Разрешить гостевые темы/ответы |
| `FORUM_MODERATE_GUESTS` | `True` | Отправлять гостевые сообщения на модерацию |
| `FORUM_STAFF_ARE_MODERATORS` | `True` | `is_staff` даёт права модератора |
| `FORUM_MODERATOR_GROUPS` | `None` | Список названий групп Django — модераторы форума |
| `FORUM_AVATAR_URL_GETTER` | `None` | import-строка функции `get_avatar_url(user) -> str` |
| `FORUM_TRUST_PROXY_HEADERS` | `False` | Брать клиентский IP из `X-Forwarded-For` (включайте только за прокси, который его перезаписывает) |
| `FORUM_TRACK_VIEWS` | `True` | Счётчик просмотров тем |
| `FORUM_TOPIC_POSTS_PER_PAGE` / `FORUM_SECTION_TOPICS_PER_PAGE` / `FORUM_SEARCH_RESULTS_PER_PAGE` | `20` / `30` / `20` | Пагинация |
| `FORUM_MAX_POST_LENGTH` / `FORUM_MAX_PM_LENGTH` | `65535` / `20000` | Лимиты длины сообщений |
| `FORUM_NOTIFY_ADMINS` / `FORUM_NOTIFY_TOPIC_AUTHOR` / `FORUM_NOTIFY_PM_RECIPIENT` | `True` | Email-уведомления |
| `FORUM_LEGACY_REDIRECT_PERMANENT` | `True` | 301 вместо 302 для legacy-редиректов |

## Переезд со старого приложения `forum` (вырезание из монолита)

Оба приложения могут стоять одновременно, поэтому переезд безопасен:

1. Установите плагин и добавьте в `INSTALLED_APPS` **оба** приложения:
   `"wagtail_simple_forum"` и старый `"forum"`.
2. `python manage.py migrate wagtail_simple_forum` — создадутся таблицы плагина.
3. `python manage.py forum_import_from_app --source forum --dry-run` —
   посмотреть, что скопируется. Команда идемпотентна (сопоставление по
   `legacy_id`), копирует категории, разделы, темы, сообщения, ЛС и
   legacy-связки пользователей.
4. `python manage.py forum_import_from_app --source forum` — выполнить копирование.
5. Переключите URL-ы на плагин (см. «Установка»), добавьте оверрайд
   `base_forum.html` под вашу тему.
6. Проверьте форум на домене из `FORUM_ALLOWED_HOSTS`.
7. Удалите `"forum"` из `INSTALLED_APPS` и каталог старого приложения.
   При необходимости пересчитайте статистику:
   `python manage.py forum_recalculate_stats`.

## Управление

Всё в админке Wagtail, группа «Форум»: категории, разделы, темы, сообщения,
legacy-пользователи. Статистика (счётчики, даты последних сообщений)
пересчитывается автоматически при модерации.

## Лицензия

MIT
