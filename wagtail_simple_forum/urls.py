# forum/urls.py

from django.urls import path, register_converter

from . import views

app_name = "wagtail_simple_forum"


class UnicodeSlugConverter:
    regex = r"[-\w]+"

    def to_python(self, value):
        return value

    def to_url(self, value):
        return value


register_converter(UnicodeSlugConverter, "uslug")

urlpatterns = [
    # Forum main and topics
    path("", views.forum_index, name="forum_index"),
    path("section/<uslug:slug>/", views.section_view, name="section_view"),
    path("section/<uslug:slug>/new/", views.topic_create, name="topic_create"),
    path("topic/<uslug:slug>/", views.topic_view, name="topic_view"),
    path("topic/<uslug:slug>/toggle-close/", views.topic_close, name="topic_close"),
    path("topic/<uslug:slug>/toggle-pin/", views.topic_pin, name="topic_pin"),
    # Post management
    path("post/<int:pk>/edit/", views.post_edit, name="post_edit"),
    path("post/<int:pk>/delete/", views.post_delete, name="post_delete"),
    path("search/", views.forum_search, name="forum_search"),
    # Private Messages
    path("messages/", views.pm_inbox, name="pm_inbox"),
    path("messages/new/", views.pm_new, name="pm_new"),
    path("messages/new/<str:username>/", views.pm_new, name="pm_new_to"),
    path("messages/thread/<int:pk>/", views.pm_thread, name="pm_thread"),
]
