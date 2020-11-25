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
    path('start_book', views.start_book, name='start_book'),
    path('update_book_progress/<int:book_id>',
         views.update_book_progress,
         name='update_book_progress'),
    path('mark_book_read/<int:book_id>', views.mark_book_read, name='mark_book_read'),
    path('mark_book_owned/<int:book_id>', views.mark_book_owned, name='mark_book_owned'),
]
