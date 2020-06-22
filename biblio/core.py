# Standard libs:
import os


# Constants:
LINKS = {
    os.path.join("DjangoProgress", "templates", "main_index.html"): {
        "free": "main_index_free.html",
        "nonfree": "main_index_nonfree.html",
    },
    os.path.join("gasolina", "static"): {
        "free": "static-free",
        "nonfree": "static-nonfree",
    },
    os.path.join("books", "static"): {
        "free": "static-free",
        "nonfree": "static-nonfree",
    },
    os.path.join("ahorro", "static"): {
        "free": "static-free",
        "nonfree": "static-nonfree",
    },
}


# Functions:
def please_delete(file_name):
    try:
        os.unlink(file_name)
    except FileNotFoundError:
        pass


def mk_links(free):
    """Generate the links to free/non-free versions of items."""

    k = "nonfree"
    if free:
        k = "free"

    for link, link_d in LINKS.items():
        dest = link_d[k]
        please_delete(link)
        os.symlink(dest, link)


