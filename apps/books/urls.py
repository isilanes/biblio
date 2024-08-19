from django.urls import path

from . import views


app_name = "books"


urlpatterns = [
    # Main:
    path('', views.stats, name="stats"),

    # Misc:
    path('index', views.index, name="index"),
    path('sagas', views.sagas, name="sagas"),
    path('stats/<int:year>', views.stats, name="stats"),

    # Details:
    path('book/<int:book_id>', views.book_detail, name='book_detail'),
    path('author/<int:author_id>', views.author_detail, name='author_detail'),

    # Forms:
    path('add_book', views.add_book, name='add_book'),
    path('modify_book/<int:book_id>', views.modify_book, name='modify_book'),
    path('add_edition/<int:book_id>', views.add_edition, name='add_edition'),
    path('modify_edition/<int:edition_id>', views.modify_edition, name='modify_edition'),
    path('find_book', views.find_book, name='find_book'),
    path('update_reading/<int:reading_id>', views.update_reading, name='update_reading'),
    path(
        'update_book_reading/<int:book_id>',
        views.update_book_reading,
        name='update_book_reading',
    ),
    path(
        'mark_reading_done/<int:reading_id>',
        views.mark_reading_done,
        name='mark_reading_done',
    ),
    path(
        'mark_reading_dnf/<int:reading_id>',
        views.mark_reading_dnf,
        name='mark_reading_dnf',
    ),
    path(
        'mark_edition_owned/<int:edition_id>',
        views.mark_edition_owned,
        name='mark_edition_owned',
    ),
    path('mark_reading_started/<int:edition_id>',
         views.mark_reading_started,
         name='mark_reading_started'),

    # REST endpoints: TODO: use DRF
    path(
        'mark_reading_pages/<int:reading_id>',
        views.mark_reading_pages,
        name='mark_reading_pages',
    ),
    path(
        'mark_reading_finished/<int:reading_id>',
        views.mark_reading_finished,
        name='mark_reading_finished',
    ),
    path(
        'mark_reading_dnf_rest/<int:reading_id>',
        views.mark_reading_dnf_rest,
        name='mark_reading_dnf_rest',
    ),
]
